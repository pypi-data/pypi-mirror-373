from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework.request import Request

from wbcore.configs.decorators import register_config


@register_config
def authentication_config(request: Request) -> tuple[str, dict]:
    return "authentication", import_string(settings.WBCORE_DEFAULT_AUTH_CONFIG)(request)
