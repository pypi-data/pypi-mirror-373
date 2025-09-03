from django.db.models import ForeignKey
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .serializers_registry import SerializersRegistry
from .timestamp_field import TimestampField

class BaseModelSerializer(serializers.ModelSerializer):
    PARENT_FIELD_KEY = 'parent_field'

    created = TimestampField(read_only=True)
    modified = TimestampField(read_only=True)

    allowed_relations = []

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        request = context.get('request', None)
        fields = []
        relations = []

        if request:
            fields = request.query_params.get('fields', '').split(',')
            relations = request.query_params.get('relations', '').split(',')

            kwargs.pop('expand', None)
            kwargs.pop('fields', None)
            kwargs.pop('relations', None)
            kwargs.pop('params', None)

        super().__init__(*args, **kwargs)

        fields_requested = set(fields) if fields else set()
        relations_requested = set(relations) if relations else set()

        allowed_fields = set(self.get_allowed_fields())
        allowed_relations = set(self.get_allowed_relations())
        fields_requested &= allowed_fields
        relations_requested &= allowed_relations

        if fields_requested or relations_requested:
            # due to how the DRF serialization mechanism works, both fields and relations are treated the same
            allowed = fields_requested.union(relations_requested)

            # gets the last key of each requested field (dot notation) to search in the list of fields in the current serializer
            allowed = {item.split('.')[-1] for item in allowed}

            for field_name in list(self.fields):
                if field_name not in allowed:
                    # if the field wasn't specified in request it is removed from the list of fields to serialize
                    self.fields.pop(field_name)

        self._serialize_pk_related_fields()

    def _serialize_pk_related_fields(self):
        # Serialize all primary key related fields
        model = self.Meta.model
        for field in model._meta.fields:
            if isinstance(field, ForeignKey):
                field_name = field.name
                id_field_name = f"{field_name}_id"

                # Only add if not explicitly defined in the serializer
                if id_field_name not in self.fields:
                    self.fields[id_field_name] = serializers.PrimaryKeyRelatedField(
                        read_only=True,
                        source=field_name
                    )

    def get_allowed_fields(self):
        # required to know if the serializer was called explicitly from the view or
        # if it is a delegation from a parent serializer (parent collection field)
        # - view explicit call -> field_name
        # - parent serializer delegation -> parent_field_name.field_name
        parent_field = self.context.get(self.PARENT_FIELD_KEY, None)

        if parent_field:
            return [f"{parent_field}.{field}" for field in self.fields.keys()]

        return self.fields.keys()

    def get_delegated_allowed_relations(self, allowed_relations):
        # required to know if the serializer was called explicitly from the view or
        # if it is a delegation from a parent serializer (parent collection field)
        # - view explicit call -> field_name
        # - parent serializer delegation -> parent_field_name.field_name
        parent_field = self.context.get(self.PARENT_FIELD_KEY, None)

        if parent_field:
            return [f"{parent_field}.{allowed_relation}" for allowed_relation in allowed_relations]

        return allowed_relations

    def get_allowed_relations(self):
        return self.get_delegated_allowed_relations(self.allowed_relations)

    def get_allowed_expands(self):
        return self.allowed_relations

    def get_expand(self):
        request = self.context.get('request', None)
        str_expand = request.query_params.get('expand', '') if request else None
        if not str_expand:
            return []

        expand = str_expand.split(',')
        parent_field = self.context.get(self.PARENT_FIELD_KEY, None)

        if parent_field:
            # current serializer related expand
            pattern = f'{parent_field}.'
            return [
                field.split(pattern)[1]
                for field in expand
                if pattern in field
            ]

        return expand

    def get_validation_detail(self, code = 0):
        errors = [f'{field}: {str(detail)}'
            for field, details in self.errors.items()
            for detail in details
        ]
        return {'message': 'Validation Failed', 'errors': errors, 'code': code}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        expand = self.get_expand()
        allowed_expands = self.get_allowed_expands()

        for allowed_expand in allowed_expands:
            if not allowed_expand in expand:
                related_obj = getattr(self.Meta.model(), allowed_expand, None)

                # collection attr names remains at it is
                if not hasattr(related_obj, 'all'):
                    new_key = f'{allowed_expand}_id'
                    data[new_key] = data.pop(allowed_expand, None)

        return data

    def __getattr__(self, attr):
        if attr.startswith("get_"):
            field_name = attr[4:]
            if field_name in self.fields:
                serializer = SerializersRegistry.get(f'{self.Meta.model.__name__}.{field_name}')

                if not serializer:
                    serializer = SerializersRegistry.get(field_name)

                list_fields = getattr(self, "list_fields", set())

                if field_name in list_fields:
                    schema_field = serializers.ListField(child=serializer())
                else:
                    schema_field = serializer()

                @extend_schema_field(schema_field)
                def dynamic_method(obj):
                    expand = self.get_expand()
                    related_obj = getattr(obj, field_name, None)

                    if not related_obj or not serializer:
                        return None

                    # collection attr serialization
                    if hasattr(related_obj, 'all'):
                        collection = related_obj.all()

                        if field_name in expand:
                            return serializer(
                                collection,
                                many=True,
                                required=False,
                                # an element is added to the context to tell the serializer that it is a delegation from a parent serializer
                                context={**self.context, self.PARENT_FIELD_KEY: field_name}
                            ).data

                        return [x.id for x in collection]

                    # single object attr serialization
                    if field_name in expand:
                        return serializer(related_obj).data
                    return related_obj.id if related_obj else None

                return dynamic_method

        raise AttributeError(f"'{self.__class__.__name__}' does not have attribute '{attr}'")
