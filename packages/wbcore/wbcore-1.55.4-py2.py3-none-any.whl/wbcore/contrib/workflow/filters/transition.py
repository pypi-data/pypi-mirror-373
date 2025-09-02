from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from wbcore import filters as wb_filters
from wbcore.contrib.workflow.models import Condition, Step, Transition


class TransitionFilter(wb_filters.FilterSet):
    from_step = wb_filters.ModelMultipleChoiceFilter(
        label=_("From"),
        queryset=Step.objects.all(),
        endpoint=Step.get_representation_endpoint(),
        value_key=Step.get_representation_value_key(),
        label_key=Step.get_representation_label_key(),
    )
    to_step = wb_filters.ModelMultipleChoiceFilter(
        label=_("To"),
        queryset=Step.objects.all(),
        endpoint=Step.get_representation_endpoint(),
        value_key=Step.get_representation_value_key(),
        label_key=Step.get_representation_label_key(),
    )
    condition = wb_filters.ModelChoiceFilter(
        label=_("Associated Condition"),
        queryset=Condition.objects.all(),
        endpoint=Condition.get_representation_endpoint(),
        value_key=Condition.get_representation_value_key(),
        label_key=Condition.get_representation_label_key(),
        method="filter_by_condition",
    )

    def filter_by_condition(self, queryset: QuerySet[Transition], name, value: Condition) -> QuerySet[Transition]:
        if value:
            return queryset.filter(associated_conditions=value)
        return queryset

    class Meta:
        model = Transition
        fields = {
            "name": ["exact", "icontains"],
            "icon": ["icontains"],
        }
