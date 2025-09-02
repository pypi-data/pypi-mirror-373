from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from wbcore import filters as wb_filters
from wbcore.contrib.authentication.models import Group, Permission, User
from wbcore.contrib.directory.models import EmailContact
from wbcore.contrib.workflow.models import (
    DecisionStep,
    EmailStep,
    FinishStep,
    JoinStep,
    ScriptStep,
    SplitStep,
    StartStep,
    Step,
    Transition,
    UserStep,
    Workflow,
)
from wbcore.contrib.workflow.sites import workflow_site


class StepBaseFilter(wb_filters.FilterSet):
    code = wb_filters.NumberFilter(label=_("Code"), field_name="code", lookup_expr="exact")
    code__lte = wb_filters.NumberFilter(label=_("Code"), field_name="code", lookup_expr="lte")
    code__gte = wb_filters.NumberFilter(label=_("Code"), field_name="code", lookup_expr="gte")
    transition = wb_filters.ModelChoiceFilter(
        label=_("Associated Transition"),
        queryset=Transition.objects.all(),
        endpoint=Transition.get_representation_endpoint(),
        value_key=Transition.get_representation_value_key(),
        label_key=Transition.get_representation_label_key(),
        method="filter_by_transition",
    )

    def filter_by_transition(self, queryset: QuerySet[Step], name, value: Transition) -> QuerySet[Step]:
        if value:
            return queryset.filter(Q(outgoing_transitions=value) | Q(incoming_transitions=value))
        return queryset

    class Meta:
        model = Step
        fields = {
            "name": ["exact", "icontains"],
            "status": ["exact", "icontains"],
        }


class StepWorkflowFilter(StepBaseFilter):
    permission = wb_filters.ModelMultipleChoiceFilter(
        label=_("Permissions"),
        queryset=Permission.objects.all(),
        endpoint=Permission.get_representation_endpoint(),
        value_key=Permission.get_representation_value_key(),
        label_key=Permission.get_representation_label_key(),
    )
    step_type = wb_filters.MultipleChoiceFilter(label=_("Step Types"), choices=Step.StepType.choices)

    class Meta(StepBaseFilter.Meta):
        model = Step
        fields = StepBaseFilter.Meta.fields


class StepFilter(StepWorkflowFilter):
    workflow = wb_filters.ModelMultipleChoiceFilter(
        label=_("Workflows"),
        queryset=Workflow.objects.all(),
        endpoint=Workflow.get_representation_endpoint(),
        value_key=Workflow.get_representation_value_key(),
        label_key=Workflow.get_representation_label_key(),
    )

    class Meta(StepWorkflowFilter.Meta):
        model = Step
        fields = StepWorkflowFilter.Meta.fields


class UserStepFilter(StepBaseFilter):
    permission = wb_filters.ModelMultipleChoiceFilter(
        label=_("Permissions"),
        queryset=Permission.objects.all(),
        endpoint=Permission.get_representation_endpoint(),
        value_key=Permission.get_representation_value_key(),
        label_key=Permission.get_representation_label_key(),
    )
    workflow = wb_filters.ModelMultipleChoiceFilter(
        label=_("Workflows"),
        queryset=Workflow.objects.all(),
        endpoint=Workflow.get_representation_endpoint(),
        value_key=Workflow.get_representation_value_key(),
        label_key=Workflow.get_representation_label_key(),
    )
    assignee = wb_filters.ModelMultipleChoiceFilter(
        label=_("Assignees"),
        queryset=User.objects.all(),
        endpoint=User.get_representation_endpoint(),
        value_key=User.get_representation_value_key(),
        label_key=User.get_representation_label_key(),
    )

    group = wb_filters.ModelMultipleChoiceFilter(
        label=_("Groups"),
        queryset=Group.objects.all(),
        endpoint=Group.get_representation_endpoint(),
        value_key=Group.get_representation_value_key(),
        label_key=Group.get_representation_label_key(),
    )

    assignee_method = wb_filters.MultipleChoiceFilter(
        label=_("Assignee Methods"), choices=workflow_site.assignees_choices
    )

    # display = wb_filters.ModelMultipleChoiceFilter(
    #     label=_("Displays"),
    #     queryset=Display.objects.all(),
    #     endpoint=Display.get_representation_endpoint(),
    #     value_key=Display.get_representation_value_key(),
    #     label_key=Display.get_representation_label_key(),
    # )

    class Meta(StepBaseFilter.Meta):
        model = UserStep
        fields = StepBaseFilter.Meta.fields | {
            "notify_user": ["exact"],
        }


