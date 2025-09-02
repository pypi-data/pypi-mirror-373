from django.utils.translation import gettext as _

from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

WORKFLOW_MENUITEM = MenuItem(
    label=_("Workflow"),
    endpoint="wbcore:workflow:workflow-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["workflow.view_workflow"]
    ),
    add=MenuItem(
        label=_("Create Workflow"),
        endpoint="wbcore:workflow:workflow-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["workflow.add_workflow"]
        ),
    ),
)
