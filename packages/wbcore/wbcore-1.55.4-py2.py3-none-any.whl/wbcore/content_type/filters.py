from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError

from wbcore import filters as wb_filters


class ContentTypeFilterSet(wb_filters.FilterSet):
    related_name_isnull = wb_filters.CharFilter(method="filter_related_name_isnull")

    def filter_related_name_isnull(self, queryset, label, value):
        if value:
            try:
                return queryset.filter(**{f"{value}__isnull": False}).distinct()
            except FieldError:
                pass
        return queryset

    class Meta:
        model = ContentType
        fields = {"id": ["in", "exact"]}
