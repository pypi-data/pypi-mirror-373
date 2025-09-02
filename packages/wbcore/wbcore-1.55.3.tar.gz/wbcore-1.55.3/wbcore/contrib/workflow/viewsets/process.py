from django.db.models import F, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from wbcore import viewsets
from wbcore.contrib.authentication.models import User
from wbcore.contrib.workflow.filters import (
    AssignedProcessStepFilter,
    ProcessFilter,
    ProcessStepFilter,
    ProcessStepProcessFilter,
    ProcessStepStepFilter,
    ProcessWorkflowFilter,
)
from wbcore.contrib.workflow.models import (
    Process,
    ProcessStep,
    Step,
    Transition,
    UserStep,
)
from wbcore.contrib.workflow.serializers import (
    AssignedProcessStepSerializer,
    ProcessModelSerializer,
    ProcessStepModelSerializer,
)
from wbcore.contrib.workflow.viewsets.display import (
    AssignedProcessStepDisplayConfig,
    ProcessDisplayConfig,
    ProcessStepDisplayConfig,
)
from wbcore.contrib.workflow.viewsets.endpoints import (
    AssignedProcessStepEndpointConfig,
    ProcessEndpointConfig,
)
from wbcore.contrib.workflow.viewsets.titles import (
    AssignedProcessStepTitleConfig,
    ProcessStepTitleConfig,
    ProcessTitleConfig,
)


class ProcessModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/process.md"
    queryset = Process.objects.all()
    serializer_class = ProcessModelSerializer
    display_config_class = ProcessDisplayConfig
    title_config_class = ProcessTitleConfig
    endpoint_config_class = ProcessEndpointConfig
    search_fields = ("workflow__name", "content_type__model")
    ordering = ("workflow__name", "state", "content_type__model", "id")
    ordering_fields = (
        "id",
        "workflow__name",
        "started",
        "finished",
        "content_type__model",
    )

    def get_queryset(self):
        if workflow_id := self.kwargs.get("workflow_id"):
            return super().get_queryset().filter(workflow=workflow_id)
        return super().get_queryset()

    def get_filterset_class(self, request):
        if self.kwargs.get("workflow_id"):
            return ProcessWorkflowFilter
        return ProcessFilter


class ProcessStepModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/processstep.md"
    queryset = ProcessStep.objects.all()
    serializer_class = ProcessStepModelSerializer
    title_config_class = ProcessStepTitleConfig
    endpoint_config_class = ProcessEndpointConfig
    display_config_class = ProcessStepDisplayConfig
    serializer_class = ProcessStepModelSerializer
    search_fields = ("process__workflow__name", "step__name")
    ordering = ("step__name", "state", "process__id", "id")
    ordering_fields = (
        "id",
        "process__id",
        "step__name",
        "started",
        "finished",
        "assignee__computed_str",
        "group__name",
        "permission__name",
        "status",
        "error_message",
    )

    @cached_property
    def request_user(self) -> User:
        return self.request.user

    def get_queryset(self) -> QuerySet[ProcessStep]:
        queryset: QuerySet[ProcessStep] = (
            super().get_queryset().select_related("assignee", "permission", "group", "process")
        )
        if not self.request_user.is_superuser:
            queryset = queryset.filter(
                Q(permission__user=self.request_user)
                | Q(permission__group__user=self.request_user)
                | Q(permission__isnull=True)
            )
        if process_id := self.kwargs.get("process_id"):
            queryset = queryset.filter(process=process_id)
        elif step_id := self.kwargs.get("step_id"):
            queryset = queryset.filter(step=step_id)
        return queryset

    def get_filterset_class(self, request):
        if self.kwargs.get("process_id"):
            return ProcessStepProcessFilter
        if self.kwargs.get("step_id"):
            return ProcessStepStepFilter
        return ProcessStepFilter

    @action(detail=True, methods=["PATCH"], permission_classes=[permissions.IsAuthenticated])
    def next(self, request, pk=None):
        process_step = get_object_or_404(ProcessStep, pk=pk)
        transition = get_object_or_404(Transition, pk=request.GET.get("transition_id"))
        Step.start_next_step(process_step, transition)
        return Response({"status": "ok"})


class AssignedProcessStepModelViewSet(ProcessStepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/assignedprocessstep.md"
    title_config_class = AssignedProcessStepTitleConfig
    serializer_class = AssignedProcessStepSerializer
    endpoint_config_class = AssignedProcessStepEndpointConfig
    display_config_class = AssignedProcessStepDisplayConfig
    search_fields = ("process__workflow__name", "step__name")
    ordering = ("step__name", "step__workflow__name", "process__id", "id")
    ordering_fields = (
        "step__name",
        "started",
        "finished",
        "group__name",
        "permission__name",
        "status",
        "attached_model",
        "workflow_name",
    )

    def get_queryset(self) -> QuerySet[ProcessStep]:
        qs = (
            super()
            .get_queryset()
            .filter(
                Q(step__step_type=Step.StepType.USERSTEP)
                & Q(state=ProcessStep.StepState.ACTIVE)
                & Q(
                    Q(assignee=self.request_user)
                    | Q(
                        Q(group__user=self.request_user)
                        & Q(step__in=UserStep.objects.filter(assignee_method__isnull=True))
                        & Q(assignee__isnull=True)
                    )
                )
            )
            .annotate(
                attached_model=F("step__workflow__model__model"),
                workflow_name=F("step__workflow__name"),
            )
        ).select_related("step__workflow")
        return qs

    def get_filterset_class(self, request):
        return AssignedProcessStepFilter
