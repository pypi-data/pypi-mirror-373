import logging

from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header, BaseAuthentication

from .access_token_service import AccessTokenService


class OAuth2Authentication(BaseAuthentication):

    def __init__(self):
        self.service = AccessTokenService()

    def authenticate(self, request):

        if not self.service.get_origin(request):
            raise exceptions.AuthenticationFailed('Invalid Origin.')

        auth = get_authorization_header(request).split()

        if len(auth) == 1:
            msg = 'Invalid bearer header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid bearer header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        if auth and auth[0].lower() == b'bearer':
            access_token = auth[1]
        elif 'access_token' in request.POST:
            access_token = request.POST['access_token']
        elif 'access_token' in request.GET:
            access_token = request.GET['access_token']
        else:
            return None

        logging.getLogger('oauth2').warning(
            'OAuth2Authentication::authenticate access_token {access_token}'.format(access_token=access_token))
        return self.service.validate(access_token)
