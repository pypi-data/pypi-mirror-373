import logging
import traceback

from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, ErrorDetail

from .external_errors import handle_external_service_errors

def flatten_validation_errors(errors, parent_key=''):
    result = []

    if isinstance(errors, dict):
        for key, value in errors.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            result.extend(flatten_validation_errors(value, full_key))

    elif isinstance(errors, list):
        for index, item in enumerate(errors):
            if isinstance(item, dict):
                result.extend(flatten_validation_errors(item, parent_key))
            else:
                msg = str(item).rstrip('.') if isinstance(item, ErrorDetail) else str(item)
                result.append(f"{parent_key}: {msg}")

    else:
        # Single messages
        msg = str(errors).rstrip('.') if isinstance(errors, ErrorDetail) else str(errors)
        result.append(f"{parent_key}: {msg}")

    return result

def custom_exception_handler(e, context):
    if isinstance(e, NotFound):
        return Response({'message': e.__str__()}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(e, ValidationError):
        errors = flatten_validation_errors(e.detail)
        return Response({'message': 'Validation Failed', 'errors': errors, 'code': 0},
                        status=status.HTTP_412_PRECONDITION_FAILED)

    # First check if DRF handles it
    response = exception_handler(e, context)

    if response is not None:
        return response

    external_error_response = handle_external_service_errors(e)
    if external_error_response:
        return external_error_response

    # Default to 500
    logging.getLogger('api').error(e)
    logging.getLogger('api').error(traceback.format_exc())
    return Response({'message': 'server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class S3Exception(Exception):
    def __init__(self, message):
        super().__init__(message)