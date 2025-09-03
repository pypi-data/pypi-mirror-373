import logging
import os
import json

from django.core.exceptions import PermissionDenied
from django.utils.functional import wraps
from django.utils.translation import gettext_lazy as _

from .shared import get_path
from ..utils import config, is_empty


def oauth2_scope_required():
    """
      Decorator to make a view only accept particular scopes:
    """
    def decorator(func):
        @wraps(func)
        def inner(view, *args, **kwargs):

            request = view.request
            token_info = request.auth

            # shortcircuit
            if os.getenv("ENV") == 'test':
                return func(view, token_info=token_info, *args, **kwargs)

            logger = logging.getLogger('oauth2')

            path = get_path(request)
            method = str(request.method).lower()

            logger.debug('endpoint {method} {path}'.format(method=method, path=path))

            endpoints = config('OAUTH2.CLIENT.ENDPOINTS')

            if token_info is None:
                logging.getLogger('oauth2').warning(
                    'oauth2_scope_required::decorator token info not present')
                raise PermissionDenied(_("token info not present."))

            logger.debug('oauth2_scope_required::decorator token_info {}'.format(
                json.dumps(token_info)
            ))

            endpoint = endpoints[path] if path in endpoints else None
            if not endpoint:
                logger.warning('oauth2_scope_required::decorator endpoint info not present')
                raise PermissionDenied(_("endpoint info not present."))

            endpoint = endpoint[method] if method in endpoint else None
            if not endpoint:
                logger.warning('endpoint info not present')
                raise PermissionDenied(_("endpoint info not present."))

            required_scope = endpoint['scopes'] if 'scopes' in endpoint else None

            if is_empty(required_scope):
                logger.warning('require scope is empty')
                raise PermissionDenied(_("required scope not present."))

            if 'scope' in token_info:
                current_scope = token_info['scope']

                logger.debug(f'current scope {current_scope} required scope {required_scope}')
                # check origins
                # check scopes

                if len(set.intersection(set(required_scope.split()), set(current_scope.split()))):
                    return func(view, token_info=token_info, *args, **kwargs)

            logger.warning('oauth2_scope_required::decorator token scopes not present')
            raise PermissionDenied(_("token scopes not present"))
        return inner
    return decorator
