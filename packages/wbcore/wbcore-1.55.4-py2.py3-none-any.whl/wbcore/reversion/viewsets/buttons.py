from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from rest_framework.reverse import reverse
from reversion import is_registered
from reversion.models import Version

from wbcore import serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display import create_simple_display
from wbcore.signals.instance_buttons import add_extra_button

from ..serializers import VersionRepresentationSerializer


class VersionButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            if (content_type_id := self.view.request.GET.get("content_type", None)) and (
                object_id := self.view.request.GET.get("object_id", None)
            ):
                content_type = ContentType.objects.get(id=content_type_id)
                return {
                    bt.HyperlinkButton(
                        label=_("Compare in Admin"),
                        endpoint=f"/admin/{content_type.app_label}/{content_type.model}/{object_id}/history/",
                    )
                }
        return set()

    def get_custom_list_instance_buttons(self):
        if (content_type_id := self.view.request.GET.get("content_type", None)) and (
            object_id := self.view.request.GET.get("object_id", None)
        ):
            content_type = ContentType.objects.get(id=content_type_id)
            obj = content_type.model_class().objects.get(id=object_id)

            class CompareSerializer(serializers.Serializer):
                compare_with = serializers.PrimaryKeyRelatedField(
                    label=gettext_lazy("Start"), queryset=Version.objects.get_for_object(obj)
                )
                _compare_with = VersionRepresentationSerializer(
                    source="compare_with", filter_params={"content_type": content_type_id, "object_id": object_id}
                )

            return {
                bt.ActionButton(
                    method=RequestType.GET,
                    identifiers=("{0.app_label}:{0.model}".format(content_type),),
                    key="revert",
                    label=_("Revert"),
                    icon=WBIcon.SYNCHRONIZE.icon,
                    description_fields=_(
                        """
                    <p>Revert object to this version</p>
                    """
                    ),
                    action_label=_("Reverting"),
                    title=_("Revert"),
                ),
                bt.ActionButton(
                    method=RequestType.GET,
                    identifiers=("wbcore:version",),
                    key="compare_with",
                    label=_("Compare With"),
                    icon=WBIcon.DATA_GRID.icon,
                    description_fields=_(
                        """
                    <p>Compare this version with another version</p>
                    """
                    ),
                    serializer=CompareSerializer,
                    action_label=_("Comparing"),
                    title=_("Compare With"),
                    instance_display=create_simple_display([["compare_with"]]),
                ),
            }
        return set()

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()


@receiver(add_extra_button)
def add_reversion_documents(sender, instance, request, view, pk=None, **kwargs):
    if instance and pk and view and is_registered(view.get_model()):
        content_type = view.get_content_type()
        endpoint = (
            f'{reverse("wbcore:version-list", args=[], request=request)}?content_type={content_type.id}&object_id={pk}'
        )
        return bt.WidgetButton(endpoint=endpoint, label="History", icon=WBIcon.HISTORY.icon)
