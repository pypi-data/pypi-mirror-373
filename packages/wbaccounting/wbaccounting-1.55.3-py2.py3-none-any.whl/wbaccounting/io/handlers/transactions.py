from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models import Value
from django.db.models.functions import Replace
from wbcore.contrib.currency.import_export.handlers import CurrencyImportHandler
from wbcore.contrib.directory.models import BankingContact
from wbcore.contrib.io.imports import ImportExportHandler


class TransactionImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbaccounting.Transaction"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currency_handler = CurrencyImportHandler(self.import_source)

    def _deserialize(self, data: dict[str, Any]):
        data["currency"] = self.currency_handler.process_object({"key": data["currency"]}, read_only=True)[0]
        data["bank_account"] = BankingContact.objects.annotate(
            stripped_iban=Replace("iban", Value(" "), Value(""))
        ).get(stripped_iban=data["bank_account"].replace(" ", ""))
        data["value"] = Decimal(data["value"])
        return super()._deserialize(data)

    def _get_instance(self, data: dict[str, Any], history: models.QuerySet | None = None, **kwargs) -> Any | None:
        if _hash := data.get("_hash", None):
            qs = self.model.objects.filter(_hash=_hash)
            if qs.exists():
                return qs.first()
        return super()._get_instance(data, history, **kwargs)
