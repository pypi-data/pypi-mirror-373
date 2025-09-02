from rest_framework.request import Request
from rest_framework.reverse import reverse

from wbcore.configs.decorators import register_config


@register_config
def notification_config(request: Request) -> tuple[str, dict[str, str]]:
    return "notifications", {
        "endpoint": reverse("wbcore:notifications:notification-list", request=request),
        "token": reverse("wbcore:notifications:token", request=request),
        "unread_notifications": reverse("wbcore:notifications:notification-unread-count", request=request),
    }
