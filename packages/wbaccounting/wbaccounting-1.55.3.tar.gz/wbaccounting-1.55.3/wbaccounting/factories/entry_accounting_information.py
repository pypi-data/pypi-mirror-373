import factory
from factory.fuzzy import FuzzyDecimal
from wbcore.contrib.directory.factories import CompanyFactory, EmailContactFactory

from wbaccounting.models import EntryAccountingInformation


class EntryAccountingInformationFactory(factory.django.DjangoModelFactory):
    class Meta:  # type: ignore
        model = EntryAccountingInformation

    entry = factory.SubFactory("wbcore.contrib.directory.factories.EntryFactory")
    tax_id = factory.Faker("text", max_nb_chars=64)
    vat = FuzzyDecimal(0, 0.9, 4)
    send_mail = factory.Faker("pybool")
    counterparty_is_private = False

    email_body = factory.Faker("paragraph")

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        if isinstance(self, EntryAccountingInformationFactory) and not create:
            self.email_to.add(EmailContactFactory.create())
            self.email_cc_add(EmailContactFactory.create())
            self.email_bcc.add(EmailContactFactory.create())

        if isinstance(self, dict):
            self["email_to"] = [EmailContactFactory.create().id]
            self["email_cc"] = [EmailContactFactory.create().id]
            self["email_bcc"] = [EmailContactFactory.create().id]

    @factory.post_generation
    def exempt_users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.exempt_users.add(user)

    default_currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyFactory")


class CompanyAccountingFactory(CompanyFactory):
    entry_accounting_information = factory.RelatedFactory(
        "wbaccounting.factories.EntryAccountingInformationFactory", "entry"
    )
