from django.utils.translation import gettext as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class TransactionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="booking_date", label=_("Booking Date"), width=150),
                dp.Field(key="value_date", label=_("Value Date"), width=150),
                dp.Field(key="bank_account", label=_("Bank Account"), width=450),
                # dp.Field(key="from_bank_account", label=_("Source"), width=300),
                # dp.Field(key="to_bank_account", label=_("Target"), width=300),
                dp.Field(key="value_local_ccy", label=_("Value (Local)"), width=150),
                dp.Field(key="value", label=_("Value"), width=150),
                dp.Field(key="description", label=_("Description"), width=450),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["booking_date", "value_date"],
                ["bank_account", "."],
                ["from_bank_account", "to_bank_account"],
                ["value", "currency"],
                ["value_local_ccy", "fx_rate"],
                ["description", "description"],
            ]
        )
