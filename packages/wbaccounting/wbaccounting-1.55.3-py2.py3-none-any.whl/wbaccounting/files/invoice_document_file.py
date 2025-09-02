import logging
from contextlib import suppress
from io import BytesIO

from dynamic_preferences.registries import global_preferences_registry
from reportlab import platypus
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, NextPageTemplate, PageTemplate
from reportlab.platypus.frames import Frame
from wbcore.contrib.directory.models import Entry

from wbaccounting.files import utils as invoice_utils

logger = logging.getLogger("wbaccounting.files.invoice_document_file")


def generate_file(invoice):
    debug = 0

    total_gross_value, total_net_value = invoice_utils.get_gross_and_net_value(invoice)
    show_tax_id = total_gross_value != total_net_value

    styles = invoice_utils.get_styles()

    output = BytesIO()
    doc = BaseDocTemplate(output, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)

    global_preferences = global_preferences_registry.manager()
    invoice_company = Entry.objects.get(id=global_preferences["wbaccounting__invoice_company"])
    signees = global_preferences["wbaccounting__invoice_signers"]

    logo_ratio = 0
    logo = None
    try:
        logo, logo_ratio = invoice_utils.logo_block(invoice_company.profile_image)
    except ValueError:
        pass
    logo_frame = Frame(
        x1=0,
        y1=A4[1] - (30 + 1 * cm),
        width=30 * logo_ratio + 1.5 * cm,
        height=30 + 1 * cm,
        leftPadding=1.5 * cm,
        bottomPadding=0,
        rightPadding=0,
        topPadding=1 * cm,
        id="logo_frame",
        showBoundary=debug,
    )

    address_frame = Frame(
        x1=A4[0] - (12 * cm),
        y1=A4[1] - (6 * cm),
        width=12 * cm,
        height=6 * cm,
        leftPadding=0,
        bottomPadding=0,
        rightPadding=1.5 * cm,
        topPadding=2.5 * cm,
        id="address_frame",
        showBoundary=debug,
    )

    content_frame = Frame(
        x1=0,
        y1=0,
        width=A4[0],
        height=A4[1] - (6 * cm),
        leftPadding=1.5 * cm,
        bottomPadding=1 * cm,
        rightPadding=1.5 * cm,
        topPadding=0,
        id="content_frame",
        showBoundary=debug,
    )

    content_frame2 = Frame(
        x1=0,
        y1=0,
        width=A4[0],
        height=A4[1],
        leftPadding=1.5 * cm,
        bottomPadding=1 * cm,
        rightPadding=1.5 * cm,
        topPadding=1 * cm,
        id="content_frame2",
        showBoundary=debug,
    )

    doc.addPageTemplates(
        [
            PageTemplate(id="TitlePage", frames=[logo_frame, address_frame, content_frame]),
            PageTemplate(id="OtherPage", frames=[content_frame2]),
        ]
    )

    elements = list()
    elements.append(NextPageTemplate(["OtherPage"]))
    if logo:
        elements.append(logo)
    elements.append(platypus.FrameBreak("address_frame"))

    if invoice.is_counterparty_invoice:
        elements.extend(invoice_utils.address_block(invoice_company, invoice, styles, right=True))
    else:
        elements.extend(invoice_utils.address_block(invoice.counterparty, invoice, styles, right=True))

    elements.append(platypus.FrameBreak("content_frame"))
    elements.extend(invoice_utils.city_and_date_block(invoice, styles, entry=invoice_company))

    if invoice.is_counterparty_invoice:
        elements.extend(invoice_utils.address_block(invoice.counterparty, invoice, styles, tax_id=show_tax_id))
    else:
        elements.extend(invoice_utils.address_block(invoice_company, invoice, styles, tax_id=show_tax_id))

    elements.extend(invoice_utils.add_text_block_with_context(invoice.text_above, invoice, styles))
    elements.extend(invoice_utils.add_booking_entries(invoice, styles, False))
    elements.extend(invoice_utils.add_text_block_with_context(invoice.text_below, invoice, styles))
    elements.extend(
        invoice_utils.add_transfer_block(
            invoice,
            invoice_company if not invoice.is_counterparty_invoice else invoice.counterparty,
            styles,
            total_gross_value,
        )
    )
    with suppress(ValueError):
        elements.extend(invoice_utils.signature_block(signees, styles))
    doc.build(elements)

    pdf = output.getvalue()
    output.close()

    return pdf
