from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from wbcore import viewsets
from wbcore.contrib.workflow.filters import TransitionFilter
from wbcore.contrib.workflow.models import Step, Transition, Workflow
from wbcore.contrib.workflow.serializers import TransitionModelSerializer
from wbcore.contrib.workflow.viewsets.display import TransitionDisplayConfig
from wbcore.contrib.workflow.viewsets.endpoints import TransitionEndpointConfig
from wbcore.contrib.workflow.viewsets.titles import TransitionTitleConfig
from wbcore.serializers import PrimaryKeyRelatedField


class TransitionModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/transition.md"
    queryset = Transition.objects.all()
    serializer_class = TransitionModelSerializer
    display_config_class = TransitionDisplayConfig
    title_config_class = TransitionTitleConfig
    endpoint_config_class = TransitionEndpointConfig
    search_fields = ("name",)
    ordering = ("name", "to_step__name")
    filterset_class = TransitionFilter
    ordering_fields = (
        "name",
        "from_step__name",
        "to_step__name",
    )

    def get_queryset(self):
        queryset = super().get_queryset().select_related("from_step", "to_step")
        if step_id := self.kwargs.get("step_id"):
            return queryset.filter(Q(from_step=step_id) | Q(to_step=step_id))
        if workflow_id := self.kwargs.get("workflow_id"):
            return queryset.filter(to_step__workflow=workflow_id)
        return queryset

    @cached_property
    def workflow(self) -> Workflow | None:
        if step_id := self.kwargs.get("step_id"):
            return Step.objects.get(id=step_id).workflow
        elif workflow_id := self.kwargs.get("workflow_id"):
            return Workflow.objects.get(id=workflow_id)

    def get_serializer_class(self):
        if self.workflow:

            class Serializer(TransitionModelSerializer):
                from_step = PrimaryKeyRelatedField(
                    queryset=Step.objects.filter(workflow=self.workflow), label=_("From"), required=False
                )
                to_step = PrimaryKeyRelatedField(
                    queryset=Step.objects.filter(workflow=self.workflow), label=_("To"), required=False
                )

            return Serializer
        return super().get_serializer_class()
