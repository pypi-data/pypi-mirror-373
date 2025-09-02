from django.utils.translation import gettext_lazy as _

from wbcore import filters as wb_filters
from wbcore.contrib.workflow.models import Condition, Transition


class ConditionFilter(wb_filters.FilterSet):
    transition = wb_filters.ModelMultipleChoiceFilter(
        label=_("Transitions"),
        queryset=Transition.objects.all(),
        endpoint=Transition.get_representation_endpoint(),
        value_key=Transition.get_representation_value_key(),
        label_key=Transition.get_representation_label_key(),
    )

    operator = wb_filters.MultipleChoiceFilter(choices=Condition.Operator.choices, label=_("Operators"))

    class Meta:
        model = Condition
        fields = {
            "attribute_name": ["exact", "icontains"],
            "expected_value": ["exact", "icontains"],
            "negate_operator": ["exact"],
        }
