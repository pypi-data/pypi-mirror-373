from datetime import date

from django.db.models import Exists, OuterRef, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.utils.date import get_date_interval_from_request

from wbaccounting.models import EntryAccountingInformation, Invoice
from wbaccounting.models.booking_entry import BookingEntry
from wbaccounting.serializers import (
    EntryAccountingInformationModelSerializer,
    EntryAccountingInformationRepresentationSerializer,
)
from wbaccounting.viewsets.buttons import EntryAccountingInformationButtonConfig
from wbaccounting.viewsets.display import EntryAccountingInformationDisplayConfig
from wbaccounting.viewsets.titles import EntryAccountingInformationTitleConfig

from ..permissions import CanGenerateBookingEntry, CanGenerateInvoice


class EntryAccountingInformationRepresentationViewSet(viewsets.RepresentationViewSet):
    search_fields = ("entry__computed_str",)
    queryset = EntryAccountingInformation.objects.all()
    serializer_class = EntryAccountingInformationRepresentationSerializer

    def get_queryset(self):
        return EntryAccountingInformation.objects.filter_for_user(self.request.user)


class EntryAccountingInformationModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbaccounting:entryaccountinginformation"
    filterset_fields = {
        "entry": ["exact"],
        "tax_id": ["exact", "icontains"],
        "vat": ["gte", "exact", "lte"],
        "default_currency": ["gte", "exact", "lte"],
        "send_mail": ["exact"],
        "counterparty_is_private": ["exact"],
        "exempt_users": ["exact"],
    }

    serializer_class = EntryAccountingInformationModelSerializer
    queryset = EntryAccountingInformation.objects.all()

    search_fields = ["entry__computed_str"]
    ordering_fields = ["tax_id", "vat", "send_mail", "counterparty_is_private"]
    ordering = ["id"]

    display_config_class = EntryAccountingInformationDisplayConfig
    title_config_class = EntryAccountingInformationTitleConfig
    button_config_class = EntryAccountingInformationButtonConfig

    def get_queryset(self) -> QuerySet[EntryAccountingInformation]:
        return (
            EntryAccountingInformation.objects.filter_for_user(self.request.user)
            .select_related(
                "entry",
                "default_currency",
                "default_invoice_type",
            )
            .prefetch_related(
                "exempt_users",
                "email_to",
                "email_cc",
                "email_bcc",
            )
        )

    @action(detail=True, methods=["POST"], permission_classes=[CanGenerateBookingEntry])
    def generate_booking_entries(self, request, pk):
        eai = get_object_or_404(EntryAccountingInformation, id=pk)
        start, end = get_date_interval_from_request(request, request_type="POST")
        if start and end:
            eai.generate_booking_entries(start, end)  # type: ignore
            return Response(
                {"__notification": {"title": "Booking Entries are being generated in the background."}},
                status=status.HTTP_200_OK,
            )
        return Response({"status": "Missing start and end dates"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], permission_classes=[CanGenerateBookingEntry])
    def generate_booking_entries_for_counterparties(self, request, pk=None):
        # TODO: this is not used yet, might want to clean this action
        start, end = get_date_interval_from_request(request, request_type="POST")
        if not start or not end:
            return Response({"status": "Missing start and end dates"}, status=status.HTTP_400_BAD_REQUEST)
        eais = EntryAccountingInformation.objects.filter(
            entry__id__in=request.POST.get("counterparties", "").split(",")
        )
        for eai in eais:
            eai.generate_booking_entries(start, end)  # type: ignore
        return Response(
            {"__notification": {"title": "Booking Entries are being generated in the background."}},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["POST"], permission_classes=[CanGenerateInvoice])
    def generate_invoices_for_counterparties(self, request, pk=None):
        # TODO: this is not used yet, might want to clean this action
        eais = (
            EntryAccountingInformation.objects.filter(entry__id__in=request.POST.get("counterparties", "").split(","))
            .annotate(
                has_open_bookings=Exists(
                    BookingEntry.objects.filter(
                        counterparty=OuterRef("entry"),
                        invoice__isnull=True,
                        payment_date__isnull=True,
                    )
                )
            )
            .filter(has_open_bookings=True)
        )
        for eai in eais:
            Invoice.objects.create_for_counterparty(eai.entry, invoice_date=date.today())
        return Response(
            {"__notification": {"title": "Invoices are being generated in the background."}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], permission_classes=[CanGenerateInvoice])
    def invoice_booking_entries(self, request, pk):
        eai = get_object_or_404(EntryAccountingInformation, id=pk)
        Invoice.objects.create_for_counterparty(eai.entry, invoice_date=date.today())
        return Response(
            {"__notification": {"title": "Booking Entries are being generated in the background."}},
            status=status.HTTP_200_OK,
        )
