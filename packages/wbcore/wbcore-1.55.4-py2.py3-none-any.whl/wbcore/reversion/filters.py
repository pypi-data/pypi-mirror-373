from reversion.models import Revision, Version

from wbcore import filters as wb_filters


class RevisionFilterSet(wb_filters.FilterSet):
    user = wb_filters.ModelChoiceFilter(
        queryset=Revision.objects.all(),
        endpoint="wbcore:revisionrepresentation-list",
        value_key="id",
        label_key="{{user}} - {{date_created}}",
    )
    profile = wb_filters.NumberFilter(method="filter_profile")

    def filter_profile(self, queryset, name, value):
        return queryset.filter(user__profile=value)

    class Meta:
        model = Revision
        fields = {"date_created": ["gte", "exact", "lte"]}


class VersionFilterSet(wb_filters.FilterSet):
    content_type = wb_filters.NumberFilter(method="filter_content_type")
    exclude_id = wb_filters.NumberFilter(method="filter_exclude_id")

    def filter_content_type(self, queryset, name, value):
        if value:
            return queryset.filter(content_type=value)
        return queryset

    def filter_exclude_id(self, queryset, name, value):
        if value:
            return queryset.exclude(id=value)
        return queryset

    class Meta:
        model = Version
        fields = {"content_type": ["exact"], "object_id": ["exact"]}
