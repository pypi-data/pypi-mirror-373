from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from wbcore.contrib.icons import WBIcon
from wbcore.contrib.icons.models import IconField
from wbcore.contrib.workflow.models import ProcessStep
from wbcore.models import WBModel


class Transition(WBModel):
    """A transition from one workflow step to the next one."""

    name = models.CharField(max_length=128, verbose_name=_("Name"))
    from_step = models.ForeignKey(
        to="workflow.Step",
        on_delete=CASCADE,
        verbose_name=_("From"),
        related_name="outgoing_transitions",
    )
    to_step = models.ForeignKey(
        to="workflow.Step", on_delete=CASCADE, verbose_name=_("To"), related_name="incoming_transitions"
    )
    icon = IconField(
        max_length=128,
        unique=False,
        verbose_name=_("Icon"),
        blank=False,
        null=False,
        default=WBIcon.START.icon,
    )

    def all_conditions_satisfied(self, process_step: ProcessStep) -> bool:
        if condition_qs := self.associated_conditions.all():
            if instance := process_step.get_instance():
                for cond in condition_qs:
                    if not cond.satisfied(instance):
                        if errors := cond.errors:
                            process_step.step.get_casted_step().set_failed(process_step, errors[0])
                        return False
                return True
            process_step.step.get_casted_step().set_failed(process_step, gettext("No instance or data attached!"))
            return False
        return True

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:workflow:transition"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:workflow:transitionrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    class Meta:
        verbose_name = _("Transition")
        verbose_name_plural = _("Transitions")
        constraints = [
            models.UniqueConstraint(fields=["name", "to_step"], name="unique_name_to_step"),
        ]
