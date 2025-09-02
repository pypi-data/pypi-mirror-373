from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class BookingEntryDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        _counterparty_fields = [dp.Field(key="counterparty", label="Counterparty")]
        _common_fields = [
            dp.Field(key="booking_date", label="Book. Date", width=100),
            dp.Field(key="reference_date", label="Ref. Date", width=100),
            dp.Field(key="payment_date", label="Payment. Date", width=100),
            dp.Field(key="title", label="Title", width=325),
            dp.Field(key="vat", label="VAT", width=100),
            dp.Field(key="gross_value", label="Gross", width=100),
            dp.Field(key="net_value", label="Net", width=100),
        ]
        _invoice_fields = [dp.Field(key="invoice", label="Invoice", width=325)]

        if "invoice_id" in self.view.kwargs:
            return dp.ListDisplay(fields=_common_fields)

        if "entry_accounting_information_id" in self.view.kwargs:
            return dp.ListDisplay(fields=[*_common_fields, *_invoice_fields])

        return dp.ListDisplay(fields=[*_counterparty_fields, *_common_fields, *_invoice_fields])

    def get_instance_display(self) -> dp.Display:
        return dp.Display(
            pages=[
                dp.Page(
                    layouts={
                        dp.default(): dp.Layout(
                            grid_template_areas=[
                                ["title", "title", "title", "counterparty", ".", "booking_date"],
                                ["currency", "vat", "gross_value", "net_value", ".", "reference_date"],
                                [
                                    "invoice_currency",
                                    "invoice_fx_rate",
                                    "invoice_gross_value",
                                    "invoice_net_value",
                                    ".",
                                    "due_date",
                                ],
                                ["invoice", "invoice", "invoice", "invoice", ".", "payment_date"],
                            ],
                            grid_template_columns=[
                                "100px",
                                "100px",
                                "200px",
                                "200px",
                                "25px",
                                "150px",
                            ],
                        )
                    }
                )
            ]
        )
