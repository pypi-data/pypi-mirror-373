from decimal import Decimal

import pytest
from pytest_factoryboy import LazyFixture
from wbaccounting.models import BookingEntry, EntryAccountingInformation, Invoice
from wbcore.contrib.authentication.models import User


@pytest.mark.django_db
class TestBookingEntry:
    def test_str(self, booking_entry: BookingEntry):
        assert str(booking_entry) == booking_entry.title

    @pytest.mark.parametrize(
        "method,return_value",
        [
            ("get_endpoint_basename", "wbaccounting:bookingentry"),
            ("get_representation_value_key", "id"),
            ("get_representation_label_key", "{{title}}"),
            ("get_representation_endpoint", "wbaccounting:bookingentryrepresentation-list"),
        ],
    )
    def test_wbmodel_methods(self, method: str, return_value: str):
        assert getattr(BookingEntry, method)() == return_value

    @pytest.mark.parametrize("user__is_superuser", [False])
    def test_filter_for_user_no_superuser(self, booking_entry: BookingEntry, user: User):
        booking_entries = BookingEntry.objects.filter_for_user(user)  # type: ignore
        assert booking_entry not in booking_entries

    @pytest.mark.parametrize("user__is_superuser", [True])
    def test_filter_for_user_superuser(self, booking_entry: BookingEntry, user: User):
        booking_entries = BookingEntry.objects.filter_for_user(user)  # type: ignore
        assert booking_entry in booking_entries

    @pytest.mark.parametrize("user__is_superuser", [False])
    @pytest.mark.parametrize("user__user_permissions", [(["wbaccounting.view_bookingentry"])])
    @pytest.mark.parametrize("booking_entry__counterparty", [LazyFixture("entry")])
    @pytest.mark.parametrize("entry_accounting_information__entry", [LazyFixture("entry")])
    @pytest.mark.parametrize("entry_accounting_information__counterparty_is_private", [False])
    def test_filter_for_user_public_counterparty(
        self, booking_entry: BookingEntry, user: User, entry_accounting_information: EntryAccountingInformation
    ):
        booking_entries = BookingEntry.objects.filter_for_user(user)  # type: ignore
        assert booking_entry in booking_entries

    @pytest.mark.parametrize("user__is_superuser", [False])
    @pytest.mark.parametrize("user__user_permissions", [(["wbaccounting.view_bookingentry"])])
    @pytest.mark.parametrize("booking_entry__counterparty", [LazyFixture("entry")])
    @pytest.mark.parametrize("entry_accounting_information__entry", [LazyFixture("entry")])
    @pytest.mark.parametrize("entry_accounting_information__counterparty_is_private", [True])
    def test_filter_for_user_private_counterparty(
        self, booking_entry: BookingEntry, user: User, entry_accounting_information: EntryAccountingInformation
    ):
        booking_entries = BookingEntry.objects.filter_for_user(user)  # type: ignore
        assert booking_entry not in booking_entries

    @pytest.mark.parametrize("user__is_superuser", [False])
    @pytest.mark.parametrize("user__user_permissions", [(["wbaccounting.view_bookingentry"])])
    @pytest.mark.parametrize("booking_entry__counterparty", [LazyFixture("entry")])
    @pytest.mark.parametrize("entry_accounting_information__entry", [LazyFixture("entry")])
    @pytest.mark.parametrize("entry_accounting_information__counterparty_is_private", [True])
    def test_filter_for_user_private_counterparty_with_exempt(
        self, booking_entry: BookingEntry, user: User, entry_accounting_information: EntryAccountingInformation
    ):
        entry_accounting_information.exempt_users.add(user)
        booking_entries = BookingEntry.objects.filter_for_user(user)  # type: ignore
        assert booking_entry in booking_entries

    @pytest.mark.parametrize("booking_entry__net_value", [Decimal(90)])
    @pytest.mark.parametrize("booking_entry__gross_value", [None])
    @pytest.mark.parametrize("booking_entry__vat", [Decimal(0.1)])
    def test_net_without_gross(self, booking_entry: BookingEntry):
        assert pytest.approx(booking_entry.gross_value) == Decimal(99)

    @pytest.mark.parametrize("booking_entry__net_value", [None])
    @pytest.mark.parametrize("booking_entry__gross_value", [Decimal(99)])
    @pytest.mark.parametrize("booking_entry__vat", [Decimal(0.1)])
    def test_gross_without_net(self, booking_entry: BookingEntry):
        assert pytest.approx(booking_entry.net_value) == Decimal(90)

    @pytest.mark.parametrize("booking_entry__net_value", [Decimal(90)])
    @pytest.mark.parametrize("booking_entry__gross_value", [Decimal(100)])
    @pytest.mark.parametrize("booking_entry__vat", [Decimal(0.1)])
    def test_net_with_gross(self, booking_entry: BookingEntry):
        assert pytest.approx(booking_entry.gross_value) == Decimal(99)

    @pytest.mark.parametrize("booking_entry__net_value", [None])
    @pytest.mark.parametrize("booking_entry__gross_value", [None])
    @pytest.mark.parametrize("booking_entry__vat", [Decimal(0.1)])
    def test_net_and_gross_none(self, booking_entry: BookingEntry):
        assert booking_entry.net_value == Decimal(0) and booking_entry.gross_value == Decimal(0)

    def test_invoice_value_same_currency(self, booking_entry: BookingEntry):
        assert booking_entry.net_value == booking_entry.invoice_net_value
        assert booking_entry.gross_value == booking_entry.invoice_gross_value

    def test_invoice_value_different_currency(
        self, booking_entry: BookingEntry, invoice: Invoice, currency_factory, mocker
    ):
        # Change the invoice currency
        invoice.invoice_currency = currency_factory.create()
        invoice.save()

        # Patch the currency convert method to no rely on the database
        mocker.patch("wbcore.contrib.currency.models.Currency.convert", return_value=Decimal(1.1))
        # Run the save method to trigger fx computation
        booking_entry.save()
        assert booking_entry.invoice_net_value == pytest.approx(booking_entry.net_value * booking_entry.invoice_fx_rate)  # type: ignore

    def test_invoice_save_on_change(self, booking_entry: BookingEntry, mocker):
        mocked_save = mocker.patch("wbaccounting.models.invoice.Invoice.save", autospec=True)
        booking_entry.save()
        mocked_save.assert_called_once()

    def test_invoice_delete_on_change(self, booking_entry: BookingEntry, mocker):
        mocked_save = mocker.patch("wbaccounting.models.invoice.Invoice.save", autospec=True)
        booking_entry.delete()
        mocked_save.assert_called_once()
