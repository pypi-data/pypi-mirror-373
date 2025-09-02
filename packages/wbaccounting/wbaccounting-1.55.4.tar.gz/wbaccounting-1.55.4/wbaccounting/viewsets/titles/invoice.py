from wbcore.metadata.configs.titles import TitleViewConfig


class InvoiceTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Invoice {{title}}"

    def get_list_title(self):
        return "Invoices"

    def get_create_title(self):
        return "New Invoice"


class ConsolidatedInvoiceTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Consolidated Invoice"

    def get_list_title(self):
        return "Consolidated Invoices"

    def get_create_title(self):
        return "New Consolidated Invoice"
