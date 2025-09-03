from rest_framework.filters import OrderingFilter


class CustomOrderingFilter(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)
        if ordering:
            ordering_map = getattr(view, 'ordering_fields', {})

            mapped_ordering = []
            for field in ordering:
                desc = '-' if field.startswith('-') else ''
                clean_field = field.lstrip('-')
                mapped_ordering.append(desc + ordering_map.get(clean_field, clean_field))
            return mapped_ordering
        return ordering
