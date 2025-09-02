from django.utils.translation import gettext as _

from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

TRANSITION_MENUITEM = MenuItem(
    label=_("Transition"),
    endpoint="wbcore:workflow:transition-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["workflow.view_transition"]
    ),
    add=MenuItem(
        label=_("Create Transition"),
        endpoint="wbcore:workflow:transition-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["workflow.add_transition"]
        ),
    ),
)
