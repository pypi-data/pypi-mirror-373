from django.utils.translation import gettext as _

from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

USER_MENUITEM = MenuItem(
    label=_("Users"),
    endpoint="wbcore:authentication:user-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["authentication.view_user"]
    ),
    add=MenuItem(
        label=_("Create New User"),
        endpoint="wbcore:authentication:user-list",
        permission=ItemPermission(permissions=["authentication.add_user"]),
    ),
)
