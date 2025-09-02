from django.db.models import F, QuerySet
from wbcore import viewsets

from wbaccounting.models import Transaction
from wbaccounting.serializers import (
    TransactionModelSerializer,
    TransactionRepresentationSerializer,
)
from wbaccounting.viewsets.display import TransactionDisplayConfig


class TransactionModelViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionModelSerializer
    search_fields = ("bank_account__isin", "from_bank_account__isin", "to_bank_account__isin")
    ordering = ordering_fields = ("booking_date", "value", "id")
    display_config_class = TransactionDisplayConfig

    def get_queryset(self) -> QuerySet[Transaction]:
        return (
            super()
            .get_queryset()
            .filter_for_user(user=self.request.user)
            .annotate(bank_account_currency_symbol=F("bank_account__currency__symbol"))
        )


class TransactionRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = TransactionRepresentationSerializer
    queryset = Transaction.objects.all()
    search_fields = ("bank_account__isin", "from_bank_account__isin", "to_bank_account__isin")
    ordering = ordering_fields = ("booking_date", "value", "id")

    def get_queryset(self) -> QuerySet[Transaction]:
        return super().get_queryset().filter_for_user(user=self.request.user)
