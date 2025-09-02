from typing import Any

from django.core.exceptions import FieldError
from django.db.models import (
    CharField,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    IntegerField,
    Q,
    QuerySet,
    Sum,
    Value,
)
from django.db.models.functions import Concat
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbcore.filters import DjangoFilterBackend

from wbaccounting.models import Invoice, submit_invoices_as_task
from wbaccounting.models.model_tasks import (
    approve_invoices_as_task,
    pay_invoices_as_task,
)
from wbaccounting.permissions import IsInvoiceAdmin
from wbaccounting.serializers import (
    ConsolidatedInvoiceSerializer,
    InvoiceModelSerializer,
    InvoiceRepresentationSerializer,
)
from wbaccounting.viewsets.buttons import (
    ConsolidatedInvoiceButtonConfig,
    InvoiceButtonConfig,
)
from wbaccounting.viewsets.display import (
    ConsolidatedInvoiceDisplayConfig,
    InvoiceDisplayConfig,
)
from wbaccounting.viewsets.endpoints import ConsolidatedInvoiceEndpointConfig
from wbaccounting.viewsets.titles import (
    ConsolidatedInvoiceTitleConfig,
    InvoiceTitleConfig,
)


class InvoiceRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = InvoiceRepresentationSerializer
    filter_backends = (filters.OrderingFilter,)
    queryset = Invoice.objects.all()
    ordering_fields = ["invoice_date"]
    ordering = ["invoice_date"]

    def get_queryset(self):
        return Invoice.objects.filter_for_user(self.request.user)  # type: ignore


class InvoiceModelViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceModelSerializer

    filterset_fields = {
        "counterparty": ["exact"],
        "status": ["exact"],
        "title": ["exact", "icontains"],
        "invoice_date": ["gte", "exact", "lte"],
        "invoice_type": ["exact"],
        "reference_date": ["gte", "exact", "lte"],
    }

    search_fields = ["counterparty__computed_str", "title", "invoice_type__name"]
    ordering_fields = (
        "invoice_date",
        "counterparty__computed_str",
        "invoice_type__name",
        "reference_date",
        "gross_value",
        "net_value",
    )
    ordering = (
        "-invoice_date",
        "id",
    )
    queryset = Invoice.objects.all()

    button_config_class = InvoiceButtonConfig
    display_config_class = InvoiceDisplayConfig
    title_config_class = InvoiceTitleConfig

    def get_queryset(self) -> QuerySet[Invoice]:
        invoices = Invoice.objects.filter_for_user(self.request.user)  # type: ignore

        if eai_id := self.kwargs.get("entry_accounting_information_id", None):
            invoices = invoices.filter(counterparty__entry_accounting_information__id=eai_id)

        return invoices.select_related(
            "counterparty",
            "invoice_currency",
            "invoice_type",
        )


