import factory
import pytest
from rest_framework.reverse import reverse
from wbaccounting.models import Transaction
from wbaccounting.serializers import (
    TransactionModelSerializer,
    TransactionRepresentationSerializer,
)
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.serializers import BankingContactRepresentationSerializer


@pytest.mark.django_db
class TestTransactionModelSerializer:
    def test_serialize(self, transaction: Transaction):
        # We need to add the currency symbol, which is usually done through the queryset in the viewset
        transaction.bank_account_currency_symbol = transaction.bank_account.currency.symbol  # type: ignore

        serializer = TransactionModelSerializer(transaction)
        assert transaction.currency is not None
        assert transaction.fx_rate is not None
        assert transaction.value_local_ccy is not None
        assert transaction.value is not None
        assert serializer.data == {
            "id": transaction.pk,
            "description": transaction.description,
            "booking_date": transaction.booking_date.strftime("%Y-%m-%d"),
            "value_date": transaction.value_date.strftime("%Y-%m-%d"),
            "bank_account": transaction.bank_account.id,
            "_bank_account": BankingContactRepresentationSerializer(transaction.bank_account).data,
            "from_bank_account": transaction.bank_account.id,
            "_from_bank_account": BankingContactRepresentationSerializer(transaction.bank_account).data,
            "to_bank_account": transaction.bank_account.id,
            "_to_bank_account": BankingContactRepresentationSerializer(transaction.bank_account).data,
            "currency": transaction.currency.pk,
            "_currency": CurrencyRepresentationSerializer(transaction.currency).data,
            "fx_rate": str(round(transaction.fx_rate, 4)),
            "value_local_ccy": str(round(transaction.value_local_ccy, 2)),
            "value": str(round(transaction.value, 2)),
            "bank_account_currency_symbol": transaction.bank_account.currency.symbol,
        }

    def test_deserialize(self, transaction_factory, banking_contact):
        data = factory.build(
            dict,
            FACTORY_CLASS=transaction_factory,
            bank_account=banking_contact,
        )

        data["bank_account"] = data["bank_account"].id
        data["from_bank_account"] = data["from_bank_account"].id
        data["to_bank_account"] = data["to_bank_account"].id
        data["currency"] = data["currency"].id
        data["value"] = round(data["value"], 2)

        serializer = TransactionModelSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestTransactionRepresentationSerializer:
    def test_serialize(self, transaction: Transaction):
        serializer = TransactionRepresentationSerializer(transaction)
        assert transaction.value is not None
        assert serializer.data == {
            "id": transaction.pk,
            "booking_date": transaction.booking_date.strftime("%Y-%m-%d"),
            "bank_account": transaction.bank_account.id,
            "_bank_account": BankingContactRepresentationSerializer(transaction.bank_account).data,
            "value": str(round(transaction.value, 2)),
            "_detail": reverse("wbaccounting:transaction-detail", args=[transaction.pk]),
        }
