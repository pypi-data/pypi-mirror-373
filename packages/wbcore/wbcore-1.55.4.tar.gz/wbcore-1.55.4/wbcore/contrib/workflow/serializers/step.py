from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from wbcore import serializers as wb_serializers
from wbcore.contrib.authentication.models import Group, Permission, User
from wbcore.contrib.authentication.serializers import (
    GroupRepresentationSerializer,
    PermissionRepresentationSerializer,
    UserRepresentationSerializer,
)
from wbcore.contrib.directory.models import EmailContact
from wbcore.contrib.directory.serializers import EmailContactRepresentationSerializer
from wbcore.contrib.workflow.models import (
    DecisionStep,
    EmailStep,
    FinishStep,
    JoinStep,
    ScriptStep,
    SplitStep,
    StartStep,
    Step,
    UserStep,
    Workflow,
)
from wbcore.contrib.workflow.serializers.display import DisplayRepresentationSerializer
from wbcore.contrib.workflow.serializers.workflow import (
    WorkflowRepresentationSerializer,
)
from wbcore.contrib.workflow.sites import workflow_site


class StepModelSerializer(wb_serializers.ModelSerializer):
    workflow = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultFromGET("workflow"),
        queryset=Workflow.objects.all(),
        label=_("Workflow"),
    )
    _workflow = WorkflowRepresentationSerializer(source="workflow")
    _permission = PermissionRepresentationSerializer(source="permission")
    casted_endpoint = wb_serializers.SerializerMethodField()

    @wb_serializers.register_resource()
    def transitions_inline(self, instance: Step, request, user) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "transitions": reverse(
                "wbcore:workflow:transition-step-list", args=[instance.pk], request=self.context["request"]
            )
        }

    @wb_serializers.register_resource()
    def process_steps_inline(self, instance: Step, request, user) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "process_steps": reverse(
                "wbcore:workflow:processstep-step-list", args=[instance.pk], request=self.context["request"]
            )
        }

    def get_casted_endpoint(self, obj) -> str:
        if not self.context.get("request"):
            return ""
        return reverse(
            f"{obj.get_casted_step().get_endpoint_basename()}-detail", args=[obj.pk], request=self.context["request"]
        )

    def validate(self, data: dict) -> dict:
        name: str | None = data.get("name", self.instance.name if self.instance else None)
        workflow: Workflow | None = data.get("workflow", self.instance.workflow if self.instance else None)
        code: int | None = data.get("code", self.instance.code if self.instance else None)
        if "status" in data:
            status: str | None = data["status"]
        else:
            status: str | None = self.instance.status if self.instance else None

        if not workflow:
            raise ValidationError({"workflow": _("You need to set a workflow.")})

        step = Step.objects.filter(name=name, workflow=workflow)
        if self.instance:
            step = step.exclude(id=self.instance.id)
        if step.exists():
            raise ValidationError({"name": _("Name has to be unique for the specified workflow.")})

        step = Step.objects.filter(code=code, workflow=workflow)
        if self.instance:
            step = step.exclude(id=self.instance.id)
        if step.exists():
            raise ValidationError({"code": _("Code has to be unique for the specified workflow.")})

        if bool(status) ^ bool(workflow.model):
            raise ValidationError(
                {
                    "status": _(
                        "You need to specify a status for a workflow with an attached model. If no model is attached, do not specify a status."
                    )
                }
            )
        return data

    class Meta:
        model = Step
        fields = (
            "id",
            "name",
            "workflow",
            "_workflow",
            "code",
            "status",
            "step_type",
            "permission",
            "_permission",
            "_additional_resources",
            "casted_endpoint",
        )
        read_only_fields = ("step_type",)


class StepRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:step-detail")

    def get_filter_params(self, request):
        filter_params = {}
        if (view := request.parser_context["view"]) and (workflow := view.workflow):
            filter_params["workflow"] = workflow.id
        return filter_params

    class Meta:
        model = Step
        fields = (
            "id",
            "name",
            "_detail",
        )


class UserStepModelSerializer(StepModelSerializer):
    _assignee = UserRepresentationSerializer(source="assignee")
    _group = GroupRepresentationSerializer(source="group")
    _display = DisplayRepresentationSerializer(source="display")
    assignee_method = wb_serializers.ChoiceField(label=_("Assignee Method"), choices=workflow_site.assignees_choices)

    def validate(self, data: dict) -> dict:
        data = super().validate(data)
        if "assignee" in data:
            assignee: User | None = data["assignee"]
        else:
            assignee: User | None = self.instance.assignee if self.instance else None
        if "assignee_method" in data:
            assignee_method: str | None = data["assignee_method"]
        else:
            assignee_method: str | None = self.instance.assignee_method if self.instance else None
        if "permission" in data:
            permission: Permission | None = data["permission"]
        else:
            permission: Permission | None = self.instance.permission if self.instance else None
        if "group" in data:
            group: Group | None = data["group"]
        else:
            group: Group | None = self.instance.group if self.instance else None

        if assignee_method and assignee_method not in map(lambda x: x[0], workflow_site.assignees_choices):
            raise ValidationError({"assignee_method": _("Assignee method must be one of the available choices.")})

        if assignee:
            if group:
                raise ValidationError({"group": _("Please select either an assignee or a group. Do not select both.")})
            if assignee_method:
                raise ValidationError({"assignee_method": _("Please do not select both an assignee and a method.")})

        if permission and (assignee or group):
            all_assignees = []
            if assignee:
                all_assignees = [assignee]
            elif group:
                if permission in group.permissions.all():
                    return data
                all_assignees = list(group.user_set.all())
            for user in all_assignees:
                if user.is_superuser or permission in user.user_permissions.all():
                    return data
            raise ValidationError(
                {
                    "permission": _(
                        "None of the selected assignees/group members has this permission. Please assign the permission to one of the users or choose a different one."
                    )
                }
            )
        return data

    class Meta(StepModelSerializer.Meta):
        model = UserStep
        fields = StepModelSerializer.Meta.fields + (
            "assignee",
            "_assignee",
            "group",
            "_group",
            "notify_user",
            "display",
            "_display",
            "assignee_method",
            "kwargs",
        )
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class UserStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:userstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = UserStep
        fields = StepRepresentationSerializer.Meta.fields


