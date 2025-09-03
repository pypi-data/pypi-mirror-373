import logging
import os
import json

from django.core.exceptions import PermissionDenied
from django.utils.functional import wraps
from django.utils.translation import gettext_lazy as _

from .shared import get_path, application_type_service
from ..utils import config, is_empty


def group_required():
    """
      Decorator to make a view only accept particular groups:
    """
    def decorator(func):
        @wraps(func)
        def inner(view, *args, **kwargs):

            request = view.request
            token_info = request.auth

            # shortcircuit
            if os.getenv("ENV") == 'test':
               return func(view, *args, **kwargs)

            logger = logging.getLogger('oauth2')

            path = get_path(request)
            method = str(request.method).lower()

            logger.debug(f'endpoint {method} {path}')

            endpoints = config('OAUTH2.CLIENT.ENDPOINTS')

            if token_info is None:
                logger.warning('group_required::decorator token info not present')
                raise PermissionDenied(_("token info not present."))

            logger.debug(f'group_required::decorator token_info {json.dumps(token_info)}')

            if 'application_type' in token_info and token_info['application_type'] == application_type_service:
                logger.debug('authz groups are not evaluated for service-type applications')
                return func(view, *args, **kwargs)

            endpoint = endpoints[path] if path in endpoints else None
            if not endpoint:
                logger.warning('group_required::decorator endpoint info not present')
                raise PermissionDenied(_("endpoint info not present."))

            endpoint = endpoint[method] if method in endpoint else None
            if not endpoint:
                logger.warning('endpoint info not present')
                raise PermissionDenied(_("endpoint info not present."))

            required_groups = endpoint['groups'] if 'groups' in endpoint else None

            if is_empty(required_groups):
                return func(view, *args, **kwargs)

            if 'user_groups' in token_info:
                current_groups = token_info['user_groups']
                logger.debug(f'current group {current_groups} required groups {required_groups}')

                req_groups = set(required_groups.split())
                user_groups = set([item['slug'] for item in current_groups])

                if any(group in req_groups for group in user_groups):
                    return func(view, *args, **kwargs)

                raise PermissionDenied(_("current user has not the proper groups permissions"))

            logger.warning('group_required::decorator token groups not present')
            raise PermissionDenied(_("user_groups not present at token info"))
        return inner
    return decorator
