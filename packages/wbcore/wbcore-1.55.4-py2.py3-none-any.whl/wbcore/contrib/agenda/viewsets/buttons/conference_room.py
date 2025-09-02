from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class BuildingButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if not self.view.kwargs.get("pk", None):
            base_url = reverse("wbcore:directory:addresscontact-list", args=[], request=self.request)

            return {
                bt.WidgetButton(
                    endpoint=base_url,
                    label=_("New Address"),
                    icon="add_location",
                    new_mode=True,
                )
            }
        return {}
