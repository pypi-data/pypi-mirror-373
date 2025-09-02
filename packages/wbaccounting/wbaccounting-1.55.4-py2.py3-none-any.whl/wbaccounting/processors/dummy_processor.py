from wbaccounting.models import Invoice


def processor(invoice: Invoice):
    print(f"I am a dummy processor that processes the Invoice: {invoice}")  # noqa
