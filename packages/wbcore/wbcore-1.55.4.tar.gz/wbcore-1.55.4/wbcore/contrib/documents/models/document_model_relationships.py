from contextlib import suppress

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from wbcore.utils.models import PrimaryMixin


class DocumentModelRelationship(PrimaryMixin):
    PRIMARY_ATTR_FIELDS = ["content_type", "object_id"]
    document = models.ForeignKey(to="documents.Document", related_name="relationships", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    content_object_repr = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.document.name} -> {self.content_object}"

    def delete(self, no_deletion=True, **kwargs):
        super().delete(no_deletion=False, **kwargs)

    def save(self, *args, **kwargs):
        with suppress(AttributeError):
            self.content_object_repr = str(self.content_object)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Document Model Relationship")
        verbose_name_plural = _("Document Model Relationships")

        indexes = [models.Index(fields=["content_type", "object_id"])]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"],
                name="unique_primary_relationship",
                condition=models.Q(primary=True),
            ),
            models.UniqueConstraint(fields=["document", "content_type", "object_id"], name="unique_relationship"),
        ]

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcore:documents:documentmodelrelationship"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    # @classmethod
    # def get_representation_endpoint(cls):
    #     return "wbcore:documents:documentmodelrelationshiprepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{content_type}}: {{content_object_repr}}"
