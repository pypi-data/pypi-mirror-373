import factory
import pytest
from rest_framework.reverse import reverse
from wbaccounting.models import InvoiceType
from wbaccounting.serializers import (
    InvoiceTypeModelSerializer,
    InvoiceTypeRepresentationSerializer,
)


@pytest.mark.django_db
class TestInvoiceTypeModelSerializer:
    def test_serialize(self, invoice_type: InvoiceType):
        serializer = InvoiceTypeModelSerializer(invoice_type)
        assert serializer.data == {
            "id": invoice_type.pk,
            "name": invoice_type.name,
            "processor": invoice_type.processor,
        }

    def test_deserialize(self, invoice_type_factory):
        data = factory.build(dict, FACTORY_CLASS=invoice_type_factory)
        serializer = InvoiceTypeModelSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestInvoiceTypeRepresentationSerializer:
    def test_serialize(self, invoice_type: InvoiceType):
        serializer = InvoiceTypeRepresentationSerializer(invoice_type)
        assert serializer.data == {
            "id": invoice_type.pk,
            "name": invoice_type.name,
            "_detail": reverse("wbaccounting:invoicetype-detail", args=[invoice_type.pk]),
        }
