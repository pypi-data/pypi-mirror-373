from wbcore.menus import ItemPermission, MenuItem

TAG_MENUITEM = MenuItem(
    label="Tag",
    endpoint="wbcore:tags:tag-list",
    add=MenuItem(label="New Tag", endpoint="wbcore:tags:tag-list"),
    permission=ItemPermission(permissions=["tags.change_tag"]),
)

TAGGROUP_MENUITEM = MenuItem(
    label="Tag Group",
    endpoint="wbcore:tags:taggroup-list",
    add=MenuItem(label="New Tag Group", endpoint="wbcore:tags:taggroup-list"),
    permission=ItemPermission(permissions=["tags.change_taggroup"]),
)
