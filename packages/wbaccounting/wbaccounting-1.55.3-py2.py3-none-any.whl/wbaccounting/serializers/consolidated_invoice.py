from django.utils.http import urlencode
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.authentication.models import User
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.serializers import EntryRepresentationSerializer

from wbaccounting.models import BookingEntry, Invoice
from wbaccounting.serializers import (
    BookingEntryRepresentationSerializer,
    InvoiceRepresentationSerializer,
    InvoiceTypeRepresentationSerializer,
)


class ConsolidatedInvoiceSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyCharField()
    reference_date = serializers.DateField()
    invoice = serializers.PrimaryKeyRelatedField(allow_null=True)
    _invoice = InvoiceRepresentationSerializer(source="invoice")
    invoice_currency = serializers.PrimaryKeyRelatedField(allow_null=True)
    _invoice_currency = CurrencyRepresentationSerializer(source="invoice_currency")
    counterparty = serializers.PrimaryKeyRelatedField(allow_null=True)
    _counterparty = EntryRepresentationSerializer(source="counterparty")
    _group_key = serializers.CharField()
    type = serializers.PrimaryKeyRelatedField(allow_null=True)
    _type = InvoiceTypeRepresentationSerializer(source="type")
    booking_entries = serializers.PrimaryKeyRelatedField(allow_null=True)
    _booking_entries = BookingEntryRepresentationSerializer(source="booking_entries")
    group = serializers.CharField()
    currency_symbol = serializers.CharField()
    value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        decorators=[serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}")],
    )
    casted_endpoint = serializers.SerializerMethodField()
    depth = serializers.IntegerField()
    num_draft = serializers.IntegerField()
    num_submitted = serializers.IntegerField()
    num_sent = serializers.IntegerField()
    num_paid = serializers.IntegerField()

    @serializers.register_resource()
    def register_buttons(self, instance: dict, request, user: User) -> dict[str, str]:
        button_dict = {}

        if instance["depth"] == 5:
            return button_dict

        if instance.get("num_draft", 0) > 0:
            button_dict["submit"] = reverse(
                "wbaccounting:consolidated-invoice-submit", args=[instance["id"]], request=request
            )

        if instance.get("num_submitted", 0) > 0 and user.has_perm("wbaccounting.administrate_invoice"):
            button_dict["approve"] = reverse(
                "wbaccounting:consolidated-invoice-approve", args=[instance["id"]], request=request
            )

        if instance.get("num_sent", 0) > 0 and user.has_perm("wbaccounting.administrate_invoice"):
            button_dict["pay"] = reverse(
                "wbaccounting:consolidated-invoice-pay", args=[instance["id"]], request=request
            )

        for key in button_dict.keys():
            button_dict[key] = button_dict[key] + "?" + urlencode(dict(request.GET.items()))
        return button_dict

    def get_casted_endpoint(self, obj: dict) -> str | None:
        if obj.get("depth", 0) == 4:
            return reverse(
                f"{Invoice.get_endpoint_basename()}-detail",
                args=[obj["id"]],
                request=self.context.get("request", None),
            )
        elif obj.get("depth", 0) == 5:
            return reverse(
                f"{BookingEntry.get_endpoint_basename()}-detail",
                args=[obj["id"]],
                request=self.context.get("request", None),
            )

    class Meta:
        fields = read_only_fields = (
            "id",
            "reference_date",
            "invoice",
            "_invoice",
            "invoice_currency",
            "_invoice_currency",
            "counterparty",
            "_counterparty",
            "booking_entries",
            "_booking_entries",
            "group",
            "value",
            "_additional_resources",
            "type",
            "_type",
            "casted_endpoint",
            "currency_symbol",
            "_buttons",
            "_group_key",
            "depth",
            "num_draft",
            "num_submitted",
            "num_sent",
            "num_paid",
        )
