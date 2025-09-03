from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class NullableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            return None
        except (TypeError, ValueError):
            self.fail('invalid')