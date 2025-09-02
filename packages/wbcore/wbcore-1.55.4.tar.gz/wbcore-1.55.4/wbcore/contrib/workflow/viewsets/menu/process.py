from django.utils.translation import gettext as _

from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

PROCESS_MENUITEM = MenuItem(
    label=_("Process"),
    endpoint="wbcore:workflow:process-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["workflow.view_process"]
    ),
)
PROCESSSTEP_MENUITEM = MenuItem(
    label=_("Process Step"),
    endpoint="wbcore:workflow:processstep-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["workflow.view_processstep"]
    ),
)
