from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

INVOICETYPE_MENUITEM = MenuItem(
    label="Invoice Types",
    endpoint="wbaccounting:invoicetype-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbaccounting.view_invoicetype"]
    ),
    add=MenuItem(
        label="Create Invoice Type",
        endpoint="wbaccounting:invoicetype-list",
        permission=ItemPermission(permissions=["wbaccounting.add_invoicetype"]),
    ),
)
