from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display import create_simple_display
from wbcore.serializers import Serializer


class DocumentTypeButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(
                key="list_of_children",
                label=_("All Children"),
                icon=WBIcon.ENUMERATION.icon,
            ),
            bt.WidgetButton(
                key="list_of_documents",
                label=_("All Documents"),
                icon=WBIcon.DOCUMENT.icon,
            ),
        }


class DocumentButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        class SendMailSerializer(Serializer):
            to_email = wb_serializers.CharField(default=self.request.user.email, label=gettext_lazy("Recipient"))

            class Meta:
                fields = "to_email"

        return {
            bt.HyperlinkButton(key="download_file", label=_("Download"), icon=WBIcon.LINK.icon),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcore:documents:document",),
                key="send_mail",
                icon=WBIcon.SEND.icon,
                label=_("Send Mail"),
                description_fields=_("""<p>Send this document as mail?</p>"""),
                action_label=_("Sending Mail"),
                title=_("Send document as mail"),
                serializer=SendMailSerializer,
                instance_display=create_simple_display([["to_email"]]),
            ),
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
