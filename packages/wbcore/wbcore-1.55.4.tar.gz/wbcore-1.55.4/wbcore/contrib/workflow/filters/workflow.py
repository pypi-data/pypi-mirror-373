from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from wbcore import filters as wb_filters
from wbcore.contrib.workflow.models import Data, Step, Workflow


class WorkflowFilter(wb_filters.FilterSet):
    model = wb_filters.CharFilter(label=_("Attached Model"), method="filter_attached_model")
    step = wb_filters.ModelChoiceFilter(
        label=_("Associated Step"),
        queryset=Step.objects.all(),
        endpoint=Step.get_representation_endpoint(),
        value_key=Step.get_representation_value_key(),
        label_key=Step.get_representation_label_key(),
        method="filter_by_step",
    )
    # data = wb_filters.ModelChoiceFilter(
    #     label=_("Associated Data"),
    #     queryset=Data.objects.all(),
    #     endpoint=Data.get_representation_endpoint(),
    #     value_key=Data.get_representation_value_key(),
    #     label_key=Data.get_representation_label_key(),
    #     method="filter_by_data",
    # )

    def filter_attached_model(self, queryset: QuerySet[Workflow], name, value: str) -> QuerySet[Workflow]:
        if value:
            return queryset.filter(model__model=value)
        return queryset

    def filter_by_data(self, queryset: QuerySet[Workflow], name, value: Data | None) -> QuerySet[Workflow]:
        if value:
            return queryset.filter(attached_data=value)
        return queryset

    class Meta:
        model = Workflow
        fields = {
            "name": ["exact", "icontains"],
            "single_instance_execution": ["exact"],
            "preserve_instance": ["exact"],
            "status_field": ["exact", "icontains"],
        }