class ConsolidatedInvoiceViewSet(viewsets.ViewSet):
    IDENTIFIER = "wbaccounting:consolidated-invoice"
    title_config_class = ConsolidatedInvoiceTitleConfig
    serializer_class = ConsolidatedInvoiceSerializer
    permission_classes = []
    display_config_class = ConsolidatedInvoiceDisplayConfig
    button_config_class = ConsolidatedInvoiceButtonConfig
    filterset_fields = {"status": ["exact"]}
    filter_backends = (DjangoFilterBackend,)
    endpoint_config_class = ConsolidatedInvoiceEndpointConfig
    queryset = Invoice.objects.none()

    def list(self, request):
        queryset = self.get_queryset()
        if serializer := self.get_serializer_class():
            serializer = serializer(queryset, many=True, context={"request": request, "view": self})
            return Response({"results": serializer.data})
        return Response({"results": {}})

    def get_lookup(self) -> dict:
        lookup = {}
        if (request := getattr(self, "request")) and (lookup_str := request.GET.get("lookup")):
            lookup = dict(map(lambda x: x.split(":"), lookup_str.split(",")))
        return lookup

    def get_lookup_mapping(self, currency_symbol: str = "") -> "list[tuple]":
        return [
            ("reference_date", "reference_date", "gross_value_default_currency", Value(currency_symbol)),
            ("invoice_type", "invoice_type__name", "gross_value_default_currency", Value(currency_symbol)),
            ("invoice_currency", "invoice_currency__symbol", "gross_value", F("invoice_currency__symbol")),
            ("counterparty", "counterparty__computed_str", "gross_value", F("invoice_currency__symbol")),
            ("id", "title", "gross_value", F("invoice_currency__symbol")),
            (
                "booking_entries",
                "booking_entries__title",
                "booking_entries__gross_value",
                F("booking_entries__currency__symbol"),
            ),
        ]

    def get_queryset(self):
        # We get the default currency id, as we potentially need it to convert some aggregates
        default_currency = Currency.objects.get(
            key=global_preferences_registry.manager()["currency__default_currency"]
        )

        # lookup is a GET parameter in the format of ?lookup=key1:param1,key2:param2
        # we convert it to a dictionairy for easier access
        lookup = self.get_lookup()

        # the number of items in the lookup dictionairy define the depth of the treeview, e.g
        # depth 0 means the first level, depth 1 the second, and so on
        depth = len(lookup.keys())

        # if there is a status GET parameter, we add it to make sure we only look at aggregated invoices
        # with that status
        status_filter = {}
        if status := self.request.GET.get("status"):
            status_filter["status"] = status

        # We filter the queryset with the lookup dictionairy and the status dictionairy
        # In case a wrong lookup was parsed in here a FieldError is raised and we return
        # an empty queryset
        try:
            queryset = Invoice.objects.filter_for_user(self.request.user).filter(**lookup, **status_filter)  # type: ignore
        except FieldError:
            return Invoice.objects.none()

        # Filter out all invoice that do not have a reference date.
        queryset = queryset.exclude(reference_date__isnull=True)

        # Depending on the depth and the default currency we get a tuple with the following elements
        # 0: reference to the field that will be used as an id
        # 1: reference to the name of the group
        # 2: reference to which field is used to sum up the invoices
        # 3: reference to which currency is used
        group_by = self.get_lookup_mapping(default_currency.symbol or "USD")[depth]

        # If the depth is smaller than 2, this means we have to convert the values to the default
        # currency FX Rate. This is because the first 2 levels (level 0 and 1) are group by date
        # and group by invoice type, which are currency agnostic. The third level (level 2) is by
        # currency, so we don't have to convert the invoice currency anymore
        if depth < 2:
            queryset = queryset.annotate(
                fx_rate_default_currency=CurrencyFXRates.get_fx_rates_subquery_for_two_currencies(
                    "reference_date", "invoice_currency", default_currency
                ),
                gross_value_default_currency=ExpressionWrapper(
                    F("gross_value") * F("fx_rate_default_currency"),
                    output_field=DecimalField(decimal_places=2, max_digits=15),
                ),
            )

        # if the id reference is not id (or level 4), we annotate the field as the id field
        # we cannot do this for level 4 (or when the id field is id) because django will
        # crash otherwise.
        if group_by[0] != "id":
            queryset = queryset.values(group_by[0]).annotate(id=F(group_by[0]))

        # We annotate all values received from the get_lookup_mapping
        queryset = queryset.annotate(
            currency_symbol=group_by[3],
            value=Sum(group_by[2]),
            group=F(group_by[1]),
            _group_key=Value(None, output_field=CharField(max_length=255)),
            depth=Value(depth, output_field=IntegerField()),
            num_draft=Count("pk", filter=Q(status="DRAFT")),
            num_submitted=Count("pk", filter=Q(status="SUBMITTED")),
            num_sent=Count("pk", filter=Q(status="SENT")),
            num_paid=Count("pk", filter=Q(status="PAID")),
        )

        # If the group_by id field is not booking entries (or not the last level), then we annotate a _group_key
        # We do this to give the frontend an understanding on how to open the next row. We don't do this on the
        # last level, to ensure that the last group cannot be further extended
        if group_by[0] != "booking_entries":
            queryset = queryset.annotate(
                _group_key=Concat(Value(group_by[0] + ":"), F(group_by[0]), output_field=CharField(max_length=255)),
            )

        return queryset.order_by("-reference_date").values(
            "id",
            "reference_date",
            "value",
            "currency_symbol",
            "_group_key",
            "group",
            "depth",
            "num_draft",
            "num_submitted",
            "num_sent",
            "num_paid",
        )

    def get_underlying_invoices(self, request: Request, pk: Any, source_status: Invoice.Status) -> QuerySet[Invoice]:
        """Returns all of the current row's underlying invoices filtered by `source_status`.

        Args:
            request: HttpRequest
            pk: Pk of the current row. Type varies accordingly.
            source_status (Invoice.Status): We need to filter by the state where a certain transition is allowed

        Returns:
            QuerySet(Invoice): A queryset of invoices
        """

        lookup = self.get_lookup()
        depth = len(lookup.keys())
        status_filter = request.GET.get("status", "")
        pk_filter = self.get_lookup_mapping()[depth][0]
        if depth < 5 and (not status_filter or status_filter == source_status.value):
            return Invoice.objects.filter(**lookup | {pk_filter: pk}, status=source_status)

        return Invoice.objects.none()

    @action(detail=True, methods=["PATCH"])
    def submit(self, request: Request, pk: Any):
        underlying_invoices = self.get_underlying_invoices(request, pk, Invoice.Status.DRAFT)
        submit_invoices_as_task.delay(underlying_invoices.values_list("id", flat=True))  # type: ignore
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], permission_classes=[IsInvoiceAdmin])
    def approve(self, request: Request, pk: Any):
        underlying_invoices = self.get_underlying_invoices(request, pk, Invoice.Status.SUBMITTED)
        approve_invoices_as_task.delay(underlying_invoices.values_list("id", flat=True))  # type: ignore
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], permission_classes=[IsInvoiceAdmin])
    def pay(self, request: Request, pk: Any):
        underlying_invoices = self.get_underlying_invoices(request, pk, Invoice.Status.SENT)
        pay_invoices_as_task.delay(underlying_invoices.values_list("id", flat=True))  # type: ignore
        return Response(status=status.HTTP_200_OK)
