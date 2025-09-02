from rest_framework.permissions import IsAuthenticated


class IsInvoiceAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm("wbaccounting.administrate_invoice")


class CanGenerateBookingEntry(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm("wbaccounting.can_generate_booking_entries")


class CanGenerateInvoice(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm("wbaccounting.can_generate_invoice")
