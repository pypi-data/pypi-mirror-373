from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import pandas as pd
from django.db.models import DateField, F, Sum, Value
from wbcore.pandas import fields as pf
from wbcore.pandas.views import PandasAPIViewSet

from wbaccounting.models import Transaction
from wbaccounting.viewsets.display import FutureCashFlowDisplayConfig

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.db.models.query import ValuesQuerySet
    from rest_framework.request import Request


class FutureCashFlowPandasAPIViewSetMixin(PandasAPIViewSet):
    DATE_COL_START = 0
    BOLD = False

    queryset = Transaction.objects.none()
    display_config_class = FutureCashFlowDisplayConfig

    def get_pandas_fields(self, request) -> pf.PandasFields:
        fields = self.get_dataframe(request, self.get_queryset()).columns[self.DATE_COL_START :]
        return pf.PandasFields(
            fields=[
                pf.PKField(key="bank_account__id", label="ID"),
                pf.CharField(key="_group_key", label="GROUPKEY"),
                pf.CharField(key="bank_account__iban", label="IBAN"),
                pf.CharField(key="bank_account__currency__symbol", label="Currency"),
                *[
                    pf.FloatField(
                        key=field,
                        label=datetime.strptime(field, "%Y-%m-%d").strftime("%d.%m.%Y"),
                        display_mode=pf.DisplayMode.SHORTENED,
                    )
                    for field in fields
                ],
            ]
        )


class FutureCashFlowPandasAPIViewSet(FutureCashFlowPandasAPIViewSetMixin):
    DATE_COL_START = 4
    BOLD = True

    def get_queryset(self) -> "ValuesQuerySet[Transaction, Any]":
        base_queryset = Transaction.objects.filter_for_user(self.request.user)
        if banking_contact_ids := self.request.GET.get("banking_contact"):
            base_queryset = base_queryset.filter(bank_account__id__in=banking_contact_ids.split(","))

        past_transactions = (
            base_queryset.filter(prenotification=False)
            .values("bank_account__id")
            .annotate(
                value_date=Value(date.today(), output_field=DateField()),
                balance=Sum("value"),
                _group_key=F("bank_account__id"),
            )
            .values(
                "bank_account__id",
                "bank_account__iban",
                "bank_account__currency__symbol",
                "value_date",
                "balance",
                "_group_key",
            )
        )

        future_transactions = (
            base_queryset.filter(prenotification=True, value_date__gt=date.today())
            .values("bank_account__id", "value_date")
            .annotate(balance=Sum("value"), _group_key=F("bank_account__id"))
            .values(
                "bank_account__id",
                "bank_account__iban",
                "bank_account__currency__symbol",
                "value_date",
                "balance",
                "_group_key",
            )
        )

        return past_transactions.union(future_transactions)

    def get_dataframe(
        self, request: "Request", queryset: "ValuesQuerySet[Transaction, Any]", **kwargs
    ) -> pd.DataFrame:
        if not queryset.exists():
            return pd.DataFrame()
        df = (
            pd.DataFrame(queryset)
            .pivot_table(
                index=["bank_account__id", "bank_account__iban", "bank_account__currency__symbol", "_group_key"],
                columns=["value_date"],
                values="balance",
            )
            .astype(float)
            .fillna(0)
            .cumsum(axis=1)
        )
        df.columns = df.columns.astype(str)
        return df.reset_index()


class FutureCashFlowTransactionsPandasAPIViewSet(FutureCashFlowPandasAPIViewSetMixin):
    DATE_COL_START = 2

    def get_queryset(self):
        queryset = Transaction.objects.filter(prenotification=True, value_date__gt=date.today())
        if bank_account := self.request.GET.get("bank_account", None):
            return queryset.filter(bank_account_id=bank_account)
        return queryset

    def get_dataframe(self, request: "Request", queryset: "QuerySet[Transaction]", **kwargs) -> pd.DataFrame:
        df = pd.DataFrame(
            queryset.values_list("description", "value", "value_date"), columns=["description", "value", "value_date"]
        ).pivot_table(index=["description"], columns=["value_date"], values="value")
        df.columns = df.columns.astype(str)
        df = df.reset_index()
        df = df.rename(columns={"description": "bank_account__iban"})
        df.insert(0, "bank_account__id", df["bank_account__iban"])
        return df
