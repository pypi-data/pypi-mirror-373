from wbcore.metadata.configs.titles import TitleViewConfig


class BookingEntryTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Booking: {{title}}"

    def get_list_title(self):
        return "Booking"

    def get_create_title(self):
        return "New Booking"
