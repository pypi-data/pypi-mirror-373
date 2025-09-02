from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class InvoiceBaseButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {bt.HyperlinkButton(key="invoice_file", label="Invoice", icon=WBIcon.DOCUMENT.icon)}

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()


class InvoiceButtonConfig(InvoiceBaseButtonConfig):
    def get_custom_buttons(self) -> set:
        buttons = super().get_custom_buttons()
        if not (self.view.kwargs.get("pk") or self.new_mode):
            buttons.add(
                bt.WidgetButton(
                    label="Consolidated Invoices",
                    endpoint=reverse("wbaccounting:consolidated-invoice-list", args=[], request=self.request),
                )
            )
        return buttons


class ConsolidatedInvoiceButtonConfig(InvoiceBaseButtonConfig):
    def get_custom_list_instance_buttons(self) -> set:
        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbaccounting:invoice",),
                label="Approve ({{num_submitted}})",
                description_fields="""
                        <p>Do you want to approve all {{num_submitted}} submitted invoices?</p>
                        """,
                action_label="Approving",
                title="Approve",
                key="approve",
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbaccounting:invoice",),
                label="Submit ({{num_draft}})",
                description_fields="""
                        <p>Do you want to submit {{num_draft}} invoices?</p>
                        """,
                action_label="Submitting",
                title="Submit",
                key="submit",
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbaccounting:invoice",),
                label="Pay ({{num_sent}})",
                description_fields="""
                        <p>Do you want to pay all {{num_sent}} invoices?</p>
                        """,
                action_label="Payment",
                title="Pay",
                key="pay",
            ),
        }
