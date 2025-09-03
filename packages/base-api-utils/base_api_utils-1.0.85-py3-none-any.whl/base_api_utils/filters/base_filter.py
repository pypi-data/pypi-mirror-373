import re

from datetime import datetime, timezone

from ..utils import safe_str_to_number
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError


class BaseFilter(filters.FilterSet):
    filter_op = '='
    filters_separator = ','
    name_operator_separator = '__'
    filter_param = 'filter'
    filters_param = 'filter[]'

    operator_map = {
        '>=': "__gte",
        '<=': "__lte",
        '>': "__gt",
        '<': "__lt",
        '==': "",
        '=@': "__icontains",
        '@@': "__istartswith"
    }

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        self.split_pattern = '|'.join(map(re.escape, self.operator_map.keys()))
        self.is_number_re = re.compile(r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$')

    def is_numeric(self, value):
        return bool(self.is_number_re.match(value))

    def is_boolean(self, value):
        return str(value).lower() in ['true', 'false']

    def parse_filter(self, filter_str):
        try:
            parts = re.split(f"({self.split_pattern})", filter_str)
            field_name = parts[0]
            operator = self.operator_map.get(parts[1].strip())
            value = parts[2]
        except ValueError:
            raise ValidationError("Invalid filter format. Expected 'key=value'.")
        return field_name.strip(), operator, value.strip()

    def filter_field(self, queryset, filter_name, filter_op, filter_value):
        """
        Generic method for filtering based on dynamic comparisons.
        """
        if not filter_op is None:
            value_to_filter = (
                safe_str_to_number(filter_value)) \
                if filter_op in ['__gte', '__lte', '__gt', '__lt', ''] and self.is_numeric(filter_value) \
                else filter_value

            if self.is_boolean(value_to_filter):
                value_to_filter = str(value_to_filter).lower() == 'true'

            return queryset.filter(**{f"{filter_name}{filter_op}": value_to_filter})

        return queryset

    def apply_or_filters(self, queryset, or_filters):
        or_filter_subquery = Q()
        active_filters = self.get_filters()
        for or_filter in or_filters:
            filter_name, filter_op, filter_value = self.parse_filter(or_filter)
            if filter_name in active_filters:
                filter_name = active_filters[filter_name].field_name
            or_filter_subquery |= Q(**{f"{filter_name}{filter_op}": filter_value})
        queryset = queryset.filter(or_filter_subquery)
        return queryset

    def epoch_to_datetime(self, queryset, name, op, value):
        try:
            dt = datetime.fromtimestamp(int(value), tz=timezone.utc)
            return queryset.filter(**{f"{name}{op}": dt})
        except (ValueError, TypeError):
            return queryset.none()

    def filter_queryset(self, queryset):
        """
        Overrides the `filter_queryset` method to apply filters dynamically.
        Invoked when Django applies filters to the query.

        Examples of possible filters:
        - filter[]=field1=@value1,field2>value2                                        (OR filter)

        - filter=field1=@value1,field2>value2                                          (OR filter)

        - filter[]=field1=@value1&filter[]=field2>value2                               (AND filter)

        - filter==field1@@value

        - filter[]=field1=@value1,field2=@value2&filter[]=field3=@value3               (OR then AND filter)
          Generates: ...WHERE (field1 LIKE '%value1%' OR field2 LIKE '%value2%') AND field3 LIKE '%value3%'
        """
        and_filter_key = 'and'
        or_filter_key = 'or'

        filter_without_brackets = self.data.get(self.filter_param, None)
        filter_with_brackets = self.data.getlist(self.filters_param, [])

        filter_category = {
            or_filter_key: filter_without_brackets.split(self.filters_separator) if filter_without_brackets else [],
            and_filter_key: []
        }

        for item in filter_with_brackets:
            if "," in item:
                filter_category[or_filter_key].extend(item.split(self.filters_separator))
            else:
                filter_category[and_filter_key].append(item)

        # Apply dynamic filters
        if filter_category[or_filter_key]:
            queryset = self.apply_or_filters(queryset, filter_category[or_filter_key])

        if not filter_category[and_filter_key]:
            return queryset

        # Get filters defined in the FilterSet
        active_filters = self.get_filters()

        for and_filter in filter_category[and_filter_key]:
            filter_name, filter_op, filter_value = self.parse_filter(and_filter)
            if filter_name in active_filters:
                filter_instance = active_filters[filter_name]

                if filter_instance.method == 'epoch_to_datetime':
                    queryset = self.epoch_to_datetime(queryset, filter_instance.field_name, filter_op, filter_value)
                    continue

                queryset = self.filter_field(queryset, filter_instance.field_name, filter_op, filter_value)

        return queryset
