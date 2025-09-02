from rest_framework.request import Request
from rest_framework.reverse import reverse

from wbcore.configs.decorators import register_config


@register_config
def profile_config(request: Request) -> tuple[str, str]:
    return "profile", reverse("wbcore:profile", request=request)
