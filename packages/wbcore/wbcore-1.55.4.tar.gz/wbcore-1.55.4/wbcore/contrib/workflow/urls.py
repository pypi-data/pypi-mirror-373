from django.urls import include, path

from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()

router.register(r"workflow", viewsets.WorkflowModelViewSet, basename="workflow")
router.register(r"workflowrepresentation", viewsets.WorkflowModelViewSet, basename="workflowrepresentation")
router.register(r"step", viewsets.StepModelViewSet, basename="step")
router.register(r"steprepresentation", viewsets.StepModelViewSet, basename="steprepresentation")
router.register(r"transition", viewsets.TransitionModelViewSet, basename="transition")
router.register(r"transitionrepresentation", viewsets.TransitionModelViewSet, basename="transitionrepresentation")
router.register(r"condition", viewsets.ConditionModelViewSet, basename="condition")
router.register(r"conditionrepresentation", viewsets.ConditionModelViewSet, basename="conditionrepresentation")
router.register(r"userstep", viewsets.UserStepModelViewSet, basename="userstep")
router.register(r"usersteprepresentation", viewsets.UserStepModelViewSet, basename="usersteprepresentation")
router.register(r"process", viewsets.ProcessModelViewSet, basename="process")
router.register(r"processrepresentation", viewsets.ProcessModelViewSet, basename="processrepresentation")
router.register(r"processstep", viewsets.ProcessStepModelViewSet, basename="processstep")
router.register(r"processsteprepresentation", viewsets.ProcessStepModelViewSet, basename="processsteprepresentation")
router.register(r"processstep-assigned", viewsets.AssignedProcessStepModelViewSet, basename="processstep-assigned")
router.register(r"display", viewsets.DisplayModelViewSet, basename="display")
router.register(r"displayrepresentation", viewsets.DisplayModelViewSet, basename="displayrepresentation")
router.register(r"decisionstep", viewsets.DecisionStepModelViewSet, basename="decisionstep")
router.register(
    r"decisionsteprepresentation", viewsets.DecisionStepModelViewSet, basename="decisionsteprepresentation"
)
router.register(r"startstep", viewsets.StartStepModelViewSet, basename="startstep")
router.register(r"startsteprepresentation", viewsets.StartStepModelViewSet, basename="startsteprepresentation")
router.register(r"splitstep", viewsets.SplitStepModelViewSet, basename="splitstep")
router.register(r"splitsteprepresentation", viewsets.SplitStepModelViewSet, basename="splitsteprepresentation")
router.register(r"joinstep", viewsets.JoinStepModelViewSet, basename="joinstep")
router.register(r"joinsteprepresentation", viewsets.JoinStepModelViewSet, basename="joinsteprepresentation")
router.register(r"scriptstep", viewsets.ScriptStepModelViewSet, basename="scriptstep")
router.register(r"scriptsteprepresentation", viewsets.ScriptStepModelViewSet, basename="scriptsteprepresentation")
router.register(r"emailstep", viewsets.EmailStepModelViewSet, basename="emailstep")
router.register(r"emailsteprepresentation", viewsets.EmailStepModelViewSet, basename="emailsteprepresentation")
router.register(r"finishstep", viewsets.FinishStepModelViewSet, basename="finishstep")
router.register(r"finishsteprepresentation", viewsets.FinishStepModelViewSet, basename="finishsteprepresentation")
router.register(r"data", viewsets.DataModelViewSet, basename="data")
router.register(r"datarepresentation", viewsets.DataModelViewSet, basename="datarepresentation")

step_router = WBCoreRouter()
step_router.register(r"transition-step", viewsets.TransitionModelViewSet, basename="transition-step")
step_router.register(r"processstep-step", viewsets.ProcessStepModelViewSet, basename="processstep-step")

workflow_router = WBCoreRouter()
workflow_router.register(r"transition-workflow", viewsets.TransitionModelViewSet, basename="transition-workflow")
workflow_router.register(r"step-workflow", viewsets.StepModelViewSet, basename="step-workflow")
workflow_router.register(r"process-workflow", viewsets.ProcessModelViewSet, basename="process-workflow")
workflow_router.register(r"data-workflow", viewsets.DataModelViewSet, basename="data-workflow")

transition_router = WBCoreRouter()
transition_router.register(r"condition-transition", viewsets.ConditionModelViewSet, basename="condition-transition")

process_router = WBCoreRouter()
process_router.register(r"processstep-process", viewsets.ProcessStepModelViewSet, basename="processstep-process")

urlpatterns = [
    path("", include(router.urls)),
    path("step/<int:step_id>/", include(step_router.urls)),
    path("workflow/<int:workflow_id>/", include(workflow_router.urls)),
    path("transition/<int:transition_id>/", include(transition_router.urls)),
    path("process/<str:process_id>/", include(process_router.urls)),
]
