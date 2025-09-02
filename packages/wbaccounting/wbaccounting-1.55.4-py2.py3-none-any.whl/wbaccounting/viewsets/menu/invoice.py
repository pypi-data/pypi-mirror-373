from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

INVOICE_MENUITEM = MenuItem(
    label="Invoices",
    endpoint="wbaccounting:invoice-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbaccounting.view_invoice"]
    ),
    add=MenuItem(
        label="Create Invoice",
        endpoint="wbaccounting:invoice-list",
        permission=ItemPermission(permissions=["wbaccounting.add_invoice"]),
    ),
)
