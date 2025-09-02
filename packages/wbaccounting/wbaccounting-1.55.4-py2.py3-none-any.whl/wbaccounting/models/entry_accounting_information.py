from contextlib import suppress
from datetime import date

from django.db import models
from django.db.models import Q, QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.module_loading import import_string
from dynamic_preferences.registries import global_preferences_registry as gpr
from wbcore.contrib.authentication.models import User
from wbcore.contrib.currency.models import Currency

from wbaccounting.models.model_tasks import generate_booking_entries_as_task


def default_email_body() -> str:
    with suppress(Exception):
        return gpr.manager()["wbaccounting__invoice_email_body"]

    return ""


def default_currency() -> Currency | None:
    with suppress(Exception):
        return Currency.objects.get(key=gpr.manager()["wbaccounting__default_entry_account_information_currency_key"])


class EntryAccountingInformationDefaultQuerySet(QuerySet):
    def filter_for_user(self, user: User) -> QuerySet:
        """
        Filters entry accounting information based on if the current user is allowed to see it.

        Args:
            user (User): The user for whom entry accounting information need to be filtered.

        Returns:
            QuerySet: A filtered queryset.
        """

        if user.is_superuser or user.has_perm("wbaccounting.administrate_invoice"):
            return self

        if not user.has_perm("wbaccounting.view_entryaccountinginformation"):
            return self.none()

        return self.filter(Q(counterparty_is_private=False) | Q(exempt_users=user))


class EntryAccountingInformation(models.Model):
    # Link to Entry
    entry = models.OneToOneField(
        "directory.Entry",
        on_delete=models.CASCADE,
        related_name="entry_accounting_information",
        verbose_name="Linked Counterparty",
    )

    # Tax Information
    tax_id = models.CharField(max_length=512, blank=True, null=True, verbose_name="Tax ID")
    vat = models.FloatField(blank=True, null=True, verbose_name="VAT")

    # Invoice Information
    default_currency = models.ForeignKey(
        "currency.Currency",
        related_name="entry_accounting_informations",
        default=default_currency,
        on_delete=models.PROTECT,
        verbose_name="Default Currency",
        blank=True,
        null=True,
    )

    email_to = models.ManyToManyField(
        "directory.EmailContact", related_name="entry_accounting_informations_to", blank=True, verbose_name="To"
    )

    email_cc = models.ManyToManyField(
        "directory.EmailContact", related_name="entry_accounting_informations_cc", blank=True, verbose_name="CC"
    )
    email_bcc = models.ManyToManyField(
        "directory.EmailContact", related_name="entry_accounting_informations_bcc", blank=True, verbose_name="BCC"
    )

    email_subject = models.CharField(default="{{invoice.title}}", max_length=1024, verbose_name="Subject")
    email_body = models.TextField(default=default_email_body, verbose_name="Body")
    send_mail = models.BooleanField(default=True, verbose_name="Send Mail")

    counterparty_is_private = models.BooleanField(
        default=False,
        verbose_name="Counterparty Is Private",
        help_text="Hides all of the counterparty's invoices from non-eligible users",
    )
    exempt_users = models.ManyToManyField(
        to="authentication.User",
        verbose_name="Exempt Users",
        help_text="Exclusion list of users who are able to see private invoices for the counterparty",
        related_name="private_accounting_information",
        blank=True,
    )
    booking_entry_generator = models.CharField(max_length=256, null=True, blank=True)
    default_invoice_type = models.ForeignKey(
        to="wbaccounting.InvoiceType",
        related_name="booking_entries",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Default Invoice Type",
        help_text="When invoicinging outstanding booking entries, this invoice type will be assigned to the corresponding invoice",
    )

    external_invoice_users = models.ManyToManyField(
        to="authentication.User",
        verbose_name="External User",
        help_text="External users who are able to see the invoices generated for this counterparty",
        related_name="external_accounting_information",
        blank=True,
    )

    def get_booking_entry_generator(self):
        with suppress(ImportError):
            return import_string(self.booking_entry_generator or "")

    objects = EntryAccountingInformationDefaultQuerySet.as_manager()

    class Meta:
        verbose_name = "Counterparty"
        verbose_name_plural = "Counterparties"

    def __str__(self):
        return f"Counterparty: {self.entry.computed_str}"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbaccounting:entryaccountinginformationrepresentation-list"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbaccounting:entryaccountinginformation"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{entry_repr}}"

    def generate_booking_entries(self, from_date: date, to_date: date):
        generate_booking_entries_as_task.delay(  # type: ignore
            self.booking_entry_generator or "", from_date, to_date, self.entry.id
        )


@receiver(post_save, sender=EntryAccountingInformation)
def post_save_entry(sender, instance, **kwargs):
    """If the EAI does not have any email_to, then we add the entries primary email address to it (if it exists)"""
    if not instance.email_to.exists() and (email := instance.entry.primary_email_contact()):
        instance.email_to.add(email)
