from django.utils.translation import gettext as _

from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

CONDITION_MENUITEM = MenuItem(
    label=_("Condition"),
    endpoint="wbcore:workflow:condition-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["workflow.view_condition"]
    ),
    add=MenuItem(
        label=_("Create Condition"),
        endpoint="wbcore:workflow:condition-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["workflow.add_condition"]
        ),
    ),
)
