import pytest
from wbaccounting.models import Transaction


@pytest.mark.django_db
class TestTransaction:
    def test_str(self, transaction: Transaction):
        assert str(transaction) == f"{transaction.booking_date:%d.%m.%Y}: {transaction.value:.2f}"

    @pytest.mark.parametrize(
        "method,return_value",
        [
            ("get_endpoint_basename", "wbaccounting:transaction"),
            ("get_representation_value_key", "id"),
            ("get_representation_label_key", "{{booking_date}}: {{value}}"),
            ("get_representation_endpoint", "wbaccounting:transactionrepresentation-list"),
        ],
    )
    def test_wbmodel_methods(self, method: str, return_value: str):
        assert getattr(Transaction, method)() == return_value

    def test_no_value_date(self, transaction_no_value_date: Transaction):
        assert transaction_no_value_date.value_date == transaction_no_value_date.booking_date

    def test_value(self, transaction: Transaction):
        assert pytest.approx(transaction.value_local_ccy) == transaction.value

    def test_value_different_fx_rate(self, transaction_fx: Transaction):
        tfx = transaction_fx
        assert tfx.value is not None
        assert pytest.approx(tfx.value / tfx.fx_rate) == pytest.approx(tfx.value_local_ccy)

    def test_local_ccy(self, transaction_local_ccy: Transaction):
        tlc = transaction_local_ccy
        assert pytest.approx(tlc.value) == tlc.value_local_ccy

    def test_local_ccy_different_fx_rate(self, transaction_local_ccy_fx: Transaction):
        tlcf = transaction_local_ccy_fx
        assert tlcf.value_local_ccy is not None
        assert pytest.approx(tlcf.value) == (tlcf.value_local_ccy * tlcf.fx_rate)
