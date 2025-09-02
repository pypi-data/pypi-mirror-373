import django_filters

from wbcore.filters.mixins import WBCoreFilterMixin


class CharFilter(WBCoreFilterMixin, django_filters.CharFilter):
    filter_type = "text"
