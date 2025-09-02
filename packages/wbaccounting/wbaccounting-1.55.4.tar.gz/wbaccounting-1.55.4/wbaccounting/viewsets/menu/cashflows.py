from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

CASHFLOW_MENUITEM = MenuItem(
    label="Cashflow",
    endpoint="wbaccounting:futurecashflow-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbaccounting.view_transaction"]
    ),
)
