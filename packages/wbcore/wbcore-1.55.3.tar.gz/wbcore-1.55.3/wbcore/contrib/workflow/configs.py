from rest_framework.request import Request
from rest_framework.reverse import reverse

from wbcore.configs.decorators import register_config


@register_config
def assigned_workflow_steps(request: Request) -> tuple[str, dict[str, str]]:
    return "workflow", {
        "endpoint": reverse("wbcore:workflow:processstep-assigned-list", request=request),
    }
