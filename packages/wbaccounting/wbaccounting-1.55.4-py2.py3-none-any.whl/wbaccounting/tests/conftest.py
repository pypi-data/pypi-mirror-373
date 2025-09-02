from decimal import Decimal

import factory
import pytest
from django.apps import apps
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbaccounting.factories import (
    BookingEntryFactory,
    EntryAccountingInformationFactory,
    InvoiceFactory,
    InvoiceTypeFactory,
    LocalCurrencyTransactionFactory,
    TransactionFactory,
)
from wbcore.contrib.authentication.factories import (
    SuperUserFactory,
    UserActivityFactory,
    UserFactory,
)
from wbcore.contrib.currency.factories import CurrencyFactory, CurrencyFXRatesFactory
from wbcore.contrib.directory.factories import (
    BankingContactFactory,
    EntryFactory,
    PersonFactory,
)
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbcore.tests.conftest import *

register(BookingEntryFactory)
register(InvoiceFactory)
register(InvoiceTypeFactory)
register(EntryAccountingInformationFactory)

register(TransactionFactory)
register(TransactionFactory, "transaction_no_value_date", value_date=None)
register(
    TransactionFactory,
    "transaction_fx",
    fx_rate=factory.Faker("pydecimal", min_value=Decimal(0.1), max_value=Decimal(0.9)),
)
register(LocalCurrencyTransactionFactory, "transaction_local_ccy")
register(
    LocalCurrencyTransactionFactory,
    "transaction_local_ccy_fx",
    fx_rate=factory.Faker("pydecimal", min_value=Decimal(0.1), max_value=Decimal(0.9)),
)


register(CurrencyFactory)
register(CurrencyFXRatesFactory)

register(EntryFactory)
register(UserFactory)
register(PersonFactory)
register(SuperUserFactory)
register(UserActivityFactory)
register(BankingContactFactory)

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbaccounting"))


@pytest.fixture
def booking_entries(request, booking_entry_factory):
    return [booking_entry_factory.create() for _ in range(request.param)]
