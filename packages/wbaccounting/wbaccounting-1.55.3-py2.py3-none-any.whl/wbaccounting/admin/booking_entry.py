from datetime import date

from django.contrib import admin
from wbcore.contrib.directory.models import Entry

from wbaccounting.models import BookingEntry, Invoice


class BookingEntryInline(admin.TabularInline):
    model = BookingEntry
    fields = ("booking_date", "net_value", "vat")
    ordering = ("vat", "title")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BookingEntry)
class BookingEntryModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "booking_date",
        "net_value",
        "vat",
        "currency",
        "payment_date",
        "counterparty",
        "reference_date",
    )
    search_fields = ["counterparty__computed_str"]
    autocomplete_fields = ("counterparty", "currency")

    # TODO: Remove or adjust.
    def create_invoice(self, request, queryset):
        counterparty = list(set(queryset.values_list("counterparty__id", flat=True)))
        if len(counterparty) == 1:
            counterparty = Entry.objects.get(id=counterparty[0])
            invoice = Invoice.objects.create(
                title=f"Rebate Invoice {counterparty.computed_str} ({queryset.earliest('from_date').from_date:%d.%m.%Y} - {queryset.latest('to_date').to_date:%d.%m.%Y})",
                invoice_date=date.today(),
                reference_date=date.today(),
                counterparty=counterparty,
                invoice_currency=counterparty.entry_accounting_information.default_currency,
                is_counterparty_invoice=True,
            )
            queryset.update(invoice=invoice)
            invoice.save()

        else:
            print("-------------------------------")  # noqa: T201
            print(f"Too many counterparties selected ({len(counterparty)})")  # noqa: T201
            print("-------------------------------")  # noqa: T201

    actions = [create_invoice]
