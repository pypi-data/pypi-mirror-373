from django.db import models
from wbcore.models import WBModel


class InvoiceType(WBModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    processor = models.CharField(max_length=128, null=True, blank=True, verbose_name="Processor")

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbaccounting:invoicetype"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbaccounting:invoicetyperepresentation-list"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"

    class Meta:  # type: ignore
        verbose_name = "Invoice Type"
        verbose_name_plural = "Invoice Types"
