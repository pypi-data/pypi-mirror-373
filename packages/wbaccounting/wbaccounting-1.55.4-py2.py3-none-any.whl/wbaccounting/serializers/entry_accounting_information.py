from decimal import Decimal

from django.db.models import Q
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.authentication.models import User
from wbcore.contrib.authentication.serializers import UserRepresentationSerializer
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.serializers import (
    CompanyModelSerializer,
    EmailContactRepresentationSerializer,
    EntryModelSerializer,
    EntryRepresentationSerializer,
    PersonModelSerializer,
)
from wbcore.signals import add_instance_additional_resource

from wbaccounting.generators.base import get_all_booking_entry_choices
from wbaccounting.models import EntryAccountingInformation
from wbaccounting.serializers import InvoiceTypeRepresentationSerializer


class EntryAccountingInformationRepresentationSerializer(serializers.RepresentationSerializer):
    entry_repr = serializers.CharField(source="entry.computed_str", read_only=True)

    class Meta:
        model = EntryAccountingInformation
        fields = (
            "id",
            "entry_repr",
        )


class EntryAccountingInformationModelSerializer(serializers.ModelSerializer):
    _entry = EntryRepresentationSerializer(source="entry")
    _default_currency = CurrencyRepresentationSerializer(source="default_currency")
    _default_invoice_type = InvoiceTypeRepresentationSerializer(source="default_invoice_type")
    vat = serializers.DecimalField(percent=True, required=False, max_digits=6, decimal_places=4, default=Decimal(0))
    _exempt_users = UserRepresentationSerializer(source="exempt_users", many=True)

    _email_to = EmailContactRepresentationSerializer(source="email_to", many=True, ignore_filter=True)
    _email_cc = EmailContactRepresentationSerializer(source="email_cc", many=True, ignore_filter=True)
    _email_bcc = EmailContactRepresentationSerializer(source="email_bcc", many=True, ignore_filter=True)
    booking_entry_generator = serializers.ChoiceField(
        choices=list(get_all_booking_entry_choices()), required=False, allow_null=True
    )

    _external_invoice_users = UserRepresentationSerializer(source="external_invoice_users", many=True)

    @serializers.register_only_instance_resource()
    def generate(self, instance, request, user, **kwargs):
        generators = {}

        if instance.booking_entry_generator and (
            user.is_superuser or user.has_perm("wbaccounting.can_generate_booking_entries")
        ):
            generators["generate_booking_entries"] = reverse(
                "wbaccounting:entryaccountinginformation-generate-booking-entries",
                args=[instance.id],
                request=request,
            )

        if user.is_superuser or user.has_perm("wbaccounting.can_generate_invoice"):
            if instance.entry.booking_entries.filter(Q(invoice__isnull=True) & Q(payment_date__isnull=True)).exists():
                generators["invoice_booking_entries"] = reverse(
                    "wbaccounting:entryaccountinginformation-invoice-booking-entries",
                    args=[instance.id],
                    request=request,
                )

        return generators

    @serializers.register_only_instance_resource()
    def inline_lists(self, instance, request, user, **kwargs):
        return {
            "invoices": reverse(
                "wbaccounting:entryaccountinginformation-invoice-list",
                args=[instance.id],
                request=request,
            ),
            "bookingentries": reverse(
                "wbaccounting:entryaccountinginformation-bookingentry-list",
                args=[instance.id],
                request=request,
            ),
        }

    class Meta:
        model = EntryAccountingInformation

        percent_fields = ["vat"]
        fields = (
            "id",
            "entry",
            "_entry",
            "tax_id",
            "vat",
            "default_currency",
            "_default_currency",
            "default_invoice_type",
            "_default_invoice_type",
            "email_to",
            "email_cc",
            "email_bcc",
            "_email_to",
            "_email_cc",
            "_email_bcc",
            "email_subject",
            "email_body",
            "send_mail",
            "counterparty_is_private",
            "exempt_users",
            "_exempt_users",
            "booking_entry_generator",
            "external_invoice_users",
            "_external_invoice_users",
            "_additional_resources",
        )

    def validate(self, data: dict) -> dict:
        counterparty_is_private: bool | None = data.get(
            "counterparty_is_private", self.instance.counterparty_is_private if self.instance else None
        )
        exempt_users: list[User] | None = data.get(
            "exempt_users", list(self.instance.exempt_users.all()) if self.instance else None
        )

        if exempt_users and not counterparty_is_private:
            raise ValidationError({"exempt_users": "You can only select exempt users for private counterparties."})

        return super().validate(data)


@receiver(add_instance_additional_resource, sender=CompanyModelSerializer)
@receiver(add_instance_additional_resource, sender=PersonModelSerializer)
@receiver(add_instance_additional_resource, sender=EntryModelSerializer)
def entry_adding_additional_resource(sender, serializer, instance, request, user, **kwargs):
    if hasattr(instance, "entry_accounting_information"):
        entry_accounting_information = instance.entry_accounting_information
        if entry_accounting_information:
            return {
                "accounting-information": reverse(
                    "wbaccounting:entryaccountinginformation-detail",
                    args=[entry_accounting_information.id],
                    request=request,
                )
            }
    return {}
