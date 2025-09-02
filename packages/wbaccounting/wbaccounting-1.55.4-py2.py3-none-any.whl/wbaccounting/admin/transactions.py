from django.contrib import admin

from wbaccounting.models import Transaction


@admin.register(Transaction)
class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ["booking_date", "value_date", "value", "bank_account", "prenotification"]

    raw_id_fields = ["import_source"]

    autocomplete_fields = [
        "bank_account",
        "from_bank_account",
        "to_bank_account",
        "currency",
    ]
