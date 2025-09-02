from django.db import models
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from wbcore.contrib.workflow.models.data import Data
from wbcore.models import WBModel


class Condition(WBModel):
    """A condition that needs to be satisfied in order to make the transition to the next workflow step"""

    class Operator(models.TextChoices):
        LT = "<", _("Less Than")
        LTE = "<=", _("Less Than or Equal")
        EQ = "==", _("Equal")
        GTE = ">=", _("Greater Than or Equal")
        GT = ">", _("Greater Than")

    transition = models.ForeignKey(
        to="workflow.Transition",
        verbose_name=_("Transition"),
        on_delete=models.CASCADE,
        related_name="associated_conditions",
    )
    attribute_name = models.CharField(
        max_length=64,
        verbose_name=_("Attribute Name"),
        help_text=_(
            "The name of the attribute on the attached instance. Its value will be evaluated against the condition."
        ),
    )
    operator = models.CharField(max_length=64, choices=Operator.choices, verbose_name=_("Operator"))
    expected_value = models.CharField(
        max_length=64,
        verbose_name=_("Expected Value"),
        help_text=_("The expected value of the attribute that will satisfy the condition."),
    )
    negate_operator = models.BooleanField(default=False, verbose_name=_("Negate Operator"))

    @property
    def errors(self):
        if not hasattr(self, "_errors"):
            raise ValueError(_('Please call "satisfied" before accessing errors'))
        return self._errors

    def satisfied(self, instance) -> bool:
        """Checks if the condition is satisfied for the provided instance

        Args:
            instance: The instance that should be checked.

        Returns:
            bool: True if the condition satisfies the provided instance, False otherwise
        """

        self._errors = []
        try:
            attribute_value = getattr(instance, self.attribute_name)
            try:
                # We need to cast the expected value to the type of the attached instance's field.
                # We technically do not need to do this for attached data as the data value is already a string, same as the expected value.
                casted_expected_value = Data.cast_value_from_target_object(attribute_value, self.expected_value)

                evaluated_condition = False
                if self.operator == self.Operator.EQ:
                    evaluated_condition = attribute_value == casted_expected_value
                elif self.operator == self.Operator.GT:
                    evaluated_condition = attribute_value > casted_expected_value
                elif self.operator == self.Operator.GTE:
                    evaluated_condition = attribute_value >= casted_expected_value
                elif self.operator == self.Operator.LT:
                    evaluated_condition = attribute_value < casted_expected_value
                elif self.operator == self.Operator.LTE:
                    evaluated_condition = attribute_value <= casted_expected_value

                if self.negate_operator:
                    return not evaluated_condition
                return evaluated_condition

            except ValueError:
                self._errors.append(
                    gettext(
                        "Condition error: Type of attribute ({}) and expected value ({}) uncompatible or wrong datetime format!"
                    ).format(type(attribute_value), self.expected_value)
                )
                return False
        except AttributeError:
            self._errors.append(
                gettext("Condition error: No attribute called {} found in attached instance or data!").format(
                    self.attribute_name
                )
            )
        return False

    def __str__(self) -> str:
        if self.negate_operator:
            return _("{} not {} {}").format(self.attribute_name, self.operator, self.expected_value)
        return f"{self.attribute_name} {self.operator} {self.expected_value}"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:workflow:condition"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:workflow:conditionrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{transition}}: {{attribute_name}} {{negate_operator}} {{operator}} {{expected_value}}"

    class Meta:
        verbose_name = _("Condition")
        verbose_name_plural = _("Conditions")
        constraints = [
            models.UniqueConstraint(
                fields=["transition", "attribute_name", "operator", "negate_operator", "expected_value"],
                name="unique_transition_attribute_name_operator_negate_expected_value",
            ),
        ]
