from django.dispatch import receiver
from django.urls import resolve
from rest_framework.request import Request
from rest_framework.reverse import reverse

from wbcore import serializers
from wbcore.contrib.icons.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.metadata.configs.buttons.enums import ButtonDefaultColor
from wbcore.metadata.configs.display.instance_display.shortcuts import create_simple_display
from wbcore.signals.instance_buttons import add_extra_button


class AutoTranslateSerializer(serializers.Serializer):
    override_existing_data = serializers.BooleanField(default=False)


@receiver(add_extra_button)
def add_auto_translate_action_button(sender, instance, request: Request, view, pk=None, **kwargs):
    if instance and pk and view and hasattr(view, "auto_translate"):
        url = reverse(resolve(request.path).view_name.replace("detail", "auto-translate"), args=[pk], request=request)
        return ActionButton(
            method=RequestType.POST,
            icon=WBIcon.DEAL.icon,
            color=ButtonDefaultColor.SUCCESS,
            endpoint=url,
            label="Auto Translate",
            action_label="Auto Translate",
            description_fields="You will automatically translate all fields available for translation.",
            serializer=AutoTranslateSerializer,
            instance_display=create_simple_display([["override_existing_data"]]),
        )
