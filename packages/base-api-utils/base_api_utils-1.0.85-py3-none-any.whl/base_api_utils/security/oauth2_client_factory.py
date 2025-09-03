import logging

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from .shared import client_secret_basic_auth_method


class OAuth2ClientFactory:
    @staticmethod
    def build(idp_config: dict, app_config: dict) -> OAuth2Session:
        client_id = app_config.get('client_id', '')
        client_secret = app_config.get('client_secret', '')
        auth_method = app_config.get('auth_method', client_secret_basic_auth_method)
        scopes = app_config.get('scopes', '').split()

        client = BackendApplicationClient(client_id=client_id, scope=scopes)

        # OAuth2 endpoint urls
        authorization_endpoint = idp_config.get('authorization_endpoint', '')
        token_endpoint = idp_config.get('token_endpoint', '')

        session = OAuth2Session(client=client)

        # Retries policy
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        # Retries HTTP adapter
        http_adapter = HTTPAdapter(max_retries=retries)
        session.mount('https://', http_adapter)
        session.mount('http://', http_adapter)

        # Auth and endpoints settings
        if auth_method == client_secret_basic_auth_method:
            session.auth = (client_id, client_secret)
        session.authorization_url = authorization_endpoint
        session.token_url = token_endpoint

        logging.info("OAuth2ClientFactory - OAuth2Session created successfully with client_id: %s", client_id)
        return session
