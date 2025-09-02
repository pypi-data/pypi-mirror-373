from contextlib import suppress

import graphviz
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import SET_NULL, Q, QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from wbcore.contrib.authentication.models import User
from wbcore.contrib.workflow.models import (
    Condition,
    DataValue,
    DecisionStep,
    EmailStep,
    FinishStep,
    JoinStep,
    Process,
    ProcessStep,
    ScriptStep,
    SplitStep,
    StartStep,
    Step,
    Transition,
    UserStep,
    activate_step,
)
from wbcore.contrib.workflow.utils import get_model_serializer_class_for_instance
from wbcore.models import WBModel
from wbcore.serializers.serializers import ModelSerializer
from wbcore.utils.signals import DisconnectSignals, SignalWrapper


class Workflow(WBModel):
    """The base workflow model that can be attached to a generic model to update its status field."""

    name = models.CharField(max_length=128, verbose_name=_("Name"), unique=True)
    single_instance_execution = models.BooleanField(
        default=False,
        verbose_name=_("Single Instance Execution"),
        help_text=_(
            "Indicates wether the workflow is restricted to only one running workflow at a time. If an instance is attached to the workflow this will restrict the workflow execution per model instance."
        ),
    )
    model = models.ForeignKey(to=ContentType, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("Model"))
    status_field = models.CharField(
        max_length=64,
        verbose_name=_("Status Field"),
        help_text=_("The status field name in the attached model that needs to be updated by the workflow"),
        null=True,
        blank=True,
    )
    preserve_instance = models.BooleanField(
        default=False,
        verbose_name=_("Preserve Instance"),
        help_text=_(
            "This will preserve the attached instance's state in a JSON field when starting the workflow. You then have the option to write this data back onto the instance in a finish step, effectively preserving the instance's state throughout the workflow."
        ),
    )
    graph = models.ImageField(verbose_name=_("Graph"), blank=True, null=True)

    def start_workflow(self, start_step: StartStep, instance=None):
        """Starts a new workflow

        Args:
            start_step (StartStep): The workflow's start step
            instance (_type_, optional): An attached instance
        """

        if instance and self.preserve_instance:
            serializer: ModelSerializer = get_model_serializer_class_for_instance(instance)
            data: dict = serializer(instance).data
            process_instance = Process.objects.create(workflow=self, instance=instance, preserved_instance=data)
        else:
            process_instance = Process.objects.create(workflow=self, instance=instance)

        for data in self.attached_data.all():
            if data.default:
                DataValue.objects.create(
                    data=data,
                    value=data.default,
                    process=process_instance,
                )
            else:
                DataValue.objects.create(data=data, process=process_instance)
        transaction.on_commit(lambda: activate_step.delay(start_step.pk, process_instance.pk))

    def get_start_steps_for_workflow(self) -> QuerySet[StartStep]:
        return StartStep.objects.filter(
            Q(workflow__model__isnull=True)
            & Q(workflow=self)
            & ~Q(Q(workflow__single_instance_execution=True) & Q(workflow__process__state=Process.ProcessState.ACTIVE))
        )

    def generate_workflow_png(self) -> bytes:
        """Generates a PNG file visually displaying the workflow

        Returns:
            bytes: The created PNG as bytes

        Raises:
            graphviz.backend.execute.ExecutableNotFound: When graphviz executable is not installed on target system
        """

        # Initialize graph
        dot = graphviz.Digraph(
            "workflow",
            graph_attr={"rankdir": "LR"},
            node_attr={
                "shape": "rectangle",
                "style": "rounded",
                "orientation": "0",
                "width": "1.0",
                "height": "0.7",
                "fontname": "times bold",
                "margin": "0.0, 0.0",
            },
            edge_attr={
                "fontsize": "10.0",
                "fontname": "times italic",
            },
        )

        # Add nodes (steps)
        for step in self.associated_steps.all():
            if step.step_type == Step.StepType.FINISHSTEP:
                dot.node(
                    str(step.code),
                    step.name,
                    shape="circle",
                    style="bold",
                    width="0.5",
                    height="0.5",
                )
            elif step.step_type == Step.StepType.STARTSTEP:
                dot.node(
                    str(step.code),
                    step.name,
                    shape="circle",
                    width="0.5",
                    height="0.5",
                )
            elif step.step_type in [Step.StepType.DECISIONSTEP, Step.StepType.JOINSTEP, Step.StepType.SPLITSTEP]:
                dot.node(
                    str(step.code),
                    step.name,
                    shape="square",
                    orientation="45",
                    style="solid",
                )
            else:
                dot.node(
                    str(step.code),
                    step.name,
                )

            # Add incoming edges (transitions) for node
            for transition in step.get_incoming_transitions():
                edge_label = ""

                # Use condition as edge label. Can sadly only properly display one condition per edge
                if condition := transition.associated_conditions.first():
                    edge_label = gettext("if {} {} {}").format(
                        condition.attribute_name, condition.operator, condition.expected_value
                    )

                dot.edge(
                    str(transition.from_step.code),
                    str(transition.to_step.code),
                    label=edge_label,
                )

        return dot.pipe(format="png")

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:workflow:workflow"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:workflow:workflowrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    @classmethod
    def get_start_steps_for_instance(cls, instance) -> list[StartStep]:
        content_type_for_instance = ContentType.objects.get_for_model(instance)

        start_steps = StartStep.objects.filter(
            Q(workflow__model=content_type_for_instance)
            & ~Q(
                Q(workflow__single_instance_execution=True)
                & Q(
                    workflow__process__in=Process.objects.filter(
                        finished__isnull=True, content_type=content_type_for_instance, instance_id=instance.id
                    )
                )
            )
        )

        valid_start_steps = []
        for step in start_steps:
            if hasattr(instance, step.workflow.status_field):
                instance_status = getattr(instance, step.workflow.status_field)
                if step.status == instance_status:
                    valid_start_steps.append(step)

        return valid_start_steps

    @classmethod
    def get_next_user_step_transitions_for_instance(
        cls, instance, user: User
    ) -> list[tuple[list[Transition], ProcessStep]]:
        # TODO: OPTIMIZE
        process_steps = ProcessStep.objects.filter(
            state=ProcessStep.StepState.ACTIVE,
            process__instance_id=instance.pk,
            process__content_type=ContentType.objects.get_for_model(instance),
            step__step_type=Step.StepType.USERSTEP,
        )
        # User has to be assigned
        if not user.is_superuser:
            process_steps = process_steps.filter(
                Q(assignee=user)
                | (
                    Q(group__user=user)
                    & Q(step__in=UserStep.objects.filter(assignee_method__isnull=True))
                    & Q(assignee__isnull=True)
                )
            )

        valid_transitions_and_process_steps = []
        for process_step in process_steps:
            transitions = Transition.objects.filter(from_step__process_steps=process_step)
            # User needs to have permission to view the step
            if not user.is_superuser:
                transitions = transitions.filter(
                    Q(
                        Q(Q(Q(from_step__permission__user=user) | Q(from_step__permission__group__user=user)))
                        | Q(from_step__permission__isnull=True)
                    )
                )
            # Check conditions
            valid_transitions = []
            for transition in transitions:
                if transition.all_conditions_satisfied(process_step):
                    valid_transitions.append(transition)

            if valid_transitions:
                valid_transitions_and_process_steps.append(
                    tuple(
                        (
                            valid_transitions,
                            process_step,
                        )
                    ),
                )

        return valid_transitions_and_process_steps

    class Meta:
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflows")


