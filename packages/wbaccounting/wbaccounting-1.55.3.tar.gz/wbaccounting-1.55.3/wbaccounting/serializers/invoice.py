from django.contrib.contenttypes.models import ContentType
from django.utils.http import urlencode
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.serializers import EntryRepresentationSerializer
from wbcore.metadata.configs.buttons import WidgetButton

from wbaccounting.models import Invoice, InvoiceType
from wbaccounting.serializers import InvoiceTypeRepresentationSerializer


class InvoiceRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbaccounting:invoice-detail")

    class Meta:
        model = Invoice
        fields = (
            "id",
            "title",
            "invoice_date",
            "_detail",
        )


class InvoiceModelSerializer(serializers.ModelSerializer):
    _counterparty = EntryRepresentationSerializer(source="counterparty")
    _invoice_currency = CurrencyRepresentationSerializer(source="invoice_currency")
    _invoice_type = InvoiceTypeRepresentationSerializer(source="invoice_type")
    invoice_type = serializers.PrimaryKeyRelatedField(label="Type", required=True, queryset=InvoiceType.objects.all())

    net_value = serializers.DecimalField(max_digits=16, decimal_places=2, label="Net Value", read_only=True)
    gross_value = serializers.DecimalField(max_digits=16, decimal_places=2, label="Gross Value", read_only=True)

    @serializers.register_resource()
    def bookingentries(self, instance, request, user):
        # Do some something (checks, etc.)
        return {
            "bookingentries": reverse("wbaccounting:invoice-bookingentry-list", args=[instance.id], request=request)
        }

    @serializers.register_resource()
    def invoice_file(self, instance, request, user):
        return {
            "invoice_file": f'{reverse("wbcore:documents:document-urlredirect", args=[], request=request)}?content_type={ContentType.objects.get_for_model(Invoice).id}&object_id={instance.id}'
        }

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
        model = Invoice
        decorators = {
            "net_value": serializers.decorator(
                decorator_type="text", position="left", value="{{_invoice_currency.symbol}}"
            ),
            "gross_value": serializers.decorator(
                decorator_type="text", position="left", value="{{_invoice_currency.symbol}}"
            ),
        }
        fields = (
            "id",
            "status",
            "reference_date",
            "resolved",
            "title",
            "invoice_date",
            "invoice_currency",
            "_invoice_currency",
            "counterparty",
            "_counterparty",
            "text_above",
            "text_below",
            "_additional_resources",
            "gross_value",
            "net_value",
            "invoice_type",
            "_invoice_type",
            "_buttons",
        )
        read_only_fields = (
            "gross_value",
            "net_value",
        )
