from contextlib import suppress
from decimal import Decimal
from io import BytesIO
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.files import File
from django.db import models, transaction
from django.db.models import Max, Q, QuerySet, Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from dynamic_preferences.registries import global_preferences_registry
from slugify import slugify
from wbcore.contrib.authentication.models import User
from wbcore.contrib.directory.models import Company, Entry
from wbcore.contrib.documents.models import Document, DocumentType
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.models import WBModel
from wbcore.utils.importlib import import_from_dotted_path

from wbaccounting.dynamic_preferences_registry import format_invoice_number
from wbaccounting.files.invoice_document_file import generate_file
from wbaccounting.models.booking_entry import BookingEntry, BookingEntryDefaultQuerySet
from wbaccounting.models.model_tasks import (
    refresh_complete_invoice_as_task,
    refresh_invoice_document_as_task,
)


class InvoiceDefaultQuerySet(QuerySet):
    def create_for_booking_entry(self, booking_entry: BookingEntry, **kwargs) -> "Invoice":
        """
        Creates an Invoice instance associated with a specific BookingEntry and updates the BookingEntry
        to link to this newly created Invoice.

        This method takes a BookingEntry object as input, creates a new Invoice associated with the BookingEntry's
        counterparty, and then links the BookingEntry to this new Invoice by updating its 'invoice' field.

        Args:
            booking_entry (BookingEntry): The BookingEntry instance for which to create the invoice.

        Returns:
            Invoice: The newly created Invoice instance associated with the given BookingEntry's counterparty.
        """
        invoice = super().create(
            counterparty=booking_entry.counterparty,
            invoice_type=booking_entry.counterparty.entry_accounting_information.default_invoice_type,
            **kwargs,
        )
        booking_entry.invoice = invoice
        booking_entry.save()
        return invoice

    def create_for_counterparty(self, counterparty: Entry, **kwargs) -> "Invoice|None":
        """
        Creates an Invoice instance for a given counterparty and associates unresolved BookingEntry objects with the
        newly created invoice.

        This method automatically finds all BookingEntry objects related to the counterparty that do not have an
        associated invoice and are not resolved, and updates them to link to the newly created Invoice.

        Args:
            counterparty (Entry): The counterparty for which to create the invoice.

        Returns:
            Invoice | None: The newly created Invoice instance associated with the given counterparty or None if no
                            Booking Entries can be invoiced.
        """
        booking_entries = BookingEntry.objects.filter(
            counterparty=counterparty,
            invoice__isnull=True,
            payment_date__isnull=True,
        )
        if not booking_entries.exists():
            return None

        title = kwargs.pop(
            "title",
            f"Invoice {counterparty.computed_str} {booking_entries.latest('reference_date').reference_date or ''}",
        )
        invoice_currency = kwargs.pop("invoice_currency", counterparty.entry_accounting_information.default_currency)
        invoice_type = kwargs.pop("type", counterparty.entry_accounting_information.default_invoice_type)
        backlinks = counterparty.entry_accounting_information.get_booking_entry_generator().merge_backlinks(
            booking_entries
        )

        invoice = super().create(
            counterparty=counterparty,
            title=title,
            invoice_currency=invoice_currency,
            backlinks=backlinks,
            invoice_type=invoice_type,
            **kwargs,
        )
        booking_entries.update(invoice=invoice)
        transaction.on_commit(lambda: refresh_complete_invoice_as_task.delay(invoice.pk))  # type: ignore
        return invoice

    def filter_for_user(self, user: User) -> QuerySet:
        """
        Filters invoices based on if the current user can see the counterparty.

        Args:
            user (User): The user for whom invoices need to be filtered.

        Returns:
            QuerySet: A filtered queryset.
        """

        if user.is_superuser or user.has_perm("wbaccounting.administrate_invoice"):
            return self

        if not user.has_perm("wbaccounting.view_invoice"):
            return self.none()

        return self.filter(
            Q(counterparty__entry_accounting_information__counterparty_is_private=False)
            | Q(counterparty__entry_accounting_information__exempt_users=user)
        )


