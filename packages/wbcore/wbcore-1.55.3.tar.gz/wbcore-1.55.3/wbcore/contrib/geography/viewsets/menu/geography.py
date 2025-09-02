from wbcore.menus import ItemPermission, MenuItem

GEOGRAPHY_MENUITEM = MenuItem(
    label="Geography",
    endpoint="geography:geography-list",
    add=MenuItem(label="New Geography", endpoint="geography:geography-list"),
    permission=ItemPermission(method=lambda request: request.user.is_staff),
)
