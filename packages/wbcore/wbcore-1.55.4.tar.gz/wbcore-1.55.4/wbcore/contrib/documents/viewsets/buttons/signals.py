from django.dispatch import receiver
from rest_framework.reverse import reverse

from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.signals.instance_buttons import add_extra_button


@receiver(add_extra_button)
def add_extra_documents(sender, instance, request, view, pk=None, **kwargs):
    if instance and pk and view:
        content_type = view.get_content_type()
        endpoint = reverse("wbcore:documents:document_content_object", args=[content_type.id, pk], request=request)
        return bt.WidgetButton(endpoint=endpoint, label="Documents", icon=WBIcon.DOCUMENT_WITH_ATTACHMENT.icon)
