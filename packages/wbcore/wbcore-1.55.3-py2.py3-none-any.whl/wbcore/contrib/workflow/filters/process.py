from django.utils.translation import gettext_lazy as _

from wbcore import filters as wb_filters
from wbcore.contrib.authentication.models import Group, Permission, User
from wbcore.contrib.workflow.models import Process, ProcessStep, Step, Workflow


class ProcessWorkflowFilter(wb_filters.FilterSet):
    started__lte = wb_filters.DateTimeFilter(
        label=_("Started Before/On"),
        lookup_expr="lte",
        field_name="started",
    )
    started__gte = wb_filters.DateTimeFilter(
        label=_("Started After/On"),
        lookup_expr="gte",
        field_name="started",
    )
    finished__lte = wb_filters.DateTimeFilter(
        label=_("Finished Before/On"),
        lookup_expr="lte",
        field_name="finished",
    )
    finished__gte = wb_filters.DateTimeFilter(
        label=_("Finished After/On"),
        lookup_expr="gte",
        field_name="finished",
    )
    id = wb_filters.CharFilter(label=_("UUID"))
    state = wb_filters.MultipleChoiceFilter(choices=Process.ProcessState.choices, label=_("States"))

    class Meta:
        model = Process
        fields = {}


class ProcessFilter(ProcessWorkflowFilter):
    workflow = wb_filters.ModelMultipleChoiceFilter(
        label=_("Workflows"),
        queryset=Workflow.objects.all(),
        endpoint=Workflow.get_representation_endpoint(),
        value_key=Workflow.get_representation_value_key(),
        label_key=Workflow.get_representation_label_key(),
    )

    class Meta(ProcessWorkflowFilter.Meta):
        model = Process
        fields = ProcessWorkflowFilter.Meta.fields


class ProcessStepBaseFilter(ProcessWorkflowFilter):
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
    permission = wb_filters.ModelMultipleChoiceFilter(
        label=_("Permissions"),
        queryset=Permission.objects.all(),
        endpoint=Permission.get_representation_endpoint(),
        value_key=Permission.get_representation_value_key(),
        label_key=Permission.get_representation_label_key(),
    )

    class Meta:
        model = ProcessStep
        fields = {
            "status": ["exact", "icontains"],
            "error_message": ["exact", "icontains"],
        }


class ProcessStepProcessFilter(ProcessStepBaseFilter):
    step = wb_filters.ModelMultipleChoiceFilter(
        label=_("Steps"),
        queryset=Step.objects.all(),
        endpoint=Step.get_representation_endpoint(),
        value_key=Step.get_representation_value_key(),
        label_key=Step.get_representation_label_key(),
    )

    class Meta(ProcessStepBaseFilter.Meta):
        model = ProcessStep
        fields = ProcessStepBaseFilter.Meta.fields


class ProcessStepStepFilter(ProcessStepBaseFilter):
    process = wb_filters.ModelMultipleChoiceFilter(
        label=_("Processes"),
        queryset=Process.objects.all(),
        endpoint=Process.get_representation_endpoint(),
        value_key=Process.get_representation_value_key(),
        label_key=Process.get_representation_label_key(),
    )

    class Meta(ProcessStepBaseFilter.Meta):
        model = ProcessStep
        fields = ProcessStepBaseFilter.Meta.fields


class ProcessStepFilter(ProcessStepProcessFilter, ProcessStepStepFilter):
    class Meta(ProcessStepBaseFilter.Meta):
        model = ProcessStep
        fields = ProcessStepBaseFilter.Meta.fields


class AssignedProcessStepFilter(wb_filters.FilterSet):
    step = wb_filters.ModelMultipleChoiceFilter(
        label=_("Steps"),
        queryset=Step.objects.all(),
        endpoint=Step.get_representation_endpoint(),
        value_key=Step.get_representation_value_key(),
        label_key=Step.get_representation_label_key(),
    )
    started__lte = wb_filters.DateTimeFilter(
        label=_("Started Before/On"),
        lookup_expr="lte",
        field_name="started",
    )
    started__gte = wb_filters.DateTimeFilter(
        label=_("Started After/On"),
        lookup_expr="gte",
        field_name="started",
    )
    finished__lte = wb_filters.DateTimeFilter(
        label=_("Finished Before/On"),
        lookup_expr="lte",
        field_name="finished",
    )
    finished__gte = wb_filters.DateTimeFilter(
        label=_("Finished After/On"),
        lookup_expr="gte",
        field_name="finished",
    )
    group = wb_filters.ModelMultipleChoiceFilter(
        label=_("Groups"),
        queryset=Group.objects.all(),
        endpoint=Group.get_representation_endpoint(),
        value_key=Group.get_representation_value_key(),
        label_key=Group.get_representation_label_key(),
    )
    permission = wb_filters.ModelMultipleChoiceFilter(
        label=_("Permissions"),
        queryset=Permission.objects.all(),
        endpoint=Permission.get_representation_endpoint(),
        value_key=Permission.get_representation_value_key(),
        label_key=Permission.get_representation_label_key(),
    )
    workflow_name = wb_filters.CharFilter(label=_("Workflow"), lookup_expr="icontains")
    attached_model = wb_filters.CharFilter(label=_("Attached Model"), lookup_expr="icontains")

    class Meta:
        model = ProcessStep
        fields = {
            "status": ["exact", "icontains"],
        }
