from wbcore import serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.serializers import BankingContactRepresentationSerializer

from wbaccounting.models import Transaction


class TransactionRepresentationSerializer(serializers.RepresentationSerializer):
    _bank_account = BankingContactRepresentationSerializer(source="bank_account")
    _detail = serializers.HyperlinkField(reverse_name="wbaccounting:transaction-detail")

    class Meta:
        model = Transaction
        fields = ("id", "booking_date", "bank_account", "_bank_account", "value", "_detail")


class TransactionModelSerializer(serializers.ModelSerializer):
    _bank_account = BankingContactRepresentationSerializer(source="bank_account")
    _from_bank_account = BankingContactRepresentationSerializer(source="from_bank_account")
    _to_bank_account = BankingContactRepresentationSerializer(source="to_bank_account")
    _currency = CurrencyRepresentationSerializer(source="currency")
    bank_account_currency_symbol = serializers.CharField(read_only=True)

    class Meta:
        model = Transaction
        decorators = {
            "value": serializers.decorator(
                decorator_type="text", position="left", value="{{bank_account_currency_symbol}}"
            ),
            "value_local_ccy": serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
        }
        fields = (
            "id",
            "booking_date",
            "value_date",
            "bank_account",
            "_bank_account",
            "from_bank_account",
            "_from_bank_account",
            "to_bank_account",
            "_to_bank_account",
            "currency",
            "_currency",
            "fx_rate",
            "value_local_ccy",
            "description",
            "value",
            "bank_account_currency_symbol",
        )
