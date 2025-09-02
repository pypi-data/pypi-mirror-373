from django.db.models import QuerySet
from wbcore import viewsets

from wbaccounting.models import BookingEntry
from wbaccounting.serializers import (
    BookingEntryModelSerializer,
    BookingEntryRepresentationSerializer,
)
from wbaccounting.viewsets.buttons import BookingEntryButtonConfig
from wbaccounting.viewsets.display import BookingEntryDisplayConfig
from wbaccounting.viewsets.titles import BookingEntryTitleConfig


class BookingEntryRepresentationViewSet(viewsets.RepresentationViewSet):
    search_fields = ["counterparty__computed_str", "title", "currency__key"]
    ordering_fields = ["title"]
    ordering = ["title"]
    serializer_class = BookingEntryRepresentationSerializer
    queryset = BookingEntry.objects.all()

    def get_queryset(self):
        return BookingEntry.objects.filter_for_user(self.request.user)


class BookingEntryModelViewSet(viewsets.ModelViewSet):
    filterset_fields = {
        "counterparty": ["exact"],
        "booking_date": ["gte", "exact", "lte"],
        "reference_date": ["gte", "exact", "lte"],
    }
    search_fields = ["counterparty__computed_str", "title", "currency__key"]
    ordering_fields = (
        "counterparty__computed_str",
        "booking_date",
        "gross_value",
        "net_value",
        "reference_date",
    )
    ordering = ["-booking_date"]

    serializer_class = BookingEntryModelSerializer
    queryset = BookingEntry.objects.all()

    button_config_class = BookingEntryButtonConfig
    display_config_class = BookingEntryDisplayConfig
    title_config_class = BookingEntryTitleConfig

    def get_queryset(self) -> QuerySet[BookingEntry]:
        booking_entries = BookingEntry.objects.filter_for_user(self.request.user)

        if eai_id := self.kwargs.get("entry_accounting_information_id", None):
            booking_entries = booking_entries.filter(counterparty__entry_accounting_information__id=eai_id)

        if invoice_id := self.kwargs.get("invoice_id", None):
            booking_entries = booking_entries.filter(invoice_id=invoice_id)

        return booking_entries.select_related(
            "counterparty",
            "invoice",
            "currency",
            "invoice__invoice_currency",
        )
