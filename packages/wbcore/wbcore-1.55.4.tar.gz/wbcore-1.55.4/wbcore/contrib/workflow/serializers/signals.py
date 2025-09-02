from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons.buttons import ActionButton

from ..models.workflow import Workflow


def add_workflow_next_buttons_to_instance(sender, serializer, instance, request, user, **kwargs):
    buttons = []
    for transition_list, process_step in Workflow.get_next_user_step_transitions_for_instance(instance, request.user):
        for transition in transition_list:
            buttons.append(
                ActionButton(
                    method=RequestType.PATCH,
                    identifiers=("workflow:step",),
                    endpoint=f"{reverse('wbcore:workflow:processstep-next', args=[process_step.pk], request=request)}?transition_id={transition.pk}",
                    label=transition.name,
                    icon=transition.icon,
                    description_fields=_("Are you sure you want to activate {}?").format(transition.name),
                    title=transition.name,
                    action_label=_("Activating {}").format(transition.name),
                )
            )
    return buttons
