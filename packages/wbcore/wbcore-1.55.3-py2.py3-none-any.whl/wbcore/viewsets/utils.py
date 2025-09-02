from dataclasses import dataclass

from django.utils.translation import gettext as _
from rest_framework.response import Response

from wbcore.metadata.configs.buttons import ButtonConfig
from wbcore.metadata.configs.display.instance_display import Display


@dataclass
class PreAction:
    message: str
    instance_display: Display | None = None
    confirm_config: ButtonConfig = ButtonConfig(label=_("Confirm"), title=_("Confirm"))
    cancel_config: ButtonConfig = ButtonConfig(label=_("Cancel"), title=_("Cancel"))

    def to_response(self):
        response_dict = {
            "message": self.message,
            "confirm_config": dict(self.confirm_config),
            "cancel_config": dict(self.cancel_config),
        }

        if self.instance_display:
            response_dict["display"] = self.instance_display.serialize()

        return Response(response_dict)
