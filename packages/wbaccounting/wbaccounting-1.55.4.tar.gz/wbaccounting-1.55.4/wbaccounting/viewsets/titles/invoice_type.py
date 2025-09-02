from wbcore.metadata.configs.titles import TitleViewConfig


class InvoiceTypeTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Invoice Type"

    def get_list_title(self):
        return "Invoice Types"

    def get_create_title(self):
        return "New Invoice Type"
