import logging

from drf_spectacular.openapi import AutoSchema

from .config import config


class CustomAutoSchema(AutoSchema):
    def get_operation(self, path, path_regex, path_prefix, method, registry):
        operation = super().get_operation(path, path_regex, path_prefix, method, registry)

        try:
            if operation and type(operation) == dict:
                endpoints = config('OAUTH2.CLIENT.ENDPOINTS')
                schema_name = config('OPEN_API_SECURITY_SCHEMA_NAME')
                endpoint = endpoints.get(path, {}).get(method.lower(), None) if endpoints else {}
                description = operation.get('description', '')
                security_scopes = operation.get('security', [])[0].get(schema_name, None)

                if endpoint:
                    description = description if description else endpoint.get('desc', '')
                    scopes = endpoint.get('scopes', '')
                    if scopes:
                        description = f'{description} - Scopes: {scopes}'
                        if security_scopes is None:
                            operation['security'] = [{schema_name: scopes.split()}]
                        else:
                            security_scopes.extend(scopes.split())
                    groups = endpoint.get('groups', '')
                    if groups:
                        description = f'{description} - Groups: {groups}'

                    operation['description'] = description

        except Exception as e:
            logging.getLogger('api').error(e)

        return operation