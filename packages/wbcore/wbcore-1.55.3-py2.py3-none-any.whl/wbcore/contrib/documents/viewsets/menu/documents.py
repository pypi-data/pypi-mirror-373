from django.utils.translation import gettext as _

from wbcore.menus import ItemPermission, MenuItem

DMS_MENUITEM = MenuItem(
    label=_("Documents"),
    endpoint="wbcore:documents:document-list",
    permission=ItemPermission(permissions=["documents.view_document"]),
    add=MenuItem(
        label=_("Create New Document"),
        endpoint="wbcore:documents:document-list",
        permission=ItemPermission(permissions=["documents.add_document"]),
    ),
)

DOCUMENT_TYPE_MENUITEM = MenuItem(
    label=_("Document Types"),
    endpoint="wbcore:documents:documenttype-list",
    permission=ItemPermission(permissions=["documents.view_documenttype"]),
    add=MenuItem(
        label=_("Create New Document Type"),
        endpoint="wbcore:documents:documenttype-list",
        permission=ItemPermission(permissions=["documents.add_documenttype"]),
    ),
)
