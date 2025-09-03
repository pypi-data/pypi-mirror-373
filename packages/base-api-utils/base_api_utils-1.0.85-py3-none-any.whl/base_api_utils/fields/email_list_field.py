from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class EmailListField(models.CharField):
    """
    Custom field that accepts a list of emails or a string with comma-separated emails.
    Stores them as a SEPARATOR-separated string in the database.
    """
    
    SEPARATOR = ","  # Separator constant for email list
    
    def __init__(self, *args, **kwargs):
        # Set a default max_length if not specified
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 1000
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        """Required for Django migrations"""
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs
    
    def to_python(self, value):
        """Converts the value from the database to Python"""
        if value is None:
            return value
        
        if isinstance(value, list):
            # If it comes as a list, validate each email and convert to string
            validated_emails = []
            for email in value:
                email = str(email).strip()
                if email:
                    try:
                        validate_email(email)
                        validated_emails.append(email)
                    except ValidationError:
                        raise ValidationError(f"'{email}' is not a valid email")
            return self.SEPARATOR.join(validated_emails)
        
        # If it's already a string, return as is
        return super().to_python(value)
    
    def get_prep_value(self, value):
        """Prepares the value to be saved to the database"""
        if value is None:
            return value
        
        if isinstance(value, list):
            # If it comes as a list, convert to string
            validated_emails = []
            for email in value:
                email = str(email).strip()
                if email:
                    validated_emails.append(email)
            return self.SEPARATOR.join(validated_emails)
        
        return super().get_prep_value(value)
    
    def validate(self, value, model_instance):
        """Custom field validation"""
        # Call parent validation first
        super().validate(value, model_instance)
        
        if value:
            # If the value is a list, it was already validated in to_python
            if isinstance(value, str):
                # Validate each email in the string
                emails = [email.strip() for email in value.split(self.SEPARATOR)]
                for email in emails:
                    if email:  # Avoid empty strings
                        try:
                            validate_email(email)
                        except ValidationError:
                            raise ValidationError(f"'{email}' is not a valid email")
    
    def get_emails_list(self, value):
        """Helper method to get the list of emails from the stored value"""
        if not value:
            return []
        return [email.strip() for email in value.split(self.SEPARATOR.strip()) if email.strip()]