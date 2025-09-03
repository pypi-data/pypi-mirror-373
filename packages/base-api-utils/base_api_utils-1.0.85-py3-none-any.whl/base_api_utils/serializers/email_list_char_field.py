from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from ..fields import EmailListField

@extend_schema_field(
    {
        'type': 'array',
        'items': build_basic_type(OpenApiTypes.EMAIL),
        'description': 'List of email addresses',
        'example': ['email1@example.com', 'email2@example.com']
    })
class EmailListCharField(serializers.CharField):
    """
    Serializer field for the EmailListField model field.
    Handles validation for a EmailListField.SEPARATOR-separated string of emails.
    """
    def to_internal_value(self, data):
        if not isinstance(data, (str, list)):
            raise serializers.ValidationError("Expected a string or a list of emails.")

        if isinstance(data, list):
            emails = [str(email).strip() for email in data]
        else: # Assuming it's a string
            emails = [email.strip() for email in data.split(EmailListField.SEPARATOR)]

        validated_emails = []
        for email in emails:
            if email:
                try:
                    validate_email(email)
                    validated_emails.append(email)
                except ValidationError:
                    raise serializers.ValidationError(f"'{email}' is not a valid email address.")

        return EmailListField.SEPARATOR.join(validated_emails)

    def to_representation(self, value):
        if not value:
            return []
        return [email.strip() for email in value.split(EmailListField.SEPARATOR) if email.strip()]