@receiver(post_save, sender=Condition)
@receiver(post_save, sender=Transition)
@receiver(post_save, sender=UserStep)
@receiver(post_save, sender=EmailStep)
@receiver(post_save, sender=DecisionStep)
@receiver(post_save, sender=SplitStep)
@receiver(post_save, sender=JoinStep)
@receiver(post_save, sender=ScriptStep)
@receiver(post_save, sender=StartStep)
@receiver(post_save, sender=FinishStep)
@receiver(post_save, sender=Workflow)
def re_render_workflow_graph(sender, instance: Workflow | Step | Transition | Condition, raw: bool, **kwargs):
    if not raw:
        match sender.__name__:
            case "Workflow":
                workflow = instance
            case (
                "UserStep"
                | "EmailStep"
                | "DecisionStep"
                | "SplitStep"
                | "JoinStep"
                | "ScriptStep"
                | "StartStep"
                | "FinishStep"
            ):
                workflow = instance.workflow
            case "Transition":
                workflow = instance.to_step.workflow
            case "Condition":
                workflow = instance.transition.to_step.workflow
            case _:
                return
        with suppress(graphviz.backend.execute.ExecutableNotFound):
            graph = ContentFile(workflow.generate_workflow_png(), "workflow_graph")
            if workflow.graph:
                workflow.graph.delete(save=False)
            workflow.graph = graph
            with DisconnectSignals([SignalWrapper(post_save, re_render_workflow_graph, sender)]):
                workflow.save()
