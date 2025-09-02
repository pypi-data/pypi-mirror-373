from contextlib import suppress
from datetime import date

from celery import shared_task
from django.db.models.signals import post_save
from django.utils.module_loading import import_string
from wbcore.contrib.directory.models import Entry

from wbaccounting.generators.base import generate_booking_entries


@shared_task
def submit_invoices_as_task(ids: list[int]):
    from wbaccounting.models import Invoice

    invoices = Invoice.objects.filter(id__in=ids)
    for invoice in invoices:
        invoice.submit()
        invoice.save()


@shared_task
def approve_invoices_as_task(ids: list[int]):
    from wbaccounting.models import Invoice

    invoices = Invoice.objects.filter(id__in=ids)
    for invoice in invoices:
        invoice.approve()
        invoice.save()


@shared_task
def pay_invoices_as_task(ids: list[int]):
    from wbaccounting.models import Invoice

    invoices = Invoice.objects.filter(id__in=ids)
    for invoice in invoices:
        invoice.pay()
        invoice.save()


@shared_task
def refresh_complete_invoice_as_task(invoice_id: int):
    from wbaccounting.models import Invoice
    from wbaccounting.models.booking_entry import BookingEntry, booking_entry_changed

    # We temmporarily disconnect the post_save hook in order to not regenerate the invoice over and over again
    post_save.disconnect(booking_entry_changed, sender=BookingEntry)

    for booking_entry in BookingEntry.objects.filter(invoice_id=invoice_id):
        booking_entry.save()

    Invoice.objects.get(id=invoice_id).save()

    # We reattach the post_save hook
    post_save.connect(booking_entry_changed, sender=BookingEntry)


@shared_task
def refresh_invoice_document_as_task(invoice_id):
    from wbaccounting.models import Invoice

    invoice = Invoice.objects.get(id=invoice_id)
    invoice.refresh_invoice_document()


@shared_task
def generate_booking_entries_as_task(func: str, from_date: date, to_date: date, counterparty_id: int):
    with suppress(ImportError):
        generator = import_string(func)
        counterparty = Entry.objects.get(id=counterparty_id)
        generate_booking_entries(generator, from_date, to_date, counterparty)
