from wbcore.menus import ItemPermission, MenuItem

CURRENCY_MENUITEM = MenuItem(
    label="Currency",
    endpoint="wbcore:currency:currency-list",
    add=MenuItem(label="New Currency", endpoint="wbcore:currency:currency-list"),
    permission=ItemPermission(method=lambda request: request.user.is_staff),
)
