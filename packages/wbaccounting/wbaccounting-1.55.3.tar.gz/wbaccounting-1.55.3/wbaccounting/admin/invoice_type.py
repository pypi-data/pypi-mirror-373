from django.contrib import admin

from wbaccounting.models import InvoiceType


@admin.register(InvoiceType)
class InvoiceTypeModelAdmin(admin.ModelAdmin):
    search_fields = ("name", "processor")
    list_display = ("id", "name", "processor")
