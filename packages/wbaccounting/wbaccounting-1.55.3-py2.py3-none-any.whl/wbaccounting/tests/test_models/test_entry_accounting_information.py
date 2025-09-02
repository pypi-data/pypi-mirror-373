import pytest
from dynamic_preferences.registries import global_preferences_registry
from wbaccounting.models import BookingEntry, EntryAccountingInformation
from wbaccounting.models.entry_accounting_information import (
    default_currency,
    default_email_body,
)
from wbcore.contrib.authentication.models import User
from wbcore.contrib.currency.models import Currency


@pytest.mark.django_db
class TestEntryAccountingInformation:
    def test_str(self, entry_accounting_information: EntryAccountingInformation):
        assert str(entry_accounting_information) == f"Counterparty: {entry_accounting_information.entry.computed_str}"

    @pytest.mark.parametrize(
        "method,return_value",
        [
            ("get_endpoint_basename", "wbaccounting:entryaccountinginformation"),
            ("get_representation_value_key", "id"),
            ("get_representation_label_key", "{{entry_repr}}"),
            ("get_representation_endpoint", "wbaccounting:entryaccountinginformationrepresentation-list"),
        ],
    )
    def test_wbmodel_methods(self, method: str, return_value: str):
        assert getattr(EntryAccountingInformation, method)() == return_value

    @pytest.mark.parametrize("user__is_superuser", [False])
    def test_filter_for_user_no_superuser(self, entry_accounting_information: EntryAccountingInformation, user: User):
        entry_accounting_information_list = EntryAccountingInformation.objects.filter_for_user(user)  # type: ignore
        assert entry_accounting_information not in entry_accounting_information_list

    @pytest.mark.parametrize("user__is_superuser", [True])
    def test_filter_for_user_superuser(self, entry_accounting_information: EntryAccountingInformation, user: User):
        entry_accounting_information_list = EntryAccountingInformation.objects.filter_for_user(user)  # type: ignore
        assert entry_accounting_information in entry_accounting_information_list

    @pytest.mark.parametrize("user__is_superuser", [False])
    @pytest.mark.parametrize("user__user_permissions", [(["wbaccounting.view_entryaccountinginformation"])])
    @pytest.mark.parametrize("entry_accounting_information__counterparty_is_private", [False])
    def test_filter_for_user_public_counterparty(
        self, entry_accounting_information: EntryAccountingInformation, user: User
    ):
        entry_accounting_information_list = EntryAccountingInformation.objects.filter_for_user(user)  # type: ignore
        assert entry_accounting_information in entry_accounting_information_list

    @pytest.mark.parametrize("user__is_superuser", [False])
    @pytest.mark.parametrize("user__user_permissions", [(["wbaccounting.view_entryaccountinginformation"])])
    @pytest.mark.parametrize("entry_accounting_information__counterparty_is_private", [True])
    def test_filter_for_user_private_counterparty(
        self, user: User, entry_accounting_information: EntryAccountingInformation
    ):
        entry_accounting_information_list = EntryAccountingInformation.objects.filter_for_user(user)  # type: ignore
        assert entry_accounting_information not in entry_accounting_information_list

    @pytest.mark.parametrize("user__is_superuser", [False])
    @pytest.mark.parametrize("user__user_permissions", [(["wbaccounting.view_entryaccountinginformation"])])
    @pytest.mark.parametrize("entry_accounting_information__counterparty_is_private", [True])
    def test_filter_for_user_private_counterparty_with_exempt(
        self, booking_entry: BookingEntry, user: User, entry_accounting_information: EntryAccountingInformation
    ):
        entry_accounting_information.exempt_users.add(user)
        entry_accounting_information_list = EntryAccountingInformation.objects.filter_for_user(user)  # type: ignore
        assert entry_accounting_information in entry_accounting_information_list

    def test_default_email_body(self):
        assert default_email_body() == ""

    def test_custom_default_email_body(self):
        global_preferences_registry.manager()["wbaccounting__invoice_email_body"] = "Custom Body"
        assert default_email_body() == "Custom Body"

    def test_default_currency(self):
        assert default_currency() is None

    def test_custom_default_currency(self, currency: Currency):
        global_preferences_registry.manager()[
            "wbaccounting__default_entry_account_information_currency_key"
        ] = currency.key
        assert default_currency().pk is currency.pk
