from django.utils.http import urlencode
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.serializers import EntryRepresentationSerializer
from wbcore.metadata.configs.buttons import WidgetButton

from wbaccounting.models import BookingEntry
from wbaccounting.serializers import InvoiceRepresentationSerializer


class BookingEntryRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbaccounting:bookingentry-detail")

    class Meta:
        model = BookingEntry
        fields = (
            "id",
            "title",
            "_detail",
        )


class BookingEntryModelSerializer(serializers.ModelSerializer):
    _currency = CurrencyRepresentationSerializer(source="currency")
    _counterparty = EntryRepresentationSerializer(source="counterparty")
    _invoice = InvoiceRepresentationSerializer(source="invoice")

    invoice_currency = serializers.StringRelatedField(
        source="invoice.invoice_currency", read_only=True, label="Inv. Currency"
    )

    @serializers.register_dynamic_button()
    def dynamic_buttons(self, instance, request, user):
        buttons = []

        if backlinks := instance.backlinks:
            for _, backlink in backlinks.items():
                buttons.append(
                    WidgetButton(
                        label=backlink["title"],
                        endpoint=f'{reverse(backlink["reverse"], request=request)}?{urlencode(backlink["parameters"])}',
                    )
                )

        return buttons

    class Meta:
        model = BookingEntry
        decorators = {
            "gross_value": serializers.decorator(decorator_type="text", position="left", value="{{_currency.symbol}}"),
            "net_value": serializers.decorator(decorator_type="text", position="left", value="{{_currency.symbol}}"),
        }
        percent_fields = ["vat"]
        read_only_fields = ["invoice_net_value", "invoice_gross_value", "invoice_fx_rate"]

        fields = (
            "id",
            "title",
            "booking_date",
            "due_date",
            "payment_date",
            "reference_date",
            "net_value",
            "gross_value",
            "vat",
            "invoice_net_value",
            "invoice_gross_value",
            "invoice_fx_rate",
            "currency",
            "_currency",
            "counterparty",
            "_counterparty",
            "invoice",
            "_invoice",
            "invoice_currency",
            "_additional_resources",
            "_buttons",
        )
