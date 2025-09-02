from django.db import models
from django.utils.translation import gettext_lazy as _

from wbcore.models import WBModel


class Display(WBModel):
    """A user modifiable display config that can be used to display process steps."""

    grid_template_areas = models.JSONField(verbose_name=_("Grid Fields"))
    name = models.CharField(max_length=128, verbose_name=_("Name"), unique=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:workflow:display"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:workflow:displayrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    class Meta:
        verbose_name = _("Display")
        verbose_name_plural = _("Displays")
