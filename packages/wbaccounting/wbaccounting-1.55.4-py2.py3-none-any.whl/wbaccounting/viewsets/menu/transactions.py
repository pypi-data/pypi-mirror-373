from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

TRANSACTION_MENUITEM = MenuItem(
    label="Transactions",
    endpoint="wbaccounting:transaction-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbaccounting.view_transaction"]
    ),
    add=MenuItem(
        label="Create Transaction",
        endpoint="wbaccounting:transaction-list",
        permission=ItemPermission(permissions=["wbaccounting.add_transaction"]),
    ),
)
