import re

from django.contrib.admindocs.views import simplify_regex

_PATH_PARAMETER_COMPONENT_RE = re.compile(
    r'<(?:(?P<converter>[^>:]+):)?(?P<parameter>\w+)>'
)

def get_path(request) -> str:
    path = simplify_regex(request.resolver_match.route)
    # Strip Django 2.0 convertors as they are incompatible with uritemplate format
    path = re.sub(_PATH_PARAMETER_COMPONENT_RE, r'{\g<parameter>}', path)
    return path.replace('{pk}', '{id}')

client_secret_basic_auth_method = 'client_secret_basic'

application_type_service = 'SERVICE'