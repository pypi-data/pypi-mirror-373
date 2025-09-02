from django.contrib import admin

from wbaccounting.models import EntryAccountingInformation


@admin.register(EntryAccountingInformation)
class EntryAccountingInformationModelAdmin(admin.ModelAdmin):
    list_display = ("entry", "send_mail", "counterparty_is_private")
    autocomplete_fields = ["default_currency", "entry", "email_to", "email_cc", "email_bcc", "exempt_users"]

    search_fields = ["entry__computed_str"]
