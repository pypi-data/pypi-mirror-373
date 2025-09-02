from rest_framework.request import Request
from rest_framework.reverse import reverse

from wbcore.configs.decorators import register_config


@register_config
def gleap_config(request: Request) -> tuple[str, dict[str, str]]:
    return "gleap", {
        "user_identity_endpoint": reverse("gleap:user_identity", request=request),
        "api_token": reverse("gleap:api_token", request=request),
    }
