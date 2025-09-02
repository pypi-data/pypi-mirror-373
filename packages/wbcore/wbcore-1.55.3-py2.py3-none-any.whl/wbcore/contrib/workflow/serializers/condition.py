from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from wbcore import serializers as wb_serializers
from wbcore.contrib.workflow.models import Condition, Transition
from wbcore.contrib.workflow.serializers.transition import (
    TransitionRepresentationSerializer,
)


class ConditionModelSerializer(wb_serializers.ModelSerializer):
    transition = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultFromGET("transition"),
        queryset=Transition.objects.all(),
        label=_("Transition"),
    )
    _transition = TransitionRepresentationSerializer(source="transition")

    def validate(self, data: dict) -> dict:
        operator: str | None = data.get("operator", self.instance.operator if self.instance else None)
        expected_value: str | None = data.get(
            "expected_value", self.instance.expected_value if self.instance else None
        )
        attribute_name: str | None = data.get(
            "attribute_name", self.instance.attribute_name if self.instance else None
        )
        transition: Transition | None = data.get("transition", self.instance.transition if self.instance else None)

        condition = Condition.objects.filter(
            operator=operator, expected_value=expected_value, attribute_name=attribute_name, transition=transition
        )
        if self.instance:
            condition = condition.exclude(id=self.instance.id)
        if condition.exists():
            raise ValidationError(
                {"non_field_errors": _("This condition for the selected transition already exists.")}
            )

        if transition and not (transition.to_step.workflow.model or transition.to_step.workflow.attached_data.all()):
            raise ValidationError({"transition": _("Related workflow needs to have a model or data attached.")})

        return data

    class Meta:
        model = Condition
        fields = (
            "id",
            "transition",
            "_transition",
            "attribute_name",
            "operator",
            "expected_value",
            "negate_operator",
        )


class ConditionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcore:workflow:transition-detail")

    class Meta:
        model = Condition
        fields = (
            "id",
            "_detail",
        )
