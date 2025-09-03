import logging
import sys
from urllib.parse import urlparse

import requests
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from .abstract_access_token_service import AbstractAccessTokenService
from ..utils import config


class AccessTokenService(AbstractAccessTokenService):

    def validate(self, access_token:str):
        """
              Authenticate the request, given the access token.
        """
        logging.getLogger('oauth2').debug('AccessTokenService::validate trying to get {access_token} from cache ...'.format(access_token=access_token))
        # try get access_token from DB and check if not expired
        cached_token_info = cache.get(access_token)

        if cached_token_info is None:
            try:
                logging.getLogger('oauth2').debug(
                    'AccessTokenService::validate {access_token} is not present on cache, trying to validate from instrospection endpoint'.format(access_token=access_token))
                response = requests.post(
                    '{base_url}/{endpoint}'.format
                        (
                        base_url=config('OAUTH2.IDP.BASE_URL', None),
                        endpoint=config('OAUTH2.IDP.INTROSPECTION_ENDPOINT', None)
                    ),
                    auth=(config('OAUTH2.CLIENT.ID', None), config('OAUTH2.CLIENT.SECRET', None),),
                    params={'token': access_token},
                    verify=False if config('DEBUG', False) else True,
                    allow_redirects=False
                )

                if response.status_code == requests.codes.ok:
                    cached_token_info = response.json()
                    lifetime = config('OAUTH2.CLIENT.ACCESS_TOKEN_CACHE_LIFETIME', cached_token_info['expires_in'])
                    logging.getLogger('oauth2').debug(
                        'AccessTokenService::validate {access_token} storing on cache with lifetime {lifetime}'.format(
                            access_token=access_token, lifetime=lifetime))
                    cache.set(access_token, cached_token_info, timeout=int(lifetime))
                    logging.getLogger('oauth2').warning(
                        'http code {code} http content {content}'.format(code=response.status_code,
                                                                         content=response.content))
                    return AnonymousUser, cached_token_info

                logging.getLogger('oauth2').warning(
                    'AccessTokenService::validate http code {code} http content {content}'.format(code=response.status_code,
                                                                     content=response.content))
                return None
            except requests.exceptions.RequestException as e:
                logging.getLogger('oauth2').error(e)
                return None
            except:
                logging.getLogger('oauth2').error(sys.exc_info())
                return None

        logging.getLogger('oauth2').debug(
            'AccessTokenService::validate {access_token} cache hit'.format(
                access_token=access_token))
        return AnonymousUser, cached_token_info

    def get_origin(self, request):
        """
        This method validates and extracts the origin of the HTTP request, with a smart fallback mechanism to the Referer
        header if the Origin header is absent. It performs a critical security check to ensure the Origin and Referer hosts
        match when both are present, preventing potential mismatches and enhancing the API's security posture.
        The function returns the determined origin, which is crucial for enforcing security policies like CORS.
        """
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')

        if origin and referer:
            origin_host = urlparse(origin).netloc
            referer_host = urlparse(referer).netloc

            if origin_host != referer_host:
                logging.getLogger('oauth2').warning(f'Origin and Referer mismatch: {origin_host} != {referer_host}')
                raise ValidationError('Origin and Referer mismatch.')

        fallback_origin = origin
        if not origin and referer:
            try:
                referer_parts = urlparse(referer)
                fallback_origin = f"{referer_parts.scheme}://{referer_parts.netloc}"
                if fallback_origin:
                    logging.getLogger('oauth2').info(f'Origin header not present. Using normalized Referer as fallback: {fallback_origin}')
            except Exception as e:
                logging.getLogger('oauth2').error(f"Error parsing Referer header for fallback: {e}")
                raise ValidationError('Error parsing Referer header.')

        return fallback_origin