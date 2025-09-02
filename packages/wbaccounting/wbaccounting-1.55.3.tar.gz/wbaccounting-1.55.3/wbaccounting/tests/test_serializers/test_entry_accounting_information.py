import factory
import pytest
from wbaccounting.models import EntryAccountingInformation
from wbaccounting.serializers import (
    EntryAccountingInformationModelSerializer,
    EntryAccountingInformationRepresentationSerializer,
)


@pytest.mark.django_db
class TestEntryAccountingInformationModelSerializer:
    def test_serialize(self, entry_accounting_information: EntryAccountingInformation):
        serializer = EntryAccountingInformationModelSerializer(entry_accounting_information)
        assert isinstance(serializer.data, dict)

    #
    def test_serialize_contains_keys(self, entry_accounting_information: EntryAccountingInformation):
        serializer = EntryAccountingInformationModelSerializer(entry_accounting_information)
        assert (
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
        ) == tuple(
            serializer.data.keys()
        )  # type: ignore

    def test_deserialize(self, entry_accounting_information_factory, entry, currency):
        data = factory.build(dict, FACTORY_CLASS=entry_accounting_information_factory)
        data["entry"] = entry.pk
        data["default_currency"] = currency.pk
        serializer = EntryAccountingInformationModelSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestEntryAccountingInformationRepresentationSerializer:
    def test_serialize(self, entry_accounting_information: EntryAccountingInformation):
        serializer = EntryAccountingInformationRepresentationSerializer(entry_accounting_information)
        assert serializer.data == {
            "id": entry_accounting_information.pk,
            "entry_repr": entry_accounting_information.entry.computed_str,
        }
