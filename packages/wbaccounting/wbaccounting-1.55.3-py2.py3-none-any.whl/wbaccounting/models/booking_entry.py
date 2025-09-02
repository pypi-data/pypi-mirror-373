from decimal import Decimal

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from wbcore.contrib.authentication.models import User
from wbcore.models import WBModel


class BookingEntryDefaultQuerySet(models.QuerySet):
    def filter_for_user(self, user: User) -> models.QuerySet:
        """
        Filters booking entries based on if the current user can see the invoice.

        Args:
            user (User): The user for whom booking entries need to be filtered.

        Returns:
            QuerySet: A filtered queryset.
        """

        # Superuser and users with the admin permission can see all booking entries
        if user.is_superuser or user.has_perm("wbaccounting.administrate_invoice"):
            return self

        # If the user doesn't have the view permission, nothing can be seen
        if not user.has_perm("wbaccounting.view_bookingentry"):
            return self.none()

        # The user can see all booking entries where the counterparty is not private
        # or where the user is part of the exempt users list
        return self.filter(
            models.Q(counterparty__entry_accounting_information__counterparty_is_private=False)
            | models.Q(counterparty__entry_accounting_information__exempt_users=user)
        )


class BookingEntry(WBModel):
    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

        permissions = (
            (
                "can_generate_booking_entries",
                "Can Generate Bookings",
            ),
        )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Reference date defaults to booking date if not specified
        if not self.reference_date:
            self.reference_date = self.booking_date

        # If net value is specified, then gross value is determined based on VAT
        if self.net_value:
            self.gross_value = self.net_value + (self.net_value * self.vat)
        # If net value is not specified, but gross value is, then net value is determined based on VAT
        elif self.gross_value:
            self.net_value = self.gross_value / (Decimal(1 + self.vat))
        # If neither is defined the both are 0
        else:
            self.net_value, self.gross_value = 0, 0

        # If an invoice is attached we need to compute net and gross value in the invoice currency
        if self.invoice:
            # We get the fx rate (If it is the same currency, then it will be 1)
            self.invoice_fx_rate = self.currency.convert(self.booking_date, self.invoice.invoice_currency)
            self.invoice_net_value = self.net_value * self.invoice_fx_rate
            self.invoice_gross_value = self.gross_value * self.invoice_fx_rate

        super().save(*args, **kwargs)

    objects = BookingEntryDefaultQuerySet.as_manager()

    # The title of the booking entry which describes what was booked
    title = models.CharField(max_length=255, verbose_name="Title")

    # The date when this booking entry is booked. Most likely the current date
    booking_date = models.DateField(verbose_name="Booking Date")

    # The date when this booking entry has to be paid / received. If None, this date is not important.
    due_date = models.DateField(null=True, blank=True, verbose_name="Due Date")

    # The date when this booking entry was paid / received. If None, this booking entry is still "open"
    payment_date = models.DateField(null=True, blank=True, verbose_name="Payment Date")

    # The reference date represents a date to which accounting period a booking entry belongs
    reference_date = models.DateField(verbose_name="Reference Date", null=True, blank=True)

    # Either Gross or Net has to be specified. If both are specifying then net is preferred.
    # If only one is specified the other one is determined based on the given VAT. The default
    # VAT is 0%. If the value of net/gross is negative, then money is paid.
    gross_value = models.DecimalField(
        max_digits=16, decimal_places=4, null=True, blank=True, verbose_name="Gross Value"
    )
    net_value = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True, verbose_name="Net Value")
    invoice_gross_value = models.DecimalField(
        max_digits=16, decimal_places=4, null=True, blank=True, verbose_name="Invoice Gross Value"
    )
    invoice_net_value = models.DecimalField(
        max_digits=16, decimal_places=4, null=True, blank=True, verbose_name="Invoice Net Value"
    )
    invoice_fx_rate = models.DecimalField(
        max_digits=20, decimal_places=6, null=True, blank=True, verbose_name="Invoice FX Rate"
    )
    vat = models.DecimalField(max_digits=4, decimal_places=4, default=Decimal(0), verbose_name="VAT")

    # The currency of the booking entry
    currency = models.ForeignKey(
        "currency.Currency", related_name="booking_entries", on_delete=models.PROTECT, verbose_name="Currency"
    )

    invoice = models.ForeignKey(
        "Invoice",
        related_name="booking_entries",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Invoice",
    )

    # The entry who has to pay / receive money
    counterparty = models.ForeignKey(
        "directory.Entry", related_name="booking_entries", on_delete=models.PROTECT, verbose_name="Counterparty"
    )

    # The backlinks stores information and the destination where to find the underlying data
    # The backlinks is rendered in lists and instances as a button
    backlinks = models.JSONField(null=True, blank=True)

    # Extra parameters for rendering on an invoice
    parameters = models.JSONField(null=True, blank=True)

    # Generator that produced this Booking Entry
    generator = models.CharField(max_length=256, null=True, blank=True)

    @classmethod
    def get_endpoint_basename(cls):
        return "wbaccounting:bookingentry"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{title}}"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbaccounting:bookingentryrepresentation-list"


@receiver(post_save, sender=BookingEntry)
def booking_entry_changed(sender, instance: BookingEntry, created: bool, raw: bool, **kwargs):
    if not raw and (invoice := instance.invoice):
        invoice.save()


@receiver(post_delete, sender=BookingEntry)
def booking_entry_deleted(sender, instance, **kwargs):
    if instance.invoice:
        instance.invoice.save()
