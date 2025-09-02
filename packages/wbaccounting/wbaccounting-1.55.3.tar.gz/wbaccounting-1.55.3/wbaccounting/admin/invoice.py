from django.contrib import admin
from wbcore.contrib.documents.admin import DocumentInLine

from wbaccounting.admin import BookingEntryInline
from wbaccounting.models import Invoice


@admin.register(Invoice)
class InvoiceModelAdmin(admin.ModelAdmin):
    fsm_field = ["status"]
    search_fields = ("counterparty__computed_str", "title", "invoice_type__name")
    list_display = (
        "status",
        "title",
        "gross_value",
        "net_value",
        "invoice_date",
        "invoice_currency",
        "counterparty",
        "invoice_type",
        "reference_date",
    )

    autocomplete_fields = ("counterparty",)
    inlines = [BookingEntryInline, DocumentInLine]

    raw_id_fields = ["counterparty", "invoice_currency", "invoice_type"]
