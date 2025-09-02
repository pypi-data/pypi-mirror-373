import factory

from wbaccounting.models import Invoice, InvoiceType


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:  # type: ignore
        model = Invoice

    title = factory.Faker("text", max_nb_chars=64)
    invoice_date = factory.Faker("date_object")
    reference_date = factory.Faker("date_object")
    invoice_currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyUSDFactory")

    counterparty = factory.SubFactory("wbcore.contrib.directory.factories.EntryFactory")
    invoice_type = factory.SubFactory("wbaccounting.factories.InvoiceTypeFactory")

    text_above = factory.Faker("text")
    text_below = factory.Faker("text")

    # @factory.post_generation
    # def invoice_document(self, create, extracted, **kwargs):
    #     self.refresh_invoice_document(override_status=True)

    # is_counterparty_invoice

    # @classmethod
    # def _create(cls, model_class, *args, **kwargs):
    #     company = CompanyFactory()
    #     signee = PersonSignatureFactory()
    #     global_preferences_registry.manager()["wbaccounting__invoice_company"] = company.id
    #     global_preferences_registry.manager()["wbaccounting__invoice_signers"] = Person.objects.filter(id=signee.id)
    #     """Override the default ``_create`` with our custom call."""
    #     manager = cls._get_manager(model_class)
    #     # The default would use ``manager.create(*args, **kwargs)``
    #     return manager.create(*args, **kwargs)


class InvoiceTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Invoice Type {n}")
    processor = factory.Faker("text", max_nb_chars=64)

    class Meta:  # type: ignore
        model = InvoiceType
