from drf_spectacular.extensions import OpenApiAuthenticationExtension

from .config import config

class OAuth2CustomSchemaBase(OpenApiAuthenticationExtension):
    name = config('OPEN_API_SECURITY_SCHEMA_NAME')

    def get_security_definition(self, auto_schema):
        unique_scopes = set()

        endpoints = config('OAUTH2.CLIENT.ENDPOINTS')

        for endpoint, methods in endpoints.items():
            for method, details in methods.items():
                if 'scopes' in details:
                    scopes_list = details['scopes'].split()
                    unique_scopes.update(scopes_list)

        return {
            'type': 'oauth2',
            'flows': {
                'implicit': {
                    'authorizationUrl': f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.AUTHORIZATION_ENDPOINT')}',
                    'tokenUrl': f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.TOKEN_ENDPOINT')}',
                    'refreshUrl': f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.REFRESH_TOKEN_ENDPOINT')}',
                    'scopes': {scope: '' for scope in unique_scopes}
                },
            },
            'description': 'OAuth2 authentication.'
        }
