from rest_framework.viewsets import ModelViewSet


class BaseView(ModelViewSet):
    ordering_fields = {}

    def get_queryset(self):
        return self.queryset


    def apply_ordering(self, queryset):
        ordering = self.request.query_params.get('ordering')

        if ordering:
            ordering_fields = []

            for field in ordering.split(","):
                is_desc = field.startswith("-")
                field_name = field[1:] if is_desc else field

                # ordering_fields is a dict
                if isinstance(self.ordering_fields, dict):
                    mapped_field = self.ordering_fields.get(field_name)
                    if mapped_field:
                        ordering_fields.append(f"-{mapped_field}" if is_desc else mapped_field)

                # ordering_fields is an array of strings
                elif isinstance(self.ordering_fields, list):
                    if field_name in self.ordering_fields:
                        ordering_fields.append(field if not is_desc else f"-{field_name}")

            if ordering_fields:
                queryset = queryset.order_by(*ordering_fields)

        return queryset
