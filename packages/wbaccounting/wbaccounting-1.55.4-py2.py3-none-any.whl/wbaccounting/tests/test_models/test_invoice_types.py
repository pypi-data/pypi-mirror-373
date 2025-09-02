import pytest
from wbaccounting.models import InvoiceType


@pytest.mark.django_db
class TestInvoiceType:
    def test_str(self, invoice_type: InvoiceType):
        assert str(invoice_type) == invoice_type.name

    @pytest.mark.parametrize(
        "method,return_value",
        [
            ("get_endpoint_basename", "wbaccounting:invoicetype"),
            ("get_representation_value_key", "id"),
            ("get_representation_label_key", "{{name}}"),
            ("get_representation_endpoint", "wbaccounting:invoicetyperepresentation-list"),
        ],
    )
    def test_wbmodel_methods(self, method: str, return_value: str):
        assert getattr(InvoiceType, method)() == return_value

