from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

BOOKINGENTRY_MENUITEM = MenuItem(
    label="Bookings",
    endpoint="wbaccounting:bookingentry-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbaccounting.view_bookingentry"]
    ),
    add=MenuItem(
        label="Create Booking",
        endpoint="wbaccounting:bookingentry-list",
        permission=ItemPermission(permissions=["wbaccounting.add_bookingentry"]),
    ),
)
