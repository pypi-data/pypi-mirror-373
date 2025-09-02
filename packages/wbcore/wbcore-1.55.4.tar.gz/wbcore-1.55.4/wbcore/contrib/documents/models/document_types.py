from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from wbcore.models import WBModel
from wbcore.utils.models import ComplexToStringMixin


class DocumentType(ComplexToStringMixin, WBModel, MPTTModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children", verbose_name=_("Parent")
    )
    system_key = models.CharField(max_length=255, null=True, blank=True)

    def compute_str(self):
        if self.id:
            ancestors_names = self.get_ancestors(ascending=False, include_self=True).values_list("name", flat=True)
            return " -> ".join(list(ancestors_names))
        return self.name

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:documents:documenttype"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:documents:documenttyperepresentation-list"

    class Meta:
        verbose_name = _("Document Type")
        verbose_name_plural = _("Document Types")
