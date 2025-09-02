from django.utils.translation import gettext as _

from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

DATA_MENUITEM = MenuItem(
    label=_("Data"),
    endpoint="wbcore:workflow:data-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["workflow.view_data"]
    ),
    add=MenuItem(
        label=_("Create Data"),
        endpoint="wbcore:workflow:data-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["workflow.add_data"]
        ),
    ),
)
