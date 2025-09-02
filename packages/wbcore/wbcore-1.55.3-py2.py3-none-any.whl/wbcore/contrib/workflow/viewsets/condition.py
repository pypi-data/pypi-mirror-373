from wbcore import viewsets
from wbcore.contrib.workflow.filters import ConditionFilter
from wbcore.contrib.workflow.models import Condition
from wbcore.contrib.workflow.serializers import ConditionModelSerializer
from wbcore.contrib.workflow.viewsets.display import ConditionDisplayConfig
from wbcore.contrib.workflow.viewsets.endpoints import ConditionEndpointConfig
from wbcore.contrib.workflow.viewsets.titles import ConditionTitleConfig


class ConditionModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/condition.md"
    queryset = Condition.objects.all()
    serializer_class = ConditionModelSerializer
    display_config_class = ConditionDisplayConfig
    title_config_class = ConditionTitleConfig
    search_fields = ("attribute_name", "expected_value")
    ordering = ("transition", "attribute_name", "operator", "negate_operator", "expected_value")
    filterset_class = ConditionFilter
    endpoint_config_class = ConditionEndpointConfig
    ordering_fields = (
        "attribute_name",
        "transition__name",
        "operator",
        "expected_value",
        "negate_operator",
    )

    def get_queryset(self):
        queryset = super().get_queryset().select_related("transition")
        if transition_id := self.kwargs.get("transition_id"):
            return queryset.filter(transition=transition_id)
        return queryset