class Invoice(WBModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        CANCELLED = "CANCELLED", "Cancelled"
        SENT = "SENT", "Sent"
        PAID = "PAID", "Paid"

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        permissions = (
            (
                "can_generate_invoice",
                "Can Generate Invoice",
            ),
            ("administrate_invoice", "Can administer Invoice"),
        )

        notification_types = [
            create_notification_type(
                "wbaccounting.invoice.notify_approval",
                "Invoice Approval Notification",
                "Sends a notification when something happens in a relevant article.",
                True,
                True,
                False,
            ),
        ]

    def __str__(self):
        return self.title

    objects = InvoiceDefaultQuerySet.as_manager()

    status = FSMField(default=Status.DRAFT, choices=Status.choices, verbose_name="Status")
    resolved = models.BooleanField(default=False, verbose_name="Resolved")

    title = models.CharField(max_length=255, verbose_name="Title")

    invoice_date = models.DateField(verbose_name="Invoice Date")
    reference_date = models.DateField(verbose_name="Reference Date", null=True, blank=True)
    payment_date = models.DateField(verbose_name="Payment Date", null=True, blank=True)

    invoice_currency = models.ForeignKey(
        "currency.Currency", related_name="invoices", on_delete=models.PROTECT, verbose_name="Curency"
    )

    counterparty = models.ForeignKey(
        "directory.Entry", related_name="accounting_invoices", on_delete=models.PROTECT, verbose_name="Counterparty"
    )

    text_above = models.TextField(null=True, blank=True)
    text_below = models.TextField(null=True, blank=True)

    invoice_type = models.ForeignKey(
        to="InvoiceType", null=True, verbose_name="Type", related_name="invoices", on_delete=models.PROTECT
    )
    gross_value = models.DecimalField(
        max_digits=16, decimal_places=4, null=True, blank=True, verbose_name="Gross Value"
    )
    net_value = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True, verbose_name="Net Value")

    backlinks = models.JSONField(null=True, blank=True)

    if TYPE_CHECKING:
        booking_entries: BookingEntryDefaultQuerySet

    def __init__(self, *args, **kwargs):
        super(Invoice, self).__init__(*args, **kwargs)
        if hasattr(self, "invoice_currency"):  # FDM instantiate model without any attribute
            self._original_invoice_currency = self.invoice_currency

    def save(self, *args, **kwargs):
        # If the invoice does not have a primary key yet, then it can't be set as a booking entries invoice
        if self.id:
            self.gross_value = self.booking_entries.all().aggregate(s=Sum("invoice_gross_value")).get("s", Decimal(0))
            self.net_value = self.booking_entries.all().aggregate(s=Sum("invoice_net_value")).get("s", Decimal(0))
            self.reference_date = self.booking_entries.all().aggregate(m=Max("reference_date")).get("m", None)

            transaction.on_commit(lambda: refresh_invoice_document_as_task.delay(self.pk))  # type: ignore
        super().save(*args, **kwargs)
        if self.invoice_currency != self._original_invoice_currency:
            refresh_complete_invoice_as_task.delay(self.id)

    @property
    def is_counterparty_invoice(self):
        return (self.net_value or 0) < 0

    @property
    def invoice_system_key(self) -> str:
        return f"invoice-{self.pk}"

    @property
    def invoice_document(self):
        return Document.get_for_object(self).filter(system_created=True, system_key=self.invoice_system_key).first()

    @property
    def invoice_company(self):
        global_preferences = global_preferences_registry.manager()
        if invoice_company_id := global_preferences["wbaccounting__invoice_company"]:
            return Company.objects.get(id=invoice_company_id)

    @transition(
        field=status,
        source=[Status.DRAFT],  # type: ignore
        target=Status.SUBMITTED,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbaccounting:invoice",),
                icon=WBIcon.SEND.icon,
                key="submit",
                label="Submit",
                action_label="Submitting",
                description_fields="<p>{{title}}</p><p>After Submitting, this invoice cannot be changed anymore.</p>",
            )
        },
    )
    def submit(self, by=None, description=None, **kwargs):
        for user in get_user_model().objects.filter(
            Q(user_permissions__codename="administrate_invoice")
            | Q(groups__permissions__codename="administrate_invoice")
        ):
            send_notification(
                code="wbaccounting.invoice.notify_approval",
                title="An invoice needs to be approved",
                body=f"An Invoice was submitted for approval ({self.title})",
                user=user,
                reverse_name="wbaccounting:invoice-detail",
                reverse_args=[self.pk],
            )

    @transition(
        field=status,
        source=[Status.SUBMITTED, Status.DRAFT],  # type: ignore
        target=Status.CANCELLED,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbaccounting:invoice",),
                icon=WBIcon.REJECT.icon,
                key="cancel",
                label="Cancel",
                action_label="Cancellation",
                description_fields="<p>{{title}}</p><p>After cancelling, this invoice cannot be used anymore.</p>",
            )
        },
    )
    def cancel(self, by=None, description=None, **kwargs):
        pass

    @transition(
        field=status,
        source=[Status.SUBMITTED],  # type: ignore
        target=Status.APPROVED,
        permission=lambda instance, user: user.has_perm("wbaccounting.administrate_invoice"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbaccounting:invoice",),
                icon=WBIcon.APPROVE.icon,
                key="approve",
                label="Approve",
                action_label="Approval",
                description_fields="<p>Are you sure you want to approve this invoice?</p>",
            )
        },
    )
    def approve(self, by=None, description=None, **kwargs):
        pass

    @transition(
        field=status,
        source=[Status.SUBMITTED],  # type: ignore
        target=Status.DRAFT,
        permission=lambda instance, user: user.has_perm("wbaccounting.administrate_invoice"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbaccounting:invoice",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label="Deny",
                action_label="Denial",
                description_fields="<p>Are you sure you want to deny this invoice?</p>",
            )
        },
    )
    def deny(self, by=None, description=None, **kwargs):
        pass

    @transition(
        field=status,
        source=[Status.APPROVED],  # type: ignore
        target=Status.SENT,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.SUCCESS,
                identifiers=("wbaccounting:invoice",),
                icon=WBIcon.GENERATE_NEXT.icon,
                key="send",
                label="Send",
                action_label="Sending",
                description_fields="<p>{{title}}</p>",
            )
        },
    )
    def send(self, by=None, description=None, **kwargs):
        pass

    def can_send(self):
        errors = dict()
        if not self.invoice_document:
            errors["status"] = [_("An invoice needs to be generated first.")]
        return errors

    @transition(
        field=status,
        source=[Status.SENT],  # type: ignore
        target=Status.PAID,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.SUCCESS,
                identifiers=("wbaccounting:invoice",),
                icon=WBIcon.DEAL_MONEY.icon,
                key="pay",
                label="Pay",
                action_label="Payment",
                description_fields="<p>{{title}}</p>",
            )
        },
    )
    def pay(self, by=None, description=None, **kwargs):
        pass

    def send_invoice_to_recipients(self):
        if invoice_document := self.invoice_document:
            entry_accounting_information = self.counterparty.entry_accounting_information
            if entry_accounting_information.send_mail:
                global_preferences = global_preferences_registry.manager()
                from_email = global_preferences["wbaccounting__default_from_email_address"]
                context = {"invoice": self.get_context(), "entry": self.counterparty}

                rendered_subject = Template(entry_accounting_information.email_subject).render(Context(context))
                rendered_body = Template(entry_accounting_information.email_body).render(Context(context))

                to_emails = list(entry_accounting_information.email_to.values_list("address", flat=True))
                cc_emails = list(entry_accounting_information.email_cc.values_list("address", flat=True))
                bcc_emails = list(entry_accounting_information.email_bcc.values_list("address", flat=True))

                invoice_document.send_email(
                    to_emails,
                    as_link=False,
                    subject=rendered_subject,
                    from_email=from_email,
                    body=rendered_body,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                )

    # Other methods
    def refresh_invoice_document(self, override_status=False):
        if self.status == self.Status.DRAFT or override_status:
            invoice = generate_file(self)
            file_name = f"{slugify(self.title)}.pdf"
            document_file = BytesIO(invoice)
            document_type, created = DocumentType.objects.get_or_create(name="invoice")
            document, created = Document.objects.update_or_create(
                document_type=document_type,
                system_created=True,
                system_key=self.invoice_system_key,
                defaults={
                    "name": f"Invoice: {self.title}",
                    "description": f"Invoice for {self.counterparty}.",
                    "file": File(document_file, file_name),
                },
            )
            document.link(self)

    def get_permissions_for_user_and_document(self, user, document, created=None) -> list[tuple[str, bool]]:
        # if the document is the invoice document, we want to assign certain permissions
        if document.system_created and self.invoice_system_key == document.system_key:
            if user.is_superuser:
                return []

            entry_info = self.counterparty.entry_accounting_information
            has_view_permission = user.has_perm("wbaccounting.view_invoice")

            if entry_info.external_invoice_users.filter(id=user.id).exists():
                return [("documents.view_document", False)]

            is_access_allowed = has_view_permission and (
                not entry_info.counterparty_is_private or user in entry_info.exempt_users.all()
            )
            has_admin_permission = user.has_perm("wbaccounting.administrate_invoice")

            if is_access_allowed or has_admin_permission:
                return [("documents.view_document", False)]
        return []

    def get_context(self) -> dict:
        return {
            "title": self.title,
            "counterparty": self.counterparty.computed_str,
            "total_net_value": format_invoice_number(self.net_value),
            "total_gross_value": format_invoice_number(self.gross_value),
            "text_above": self.text_above,
            "text_below": self.text_below,
            "invoice_date": self.invoice_date.strftime("%d.%m.%Y"),
            "currency": self.invoice_currency,
            "invoice": self,
        }

    @classmethod
    def get_endpoint_basename(cls):
        return "wbaccounting:invoice"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbaccounting:invoicerepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{title}} ({{invoice_date}})"


@receiver(pre_save, sender=Invoice)
def post_save_handle_processor(sender, instance, **kwargs):
    if (
        instance.status == Invoice.Status.APPROVED
        and instance.invoice_type
        and (processor_path := instance.invoice_type.processor)
    ):
        with suppress(ModuleNotFoundError):
            processor = import_from_dotted_path(processor_path)
            processor(instance)
            instance.status = instance.Status.SENT