class StartStepModelSerializer(StepModelSerializer):
    class Meta(StepModelSerializer.Meta):
        model = StartStep
        fields = StepModelSerializer.Meta.fields
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class StartStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:startstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = StartStep
        fields = StepRepresentationSerializer.Meta.fields


class DecisionStepModelSerializer(StepModelSerializer):
    class Meta(StepModelSerializer.Meta):
        model = DecisionStep
        fields = StepModelSerializer.Meta.fields
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class DecisionStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:decisionstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = DecisionStep
        fields = StepRepresentationSerializer.Meta.fields


class SplitStepModelSerializer(StepModelSerializer):
    class Meta(StepModelSerializer.Meta):
        model = SplitStep
        fields = StepModelSerializer.Meta.fields
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class SplitStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:splitstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = SplitStep
        fields = StepRepresentationSerializer.Meta.fields


class JoinStepModelSerializer(StepModelSerializer):
    class Meta(StepModelSerializer.Meta):
        model = JoinStep
        fields = StepModelSerializer.Meta.fields + ("wait_for_all",)
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class JoinStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:joinstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = JoinStep
        fields = StepRepresentationSerializer.Meta.fields


class ScriptStepModelSerializer(StepModelSerializer):
    script = wb_serializers.CodeField(label=_("Script"))

    class Meta(StepModelSerializer.Meta):
        model = ScriptStep
        fields = StepModelSerializer.Meta.fields + ("script",)
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class ScriptStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:scriptstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = ScriptStep
        fields = StepRepresentationSerializer.Meta.fields


class EmailStepModelSerializer(StepModelSerializer):
    _to = EmailContactRepresentationSerializer(source="to", many=True)
    _cc = EmailContactRepresentationSerializer(source="cc", many=True)
    _bcc = EmailContactRepresentationSerializer(source="bcc", many=True)

    def validate(self, data: dict) -> dict:
        to: list[EmailContact] = data.get("to", list(self.instance.to.all()) if self.instance else [])
        if "cc" in data:
            cc: list[EmailContact] = data["cc"]
        else:
            cc: list[EmailContact] = list(self.instance.cc.all()) if self.instance else []
        if "bcc" in data:
            bcc: list[EmailContact] = data["bcc"]
        else:
            bcc: list[EmailContact] = list(self.instance.bcc.all()) if self.instance else []

        to = set(to)
        cc = set(cc)
        bcc = set(bcc)

        if to.intersection(cc):
            raise ValidationError({"cc": _("Duplicate E-Mails in 'To' and 'CC'.")})
        if to.intersection(bcc):
            raise ValidationError({"bcc": _("Duplicate E-Mails in 'To' and 'BCC'.")})
        if cc.intersection(bcc):
            raise ValidationError({"bcc": _("Duplicate E-Mails in 'CC' and 'BCC'.")})
        return super().validate(data)

    class Meta(StepModelSerializer.Meta):
        model = EmailStep
        fields = StepModelSerializer.Meta.fields + ("template", "subject", "to", "_to", "cc", "_cc", "bcc", "_bcc")
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class EmailStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:emailstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = EmailStep
        fields = StepRepresentationSerializer.Meta.fields


class FinishStepModelSerializer(StepModelSerializer):
    def validate(self, data: dict) -> dict:
        data = super().validate(data)
        write_preserved_instance: bool | None = data.get(
            "write_preserved_instance", self.instance.write_preserved_instance if self.instance else None
        )
        workflow: Workflow | None = data.get("workflow", self.instance.workflow if self.instance else None)
        if write_preserved_instance and workflow and not workflow.preserve_instance:
            raise ValidationError(
                {
                    "write_preserved_instance": _(
                        "Cannot write preserved instance without picking the option to preserve it when creating the workflow."
                    )
                }
            )
        return data

    class Meta(StepModelSerializer.Meta):
        model = FinishStep
        fields = StepModelSerializer.Meta.fields + ("write_preserved_instance",)
        read_only_fields = StepModelSerializer.Meta.read_only_fields


class FinishStepRepresentationSerializer(StepRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:finishstep-detail")

    class Meta(StepRepresentationSerializer.Meta):
        model = FinishStep
        fields = StepRepresentationSerializer.Meta.fields
