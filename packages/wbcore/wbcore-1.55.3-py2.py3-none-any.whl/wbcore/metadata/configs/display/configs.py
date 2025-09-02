from rest_framework.request import Request
from rest_framework.reverse import reverse

from wbcore.configs.decorators import register_config


@register_config
def preset_config(request: Request) -> tuple[str, dict[str, str]]:
    """We return the wbcore:preset endpoint. We have to add a dummy arg and remove it immediately, since this endpoint only supports endpoints with arguments"""

    dummy_arg = "empty"
    arg_len = len(dummy_arg) + 1  # +1 to account for the second trailing slash
    endpoint = reverse("wbcore:preset", args=[dummy_arg], request=request)
    endpoint = endpoint[: -1 * arg_len]

    return "presets", {"endpoint": endpoint}
