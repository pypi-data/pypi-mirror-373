from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext as _
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.models import WBModel

from wbaccounting.io.handlers.transactions import TransactionImportHandler

if TYPE_CHECKING:
    from wbcore.contrib.authentication.models import User


class TransactionQuerySet(models.QuerySet):
    def filter_for_user(self, user: "User") -> models.QuerySet["Transaction"]:
        if user.is_superuser:
            return self

        return self.filter(bank_account__access__user_account__in=[user])


class Transaction(ImportMixin, WBModel):
    """A transaction represents a bank transfer of some funds in some currency from one Bank Account to another one."""

    import_export_handler_class = TransactionImportHandler

    booking_date = models.DateField(verbose_name=_("Booking Date"))
    value_date = models.DateField(verbose_name=_("Value Date"))

    bank_account = models.ForeignKey(
        to="directory.BankingContact",
        related_name="wbaccounting_transactions",
        on_delete=models.PROTECT,
        verbose_name=_("Linked Bank Account"),
    )
    from_bank_account = models.ForeignKey(
        to="directory.BankingContact",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("Source Bank Account"),
    )
    to_bank_account = models.ForeignKey(
        to="directory.BankingContact",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("Target Bank Account"),
    )
    currency = models.ForeignKey(
        to="currency.Currency",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("Currency"),
    )
    fx_rate = models.DecimalField(default=Decimal(1), max_digits=10, decimal_places=4, verbose_name=_("FX Rate"))
    value_local_ccy = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True, verbose_name=_("Value (Local Currency)")
    )
    value = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, verbose_name=_("Value"))
    description = models.TextField(default="")
    prenotification = models.BooleanField(
        default=False,
        verbose_name=_("Prenotification"),
        help_text=_("This field indicates that this transaction will happen sometime in the future."),
    )
    _hash = models.CharField(max_length=64, null=True, blank=True)

    objects = TransactionQuerySet.as_manager()

    def save(self, *args, **kwargs):
        # We make sure that the relationship between value and
        # value_local_ccy stays consistant while prefering value
        if self.value is not None:
            self.value_local_ccy = self.value / self.fx_rate

        elif self.value_local_ccy is not None:
            self.value = self.value_local_ccy * self.fx_rate

        # If value date is not set we set it to the booking date
        if self.value_date is None:
            self.value_date = self.booking_date

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.booking_date:%d.%m.%Y}: {self.value:.2f}"

    class Meta:
        default_related_name = "transactions"
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbaccounting:transaction"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbaccounting:transactionrepresentation-list"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{booking_date}}: {{value}}"
