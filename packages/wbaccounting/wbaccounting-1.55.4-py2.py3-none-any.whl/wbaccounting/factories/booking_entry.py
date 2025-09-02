import factory
from factory.fuzzy import FuzzyDecimal

from wbaccounting.models import BookingEntry


class BookingEntryFactory(factory.django.DjangoModelFactory):
    class Meta:  # type: ignore
        model = BookingEntry

    # resolved
    title = factory.Faker("text", max_nb_chars=64)
    booking_date = factory.Faker("date_between", start_date="+2d", end_date="+3d")
    payment_date = factory.Faker("date_object")
    reference_date = factory.Faker("date_object")
    gross_value = factory.Faker("pydecimal", right_digits=4, min_value=0, max_value=99999999999)
    net_value = factory.Faker("pydecimal", right_digits=4, min_value=0, max_value=99999999999)
    vat = FuzzyDecimal(0, 0.9, 4)
    currency = factory.SelfAttribute("invoice.invoice_currency")

    invoice = factory.SubFactory("wbaccounting.factories.InvoiceFactory")
    counterparty = factory.SubFactory("wbcore.contrib.directory.factories.EntryFactory")
