import pytest


@pytest.mark.django_db
def test_dummy_processor(invoice, mocker):
    from wbaccounting.processors import dummy_processor

    invoice_type = invoice.invoice_type
    invoice_type.processor = "wbaccounting.processors.dummy_processor.processor"
    invoice_type.save()
    invoice.status = invoice.Status.SUBMITTED
    invoice.save()

    dummy_processor = mocker.spy(dummy_processor, "processor")
    invoice.approve()
    invoice.save()
    dummy_processor.assert_called_once()
    assert invoice.status == invoice.Status.SENT


@pytest.mark.django_db
def test_no_processor(invoice):
    invoice.status = invoice.Status.SUBMITTED
    invoice.save()

    invoice.approve()
    invoice.save()
    assert invoice.status == invoice.Status.APPROVED
