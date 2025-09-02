from django.conf import settings
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import (
    IntegerPreference,
    LongStringPreference,
    ModelMultipleChoicePreference,
    StringPreference,
)
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.directory.models import Person

accounting_section = Section("wbaccounting")


def format_invoice_number(number):
    global_preferences = global_preferences_registry.manager()
    ts = global_preferences["wbaccounting__invoice_thousand_seperator"]
    ds = global_preferences["wbaccounting__invoice_decimal_seperator"]
    if not number:
        number = 0
    s = "{:,.2f}".format(number)
    s = s.replace(",", "//")
    s = s.replace(".", "\\")

    return s.replace("//", ts).replace("\\", ds)


@global_preferences_registry.register
class DefaultEntryAccountingInformationCurrency(StringPreference):
    section = accounting_section
    name = "default_entry_account_information_currency_key"
    default = "CHF"

    verbose_name = "The currency key used for the default currency of newly created entry accounting informations."

    def validate(self, value):
        if not Currency.objects.filter(key=value).exists():
            return ValueError("The specified currency key is not valid")


@global_preferences_registry.register
class ExternalEmailAddress(StringPreference):
    section = accounting_section
    name = "external_email_address"
    default = ""

    verbose_name = "External Email Address"
    help_text = "The Email Address used to send Invoices to the external party."


@global_preferences_registry.register
class InvoiceEmailBody(LongStringPreference):
    section = accounting_section
    name = "invoice_email_body"
    default = ""

    verbose_name = "The default E-Mail Body used for emailing Invoices"


@global_preferences_registry.register
class InvoiceThousandSeperatorPreference(StringPreference):
    section = accounting_section
    name = "invoice_thousand_seperator"
    default = ","

    verbose_name = "Invoice Thousand Seperator"
    help_text = "Thousand Seperator for Invoices"


@global_preferences_registry.register
class InvoiceDecimalSeperatorPreference(StringPreference):
    section = accounting_section
    name = "invoice_decimal_seperator"
    default = "."

    verbose_name = "Invoice Decimal Seperator"
    help_text = "Decimal Seperator for Invoices"


@global_preferences_registry.register
class InvoiceSignerPreference(ModelMultipleChoicePreference):
    section = accounting_section
    name = "invoice_signers"
    queryset = Person.objects.all()
    default = None
    verbose_name = "Invoice Signers"


@global_preferences_registry.register
class InvoiceCompanyPreference(IntegerPreference):
    section = accounting_section
    name = "invoice_company"
    default = 0

    verbose_name = "Invoice Company"
    help_text = "The PK of the company who issues the invoices"


@global_preferences_registry.register
class DefaultFromEmailAddressPreference(StringPreference):
    section = accounting_section
    name = "default_from_email_address"
    default = settings.DEFAULT_FROM_EMAIL

    verbose_name = "The default from email address"
    help_text = "The default from email address used to send invoice"
