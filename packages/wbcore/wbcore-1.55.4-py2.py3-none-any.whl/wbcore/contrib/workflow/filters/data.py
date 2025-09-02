from django.utils.translation import gettext_lazy as _

from wbcore import filters as wb_filters
from wbcore.contrib.workflow.models import Data, Workflow


class DataFilter(wb_filters.FilterSet):
    workflow = wb_filters.ModelMultipleChoiceFilter(
        label=_("Workflows"),
        queryset=Workflow.objects.all(),
        endpoint=Workflow.get_representation_endpoint(),
        value_key=Workflow.get_representation_value_key(),
        label_key=Workflow.get_representation_label_key(),
    )

    data_type = wb_filters.MultipleChoiceFilter(choices=Data.DataType.choices, label=_("Data Types"))

    class Meta:
        model = Data
        fields = {
            "label": ["exact", "icontains"],
            "help_text": ["exact", "icontains"],
            "default": ["exact", "icontains"],
            "required": ["exact"],
        }
