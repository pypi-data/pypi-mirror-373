from typing import Optional

from rest_framework.reverse import reverse
from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbaccounting.models import Invoice

COLOR_DRAFT = "rgb(255,249,196)"
COLOR_SUBMITTED = "rgb(51, 204, 255)"
COLOR_SENT = "rgb(255, 153, 102)"
COLOR_PAID = "rgb(214, 229, 145)"


class InvoiceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="status", label="Status"),
                dp.Field(key="type", label="Type"),
                dp.Field(key="counterparty", label="Counterparty"),
                dp.Field(key="title", label="Title"),
                dp.Field(key="invoice_date", label="Invoice Date"),
                dp.Field(key="reference_date", label="Reference Date"),
                dp.Field(key="gross_value", label="Gross Value"),
                dp.Field(key="net_value", label="Net Value"),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=COLOR_DRAFT,
                            label=Invoice.Status.DRAFT.label,
                            value=Invoice.Status.DRAFT.name,
                        ),
                        dp.LegendItem(
                            icon=COLOR_SUBMITTED,
                            label=Invoice.Status.SUBMITTED.label,
                            value=Invoice.Status.SUBMITTED.name,
                        ),
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=Invoice.Status.APPROVED.label,
                            value=Invoice.Status.APPROVED.name,
                        ),
                        dp.LegendItem(
                            icon=COLOR_SENT,
                            label=Invoice.Status.SENT.label,
                            value=Invoice.Status.SENT.name,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=Invoice.Status.PAID.label,
                            value=Invoice.Status.PAID.name,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREY.value,
                            label=Invoice.Status.CANCELLED.label,
                            value=Invoice.Status.CANCELLED.name,
                        ),
                    ],
                )
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": COLOR_DRAFT},
                            condition=("==", Invoice.Status.DRAFT.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": COLOR_SUBMITTED},
                            condition=("==", Invoice.Status.SUBMITTED.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=("==", Invoice.Status.APPROVED.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": COLOR_SENT},
                            condition=("==", Invoice.Status.SENT.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", Invoice.Status.PAID.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREY.value},
                            condition=("==", Invoice.Status.CANCELLED.name),
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "status")],
                ["title", "invoice_type"],
                ["counterparty", "reference_date"],
                ["invoice_date", "invoice_currency"],
                ["text_above", "text_below"],
                [repeat_field(2, "booking_entry_section")],
            ],
            [
                create_simple_section(
                    "booking_entry_section", "Booking Entries", [["bookingentries"]], "bookingentries", collapsed=True
                )
            ],
        )


class ConsolidatedInvoiceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="group", label="Group", pinned="left"),
                dp.Field(key="value", label="Value"),
            ],
            tree=True,
            tree_group_field="group",
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_depth=None,  # We want lookup to be concatenated
                    filter_key="lookup",
                    list_endpoint=reverse(
                        "wbaccounting:consolidated-invoice-list",
                        args=[],
                        request=self.request,
                    ),
                )
            ],
            legends=[
                dp.Legend(
                    key="status",
                    label="Lowest Status",
                    items=[
                        dp.LegendItem(
                            icon=COLOR_DRAFT,
                            label=Invoice.Status.DRAFT.label,
                            value=Invoice.Status.DRAFT.name,
                        ),
                        dp.LegendItem(
                            icon=COLOR_SUBMITTED,
                            label=Invoice.Status.SUBMITTED.label,
                            value=Invoice.Status.SUBMITTED.name,
                        ),
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=Invoice.Status.APPROVED.label,
                            value=Invoice.Status.APPROVED.name,
                        ),
                        dp.LegendItem(
                            icon=COLOR_SENT,
                            label=Invoice.Status.SENT.label,
                            value=Invoice.Status.SENT.name,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=Invoice.Status.PAID.label,
                            value=Invoice.Status.PAID.name,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREY.value,
                            label=Invoice.Status.CANCELLED.label,
                            value=Invoice.Status.CANCELLED.name,
                        ),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="num_paid",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": COLOR_PAID},
                            condition=(">", 0),
                        )
                    ],
                ),
                dp.Formatting(
                    column="num_sent",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": COLOR_SENT},
                            condition=(">", 0),
                        )
                    ],
                ),
                dp.Formatting(
                    column="num_submitted",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": COLOR_SUBMITTED},
                            condition=(">", 0),
                        )
                    ],
                ),
                dp.Formatting(
                    column="num_draft",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": COLOR_DRAFT},
                            condition=(">", 0),
                        )
                    ],
                ),
            ],
        )
