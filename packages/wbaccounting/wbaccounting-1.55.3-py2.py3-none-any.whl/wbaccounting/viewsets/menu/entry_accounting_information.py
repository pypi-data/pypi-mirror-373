from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

ENTRYACCOUNTINGINFORMATION_MENUITEM = MenuItem(
    label="Counterparties",
    endpoint="wbaccounting:entryaccountinginformation-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbaccounting.view_entryaccountinginformation"],
    ),
)
