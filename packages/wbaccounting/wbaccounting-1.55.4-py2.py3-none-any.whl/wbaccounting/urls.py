from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbaccounting.viewsets import (
    BookingEntryModelViewSet,
    BookingEntryRepresentationViewSet,
    ConsolidatedInvoiceViewSet,
    EntryAccountingInformationModelViewSet,
    EntryAccountingInformationRepresentationViewSet,
    FutureCashFlowPandasAPIViewSet,
    FutureCashFlowTransactionsPandasAPIViewSet,
    InvoiceModelViewSet,
    InvoiceRepresentationViewSet,
    InvoiceTypeModelViewSet,
    InvoiceTypeRepresentationViewSet,
    TransactionModelViewSet,
    TransactionRepresentationViewSet,
)

router = WBCoreRouter()
router.register(r"bookingentry", BookingEntryModelViewSet, basename="bookingentry")
router.register(
    r"bookingentryrepresentation", BookingEntryRepresentationViewSet, basename="bookingentryrepresentation"
)
router.register(r"invoice", InvoiceModelViewSet, basename="invoice")
router.register(r"invoicerepresentation", InvoiceRepresentationViewSet, basename="invoicerepresentation")
router.register(r"transaction", TransactionModelViewSet, basename="transaction")
router.register(r"transactionrepresentation", TransactionRepresentationViewSet, basename="transactionrepresentation")
router.register(r"consolidated-invoice", ConsolidatedInvoiceViewSet, basename="consolidated-invoice")
router.register(r"invoicetype", InvoiceTypeModelViewSet, basename="invoicetype")
router.register(r"invoicetyperepresentation", InvoiceTypeRepresentationViewSet, basename="invoicetyperepresentation")
router.register(
    r"entryaccountinginformationrepresentation",
    EntryAccountingInformationRepresentationViewSet,
    basename="entryaccountinginformationrepresentation",
)
router.register(
    r"entryaccountinginformation", EntryAccountingInformationModelViewSet, basename="entryaccountinginformation"
)
router.register(r"futurecashflow", FutureCashFlowPandasAPIViewSet, basename="futurecashflow")
router.register(
    r"futurecashflowtransaction", FutureCashFlowTransactionsPandasAPIViewSet, basename="futurecashflowtransaction"
)

entry_router = WBCoreRouter()

invoice_router = WBCoreRouter()
invoice_router.register(r"bookingentry", BookingEntryModelViewSet, basename="invoice-bookingentry")

entry_accounting_information_router = WBCoreRouter()
entry_accounting_information_router.register(
    r"invoice", InvoiceModelViewSet, basename="entryaccountinginformation-invoice"
)
entry_accounting_information_router.register(
    r"bookingentry", BookingEntryModelViewSet, basename="entryaccountinginformation-bookingentry"
)

booking_entry_router = WBCoreRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("entry/<int:entry_id>/", include(entry_router.urls)),
    path("invoice/<int:invoice_id>/", include(invoice_router.urls)),
    path("bookingentry/<int:booking_entry_id>/", include(booking_entry_router.urls)),
    path(
        "entryaccountinginformation/<int:entry_accounting_information_id>/",
        include(entry_accounting_information_router.urls),
    ),
]
