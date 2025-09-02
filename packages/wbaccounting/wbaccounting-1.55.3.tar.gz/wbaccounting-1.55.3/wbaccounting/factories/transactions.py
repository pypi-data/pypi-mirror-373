from decimal import Decimal

import factory

from wbaccounting.models import Transaction


class AbstractTransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction
        abstract = True

    booking_date = factory.Faker("date_between", start_date="+2d", end_date="+3d")
    value_date = factory.Faker("date_object")

    bank_account = factory.SubFactory("wbcore.contrib.directory.factories.BankingContactFactory")
    from_bank_account = factory.SubFactory("wbcore.contrib.directory.factories.BankingContactFactory")
    to_bank_account = factory.SubFactory("wbcore.contrib.directory.factories.BankingContactFactory")

    @factory.post_generation
    def set_currency(self, create, extracted, **kwargs):
        if isinstance(self, dict):
            self["currency"] = self["bank_account"].currency
        else:
            self.currency = self.bank_account.currency


class TransactionFactory(AbstractTransactionFactory):
    value = factory.Faker("pydecimal", min_value=Decimal(0.1), max_value=Decimal(10000000))


class LocalCurrencyTransactionFactory(AbstractTransactionFactory):
    value_local_ccy = factory.Faker("pydecimal", min_value=Decimal(0.1), max_value=Decimal(10000000))
