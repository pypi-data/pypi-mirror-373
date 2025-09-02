from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from wbcore import serializers as wb_serializers
from wbcore.contrib.workflow.models import Step, Transition
from wbcore.contrib.workflow.serializers.step import StepRepresentationSerializer


class TransitionModelSerializer(wb_serializers.ModelSerializer):
    _from_step = StepRepresentationSerializer(source="from_step", required=False)

    _to_step = StepRepresentationSerializer(source="to_step", required=False)

    @wb_serializers.register_resource()
    def conditions_inline(self, instance: Transition, request, user) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "conditions": reverse(
                "wbcore:workflow:condition-transition-list", args=[instance.pk], request=self.context["request"]
            )
        }

    def validate(self, data: dict) -> dict:
        from_step: Step | None = data.get("from_step", self.instance.from_step if self.instance else None)
        to_step: Step | None = data.get("to_step", self.instance.to_step if self.instance else None)
        name: str | None = data.get("name", self.instance.name if self.instance else None)

        if to_step:
            if to_step.step_type == Step.StepType.STARTSTEP:
                raise ValidationError({"to_step": _("Cannot set a start step at the end of a transition.")})

            if from_step:
                if not from_step.workflow == to_step.workflow:
                    raise ValidationError({"to_step": _("All steps need to belong to the same workflow.")})
                if from_step == to_step:
                    raise ValidationError(
                        {
                            "to_step": _(
                                "Cannot transition to the same step. Please set different preceding and succeeding steps."
                            )
                        }
                    )
        if from_step:
            if from_step.step_type == Step.StepType.FINISHSTEP:
                raise ValidationError({"from_step": _("Cannot set a finishing step at the start of a transition.")})

        transition = Transition.objects.filter(name=name, to_step=to_step)
        if self.instance:
            transition = transition.exclude(id=self.instance.id)
        if transition.exists():
            raise ValidationError(
                {"name": _("A transition with this name to the same succeeding step already exists.")}
            )
        return data

    class Meta:
        model = Transition
        fields = (
            "id",
            "name",
            "from_step",
            "_from_step",
            "to_step",
            "_to_step",
            "icon",
            "_additional_resources",
        )


class TransitionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:transition-detail")

    class Meta:
        model = Transition
        fields = (
            "id",
            "name",
            "_detail",
        )