class DecisionStepFilter(StepBaseFilter):
    permission = wb_filters.ModelMultipleChoiceFilter(
        label=_("Permissions"),
        queryset=Permission.objects.all(),
        endpoint=Permission.get_representation_endpoint(),
        value_key=Permission.get_representation_value_key(),
        label_key=Permission.get_representation_label_key(),
    )
    workflow = wb_filters.ModelMultipleChoiceFilter(
        label=_("Workflows"),
        queryset=Workflow.objects.all(),
        endpoint=Workflow.get_representation_endpoint(),
        value_key=Workflow.get_representation_value_key(),
        label_key=Workflow.get_representation_label_key(),
    )

    class Meta(StepBaseFilter.Meta):
        model = DecisionStep
        fields = StepBaseFilter.Meta.fields


class SplitStepFilter(DecisionStepFilter):
    class Meta(DecisionStepFilter.Meta):
        model = SplitStep
        fields = DecisionStepFilter.Meta.fields


class StartStepFilter(StepBaseFilter):
    workflow = wb_filters.ModelMultipleChoiceFilter(
        label=_("Workflows"),
        queryset=Workflow.objects.all(),
        endpoint=Workflow.get_representation_endpoint(),
        value_key=Workflow.get_representation_value_key(),
        label_key=Workflow.get_representation_label_key(),
    )

    class Meta(StepBaseFilter.Meta):
        model = StartStep
        fields = StepBaseFilter.Meta.fields


class JoinStepFilter(DecisionStepFilter):
    class Meta(DecisionStepFilter.Meta):
        model = JoinStep
        fields = DecisionStepFilter.Meta.fields | {
            "wait_for_all": ["exact"],
        }


class ScriptStepFilter(DecisionStepFilter):
    class Meta(DecisionStepFilter.Meta):
        model = ScriptStep
        fields = DecisionStepFilter.Meta.fields | {
            "script": ["exact", "icontains"],
        }


class EmailStepFilter(DecisionStepFilter):
    template = wb_filters.CharFilter(label=_("Template"), method="filter_template_name")
    to = wb_filters.ModelMultipleChoiceFilter(
        label=pgettext_lazy("Email context", "To"),
        queryset=EmailContact.objects.all(),
        endpoint=EmailContact.get_representation_endpoint(),
        value_key=EmailContact.get_representation_value_key(),
        label_key=EmailContact.get_representation_label_key(),
    )
    cc = wb_filters.ModelMultipleChoiceFilter(
        label=_("CC"),
        queryset=EmailContact.objects.all(),
        endpoint=EmailContact.get_representation_endpoint(),
        value_key=EmailContact.get_representation_value_key(),
        label_key=EmailContact.get_representation_label_key(),
    )
    bcc = wb_filters.ModelMultipleChoiceFilter(
        label=_("BCC"),
        queryset=EmailContact.objects.all(),
        endpoint=EmailContact.get_representation_endpoint(),
        value_key=EmailContact.get_representation_value_key(),
        label_key=EmailContact.get_representation_label_key(),
    )

    def filter_template_name(self, queryset: QuerySet[EmailStep], name, value: str) -> QuerySet[EmailStep]:
        if value:
            return queryset.filter(template__endswith=value)
        return queryset

    class Meta(DecisionStepFilter.Meta):
        model = EmailStep
        fields = DecisionStepFilter.Meta.fields | {
            "subject": ["exact", "icontains"],
        }


class FinishStepFilter(DecisionStepFilter):
    class Meta(DecisionStepFilter.Meta):
        model = FinishStep
        fields = DecisionStepFilter.Meta.fields | {
            "write_preserved_instance": ["exact"],
        }
