from django.dispatch import receiver
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.directory.serializers import EntryRepresentationSerializer
from wbcore.contrib.directory.viewsets import (
    CompanyModelViewSet,
    EntryModelViewSet,
    PersonModelViewSet,
)
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.signals.instance_buttons import add_instance_button
from wbcore.utils.date import current_quarter_date_end, current_quarter_date_start


class StartEndParametersSerializer(serializers.Serializer):
    start = serializers.DateField(default=current_quarter_date_start(), label="Start")
    end = serializers.DateField(default=current_quarter_date_end(), label="End")


class CounterpartiesSerializer(serializers.Serializer):
    counterparties = serializers.PrimaryKeyRelatedField(many=True)
    _counterparties = EntryRepresentationSerializer(many=True, source="counterparties")


class StartEndParametersWithCounterpartiesSerializer(CounterpartiesSerializer, StartEndParametersSerializer): ...


class EntryAccountingInformationButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self) -> set:
        if not self.instance:
            return {
                buttons.ActionButton(
                    method=RequestType.POST,
                    identifiers=("wbaccounting:bookingentry",),
                    endpoint=reverse(
                        "wbaccounting:entryaccountinginformation-generate-booking-entries-for-counterparties",
                        request=self.request,
                    ),
                    label="Generate Booking Entries",
                    description_fields="""<p>Generate Booking Entries between {{start}} and {{end}}?</p>""",
                    action_label="Generate Booking Entries",
                    title="Generate Booking Entries",
                    serializer=StartEndParametersWithCounterpartiesSerializer,
                    instance_display=create_simple_display([["start"], ["end"], ["counterparties"]]),
                ),
                buttons.ActionButton(
                    method=RequestType.POST,
                    identifiers=("wbaccounting:invoice",),
                    endpoint=reverse(
                        "wbaccounting:entryaccountinginformation-generate-invoices-for-counterparties",
                        request=self.request,
                    ),
                    label="Invoice outstanding Bookings",
                    description_fields="""<p>Invoice outstanding bookings? If you don't supply counterparties, all counterparties will be considered</p>""",
                    action_label="Invoice outstanding Bookings",
                    title="Invoice outstanding Bookings",
                    serializer=CounterpartiesSerializer,
                    instance_display=create_simple_display([["counterparties"]]),
                ),
            }
        return set()

    def get_custom_instance_buttons(self) -> set:
        return {
            buttons.ActionButton(
                method=RequestType.POST,
                identifiers=("wbaccounting:bookingentry",),
                key="generate_booking_entries",
                label="Generate Booking Entries",
                description_fields="""<p>Generate Booking Entries between {{start}} and {{end}}?</p>""",
                action_label="Generate Booking Entries",
                title="Generate Booking Entries",
                serializer=StartEndParametersSerializer,
                instance_display=create_simple_display([["start"], ["end"]]),
            ),
            buttons.ActionButton(
                method=RequestType.POST,
                identifiers=("wbaccounting:invoice",),
                key="invoice_booking_entries",
                label="Invoice Booking Entries",
                description_fields="<p>Do you want to invoice all outstanding booking entries?</p>",
                action_label="Invoice Booking Entries",
                title="Invoice Booking Entries",
            ),
        }


@receiver(add_instance_button, sender=PersonModelViewSet)
@receiver(add_instance_button, sender=EntryModelViewSet)
@receiver(add_instance_button, sender=CompanyModelViewSet)
def entry_adding_instance_buttons(sender, many, *args, **kwargs):
    if not many:
        return buttons.WidgetButton(key="accounting-information", label="Accounting", icon=WBIcon.MAIL_OPEN.icon)
