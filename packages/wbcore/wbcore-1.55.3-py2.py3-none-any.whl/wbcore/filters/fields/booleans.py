import django_filters

from wbcore.filters.mixins import WBCoreFilterMixin


class BooleanFilter(WBCoreFilterMixin, django_filters.BooleanFilter):
    filter_type = "boolean"
