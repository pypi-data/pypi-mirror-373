import factory
import pytest
from django.test import RequestFactory
from rest_framework.reverse import reverse
from wbaccounting.models import BookingEntry
from wbaccounting.serializers import (
    BookingEntryModelSerializer,
    BookingEntryRepresentationSerializer,
)


@pytest.mark.django_db
class TestBookingEntryModelSerializer:
    def test_serialize(self, booking_entry: BookingEntry):
        serializer = BookingEntryModelSerializer(booking_entry)
        assert isinstance(serializer.data, dict)

    def test_serialize_contains_keys(self, booking_entry: BookingEntry):
        serializer = BookingEntryModelSerializer(booking_entry)
        assert (
            "id",
            "title",
            "booking_date",
            "due_date",
            "payment_date",
            "reference_date",
            "net_value",
            "gross_value",
            "vat",
            "invoice_net_value",
            "invoice_gross_value",
            "invoice_fx_rate",
            "currency",
            "_currency",
            "counterparty",
            "_counterparty",
            "invoice",
            "_invoice",
            "invoice_currency",
            "_additional_resources",
            "_buttons",
        ) == tuple(
            serializer.data.keys()
        )  # type: ignore

    @pytest.mark.parametrize("decorator", ["net_value", "gross_value"])
    def test_serialize_decorators(self, booking_entry: BookingEntry, rf: RequestFactory, decorator: str):
        serializer = BookingEntryModelSerializer(booking_entry)
        _, representation = serializer[decorator].get_representation(rf.get("/"), decorator)  # type: ignore
        assert representation["decorators"] == [{"position": "left", "type": "text", "value": "{{_currency.symbol}}"}]

    def test_deserialize(self, booking_entry_factory, entry, currency, invoice):
        data = factory.build(dict, FACTORY_CLASS=booking_entry_factory)
        data["currency"] = currency.pk
        data["counterparty"] = entry.pk
        data["invoice"] = invoice.pk
        serializer = BookingEntryModelSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestBookingEntryRepresentationSerializer:
    def test_serialize(self, booking_entry: BookingEntry):
        serializer = BookingEntryRepresentationSerializer(booking_entry)
        assert serializer.data == {
            "id": booking_entry.pk,
            "title": booking_entry.title,
            "_detail": reverse("wbaccounting:bookingentry-detail", args=[booking_entry.pk]),
        }
