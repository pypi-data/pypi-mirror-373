from wbcore import viewsets
from wbcore.contrib.workflow.filters import (
    DecisionStepFilter,
    EmailStepFilter,
    FinishStepFilter,
    JoinStepFilter,
    ScriptStepFilter,
    SplitStepFilter,
    StartStepFilter,
    StepFilter,
    StepWorkflowFilter,
    UserStepFilter,
)
from wbcore.contrib.workflow.models import (
    DecisionStep,
    Display,
    EmailStep,
    FinishStep,
    JoinStep,
    ScriptStep,
    SplitStep,
    StartStep,
    Step,
    UserStep,
)
from wbcore.contrib.workflow.serializers import (
    DecisionStepModelSerializer,
    DisplayModelSerializer,
    EmailStepModelSerializer,
    FinishStepModelSerializer,
    JoinStepModelSerializer,
    ScriptStepModelSerializer,
    SplitStepModelSerializer,
    StartStepModelSerializer,
    StepModelSerializer,
    UserStepModelSerializer,
)
from wbcore.contrib.workflow.viewsets.buttons import StepButtonConfig
from wbcore.contrib.workflow.viewsets.display import (
    BaseStepDisplayConfig,
    EmailStepDisplayConfig,
    FinishDisplayConfig,
    JoinStepDisplayConfig,
    ScriptStepDisplayConfig,
    StartStepDisplay,
    StepDisplayConfig,
    UserStepDisplayConfig,
)
from wbcore.contrib.workflow.viewsets.endpoints import (
    DisplayEndpointConfig,
    StepEndpointConfig,
)
from wbcore.contrib.workflow.viewsets.titles import (
    DecisionStepTitleConfig,
    EmailStepTitleConfig,
    FinishStepTitleConfig,
    JoinStepTitleConfig,
    ScriptStepTitleConfig,
    SplitStepTitleConfig,
    StartStepTitleConfig,
    StepTitleConfig,
    UserStepTitleConfig,
)
from wbcore.metadata.configs.buttons import ButtonViewConfig


class StepModelViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepModelSerializer
    display_config_class = StepDisplayConfig
    search_fields = ("name",)
    ordering = ("workflow__name", "name")
    endpoint_config_class = StepEndpointConfig
    title_config_class = StepTitleConfig
    button_config_class = StepButtonConfig
    ordering_fields = (
        "name",
        "workflow__name",
        "code",
        "status",
        "step_type",
    )

    def get_queryset(self):
        # TODO: OPTIMIZE PERFORMANCE, 390 duplicate queries
        queryset = super().get_queryset().select_related("workflow")
        if workflow_id := self.kwargs.get("workflow_id"):
            return queryset.filter(workflow=workflow_id)
        return queryset

    def get_filterset_class(self, request):
        if self.kwargs.get("workflow_id"):
            return StepWorkflowFilter
        return StepFilter


class UserStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/userstep.md"
    queryset = UserStep.objects.all()
    serializer_class = UserStepModelSerializer
    display_config_class = UserStepDisplayConfig
    title_config_class = UserStepTitleConfig
    search_fields = ("name", "assignee", "group")
    button_config_class = ButtonViewConfig
    ordering = ("workflow__name", "assignee__email", "name")
    ordering_fields = StepModelViewSet.ordering_fields + (
        "assignee__computed_str",
        "group__name",
        "notify_user",
        "permission__name",
        "assignee_method",
    )

    def get_queryset(self):
        return super().get_queryset().select_related("assignee")

    def get_filterset_class(self, request):
        return UserStepFilter


class DecisionStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/decisionstep.md"
    queryset = DecisionStep.objects.all()
    title_config_class = DecisionStepTitleConfig
    button_config_class = ButtonViewConfig
    display_config_class = BaseStepDisplayConfig
    serializer_class = DecisionStepModelSerializer

    def get_filterset_class(self, request):
        return DecisionStepFilter


class StartStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/startstep.md"
    queryset = StartStep.objects.all()
    title_config_class = StartStepTitleConfig
    button_config_class = ButtonViewConfig
    display_config_class = StartStepDisplay
    serializer_class = StartStepModelSerializer

    def get_filterset_class(self, request):
        return StartStepFilter


class SplitStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/splitstep.md"
    queryset = SplitStep.objects.all()
    title_config_class = SplitStepTitleConfig
    button_config_class = ButtonViewConfig
    display_config_class = BaseStepDisplayConfig
    serializer_class = SplitStepModelSerializer

    def get_filterset_class(self, request):
        return SplitStepFilter


class JoinStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/joinstep.md"
    queryset = JoinStep.objects.all()
    title_config_class = JoinStepTitleConfig
    button_config_class = ButtonViewConfig
    display_config_class = JoinStepDisplayConfig
    serializer_class = JoinStepModelSerializer
    ordering = ("workflow__name", "wait_for_all", "name")
    ordering_fields = StepModelViewSet.ordering_fields + ("wait_for_all",)

    def get_filterset_class(self, request):
        return JoinStepFilter


class ScriptStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/scriptstep.md"
    queryset = ScriptStep.objects.all()
    title_config_class = ScriptStepTitleConfig
    button_config_class = ButtonViewConfig
    display_config_class = ScriptStepDisplayConfig
    serializer_class = ScriptStepModelSerializer
    ordering_fields = StepModelViewSet.ordering_fields + ("script",)

    def get_filterset_class(self, request):
        return ScriptStepFilter


class EmailStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/emailstep.md"
    queryset = EmailStep.objects.all()
    title_config_class = EmailStepTitleConfig
    button_config_class = ButtonViewConfig
    display_config_class = EmailStepDisplayConfig
    serializer_class = EmailStepModelSerializer
    ordering_fields = StepModelViewSet.ordering_fields + (
        "subject",
        "to__adress",
        "cc__adress",
        "bcc__address",
        "template__name",
    )
    search_fields = ("name", "subject", "to__address")

    def get_filterset_class(self, request):
        return EmailStepFilter

    def get_queryset(self):
        return super().get_queryset().prefetch_related("to", "cc", "bcc")


class FinishStepModelViewSet(StepModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/finishstep.md"
    queryset = FinishStep.objects.all()
    title_config_class = FinishStepTitleConfig
    button_config_class = ButtonViewConfig
    display_config_class = FinishDisplayConfig
    serializer_class = FinishStepModelSerializer
    ordering_fields = StepModelViewSet.ordering_fields + ("write_preserved_instance",)

    def get_filterset_class(self, request):
        return FinishStepFilter


class DisplayModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "workflow/markdown/documentation/display.md"
    queryset = Display.objects.all()
    serializer_class = DisplayModelSerializer
    endpoint_config_class = DisplayEndpointConfig
    search_fields = ordering = ("name",)
    ordering_fields = (
        "name",
        "grid_template_areas",
    )
