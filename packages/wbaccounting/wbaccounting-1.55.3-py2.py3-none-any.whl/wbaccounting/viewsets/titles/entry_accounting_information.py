from wbcore.metadata.configs.titles import TitleViewConfig


class EntryAccountingInformationTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Counterparty: {{ _entry.computed_str }}"

    def get_list_title(self):
        return "Counterparties"

    def get_create_title(self):
        return "New Counterparty"
