from wbcore import viewsets
from wbcore.contrib.workflow.filters import DataFilter
from wbcore.contrib.workflow.models import Data
from wbcore.contrib.workflow.serializers import DataModelSerializer
from wbcore.contrib.workflow.viewsets.display import DataDisplayConfig
from wbcore.contrib.workflow.viewsets.endpoints import DataEndpointConfig
from wbcore.contrib.workflow.viewsets.titles import DataTitleConfig


class DataModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/data.md"
    queryset = Data.objects.all()
    serializer_class = DataModelSerializer
    display_config_class = DataDisplayConfig
    title_config_class = DataTitleConfig
    search_fields = ("label",)
    ordering = ("workflow__name", "data_type", "label")
    filterset_class = DataFilter
    endpoint_config_class = DataEndpointConfig
    ordering_fields = (
        "workflow__name",
        "data_type",
        "label",
        "help_text",
        "default",
        "required",
    )

    def get_queryset(self):
        queryset = super().get_queryset().select_related("workflow")
        if workflow_id := self.kwargs.get("workflow_id"):
            return queryset.filter(workflow=workflow_id)
        return queryset
