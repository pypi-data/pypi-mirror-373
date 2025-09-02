from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse

from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.identifiers import IdentifierViewConfig


def add_clear_cache_button(sender, instance, request, view, pk=None, **kwargs):
    if request.user.is_superuser and not instance:
        cache_key = view._get_cache_key()
        identifier = IdentifierViewConfig(view, request, instance=instance).get_metadata()
        return bt.ActionButton(
            method=RequestType.PATCH,
            icon=WBIcon.DOWNLOAD.icon,
            identifiers=(identifier,),
            endpoint=reverse("wbcore:clear_cache", args=[cache_key], request=request),
            action_label=_("Clear Cache"),
            title=_("Clear Cache"),
            label=_("Clear Cache"),
            description_fields=_("Clear Cache"),
        )
