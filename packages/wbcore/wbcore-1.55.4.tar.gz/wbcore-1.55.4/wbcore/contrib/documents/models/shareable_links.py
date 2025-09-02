from typing import Any, Dict, Optional
from uuid import uuid4

from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse

from wbcore.models import WBModel


class ShareableLink(WBModel):
    document = models.ForeignKey(to="documents.Document", related_name="shareable_links", on_delete=models.CASCADE)

    valid_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Valid Until"))
    one_time_link = models.BooleanField(default=False, verbose_name=_("One Time Link"))
    manual_invalid = models.BooleanField(default=False)

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    def __str__(self) -> str:
        return f"{self.document}: {self.valid_until}"

    def is_valid(self):
        return (
            not self.manual_invalid
            and (self.valid_until is None or self.valid_until > timezone.now())
            and (not self.one_time_link or self.accesses.count() < 1)
        )

    @property
    def link(self):
        endpoint = reverse("wbcore:documents:download", kwargs={"uuid": self.uuid})
        return "https://%s%s" % (Site.objects.get_current().domain, endpoint)

    def access(self, metadata: Optional[Dict[str, Any]] = None):
        if not metadata:
            metadata = dict()
        ShareableLinkAccess.objects.create(shareable_link=self, metadata=metadata)

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:documents:link"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:documents:linkrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{uuid}}"

    class Meta:
        verbose_name = _("Shareable Link")
        verbose_name_plural = _("Shareable Links")


class ShareableLinkAccess(WBModel):
    shareable_link = models.ForeignKey(to="documents.ShareableLink", related_name="accesses", on_delete=models.PROTECT)

    metadata = models.JSONField(default=dict)

    accessed = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.shareable_link}: {self.accessed}"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:documents:linkaccess"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:documents:linkaccessrepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{id}}"

    class Meta:
        verbose_name = _("Shareable Link Access")
        verbose_name_plural = _("Shareable Link Accesses")
