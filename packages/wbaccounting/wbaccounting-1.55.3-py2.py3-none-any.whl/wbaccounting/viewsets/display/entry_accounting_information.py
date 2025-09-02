from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import Display, default
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class EntryAccountingInformationDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="entry", label="CRM", width=400),
                dp.Field(key="tax_id", label="Tax ID"),
                dp.Field(key="vat", label="VAT", width=100),
                dp.Field(key="default_currency", label="Currency", width=100),
                dp.Field(key="send_mail", label="Send Mail", width=100),
            ],
            formatting=[
                dp.Formatting(
                    column="counterparty_is_private",
                    formatting_rules=[dp.FormattingRule(condition=("==", True), style={"backgroundColor": "#708090"})],
                )
            ],
            legends=[
                dp.Legend(
                    key="counterparty_is_private",
                    items=[dp.LegendItem(icon="#708090", label="Private Counterparty", value=True)],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        return dp.Display(
            pages=[
                dp.Page(
                    title="General Information",
                    layouts={
                        default(): dp.Layout(
                            grid_template_areas=[
                                ["entry", "booking_entry_generator"],
                                ["counterparty_is_private", "exempt_users"],
                                ["default_currency", "tax_id"],
                                ["vat", "default_invoice_type"],
                                ["external_invoice_users", "."],
                            ],
                        )
                    },
                ),
                dp.Page(
                    title="E-Mail Settings",
                    layouts={
                        dp.default(): dp.Layout(
                            grid_template_areas=[
                                ["send_mail", "."],
                                ["email_to", "."],
                                ["email_cc", "."],
                                ["email_bcc", "."],
                                ["email_subject", "."],
                                [repeat_field(2, "email_body")],
                            ],
                            grid_template_columns=["600px", "1fr"],
                        )
                    },
                ),
                dp.Page(
                    title="Invoices",
                    layouts={
                        default(): dp.Layout(
                            grid_template_areas=[
                                ["invoices"],
                            ],
                            grid_template_rows=["600px"],
                            inlines=[dp.Inline(key="invoices", endpoint="invoices")],
                        )
                    },
                ),
                dp.Page(
                    title="Bookings",
                    layouts={
                        default(): dp.Layout(
                            grid_template_areas=[
                                ["bookingentries"],
                            ],
                            grid_template_rows=["600px"],
                            inlines=[dp.Inline(key="bookingentries", endpoint="bookingentries")],
                        )
                    },
                ),
            ]
        )
