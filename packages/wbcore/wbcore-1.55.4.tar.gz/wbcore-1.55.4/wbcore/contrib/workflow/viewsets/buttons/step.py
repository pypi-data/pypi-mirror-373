from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons import ButtonViewConfig


class StepButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self) -> set:
        if workflow_id := self.view.kwargs.get("workflow_id"):
            return {
                bt.DropDownButton(
                    label=_("New Step"),
                    icon=WBIcon.UNFOLD.icon,
                    buttons=(
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:startstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New Start Step"),
                            icon=WBIcon.START.icon,
                            new_mode=True,
                        ),
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:userstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New User Step"),
                            icon=WBIcon.PERSON.icon,
                            new_mode=True,
                        ),
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:decisionstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New Decision Step"),
                            icon=WBIcon.DECISION_STEP.icon,
                            new_mode=True,
                        ),
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:splitstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New Split Step"),
                            icon=WBIcon.SPLIT.icon,
                            new_mode=True,
                        ),
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:joinstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New Join Step"),
                            icon=WBIcon.JOIN_STEP.icon,
                            new_mode=True,
                        ),
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:scriptstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New Script Step"),
                            icon=WBIcon.SCRIPT.icon,
                            new_mode=True,
                        ),
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:emailstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New Email Step"),
                            icon=WBIcon.MAIL.icon,
                            new_mode=True,
                        ),
                        bt.WidgetButton(
                            endpoint=f"{reverse('wbcore:workflow:finishstep-list', args=[], request=self.request)}?workflow={workflow_id}",
                            label=_("New Finish Step"),
                            icon=WBIcon.END.icon,
                            new_mode=True,
                        ),
                    ),
                )
            }
        return set()
