from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from wbcore import viewsets
from wbcore.contrib.workflow.filters import WorkflowFilter
from wbcore.contrib.workflow.models import StartStep, Workflow
from wbcore.contrib.workflow.serializers import WorkflowModelSerializer
from wbcore.contrib.workflow.viewsets.display import WorkflowDisplayConfig
from wbcore.contrib.workflow.viewsets.titles import WorkflowTitleConfig


class WorkflowModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/workflow.md"
    queryset = Workflow.objects.all()
    serializer_class = WorkflowModelSerializer
    display_config_class = WorkflowDisplayConfig
    title_config_class = WorkflowTitleConfig
    search_fields = ordering = ("name",)
    filterset_class = WorkflowFilter
    ordering_fields = (
        "name",
        "single_instance_execution",
        "model__model",
        "status_field",
        "preserve_instance",
    )

    @action(detail=True, methods=["PATCH"], permission_classes=[permissions.IsAuthenticated])
    def start(self, request, pk=None):
        start_step = get_object_or_404(StartStep, pk=request.GET.get("step_id"))
        workflow = get_object_or_404(Workflow, pk=pk)
        instance_id: int | None = request.GET.get("instance_id")
        instance = get_object_or_404(workflow.model.model_class(), pk=instance_id) if instance_id else None
        workflow.start_workflow(start_step, instance)
        return Response({"status": "ok"})
