from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class BookingEntryButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {
            buttons.WidgetButton(
                key="appended_booking_entries", label="Appended Booking Entries", icon=WBIcon.NOTEBOOK.icon
            )
        }

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()
