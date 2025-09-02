from django.template import Context, Template
from reportlab.lib import colors, utils
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, Table, TableStyle

from wbaccounting.dynamic_preferences_registry import format_invoice_number


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Headline", fontName="Helvetica", fontSize=24, leading=34))
    styles.add(ParagraphStyle(name="Default", fontName="Helvetica", fontSize=10, leading=12))
    styles.add(ParagraphStyle(name="Default-Table-Header", fontName="Helvetica", fontSize=14, leading=16))
    styles.add(
        ParagraphStyle(
            name="Default-Table-Header-Right", fontName="Helvetica", fontSize=14, leading=16, alignment=TA_RIGHT
        )
    )
    styles.add(ParagraphStyle(name="Default-Right", fontName="Helvetica", fontSize=10, leading=12, alignment=TA_RIGHT))
    styles.add(
        ParagraphStyle(
            name="Default-Right-Linebreak",
            fontName="Helvetica",
            fontSize=10,
            leading=12,
            alignment=TA_RIGHT,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(name="Default-Center", fontName="Helvetica", fontSize=10, leading=12, alignment=TA_CENTER)
    )
    styles.add(ParagraphStyle(name="Default-Linebreak", fontName="Helvetica", fontSize=10, leading=12, spaceAfter=12))
    styles.add(
        ParagraphStyle(name="Default-Linebreak-Before", fontName="Helvetica", fontSize=10, leading=12, spaceBefore=12)
    )
    styles.add(
        ParagraphStyle(name="Default-Double-Linebreak", fontName="Helvetica", fontSize=10, leading=12, spaceAfter=24)
    )
    styles.add(
        ParagraphStyle(
            name="Default-Double-Linebreak-With-Before",
            fontName="Helvetica",
            fontSize=10,
            leading=12,
            spaceAfter=24,
            spaceBefore=24,
        )
    )
    (styles.add(ParagraphStyle(name="Normal-Right", alignment=TA_RIGHT)),)
    (styles.add(ParagraphStyle(name="Annotation", fontName="Helvetica", fontSize=8, leading=10)),)
    (
        styles.add(
            ParagraphStyle(name="Annotation-Right", fontName="Helvetica", fontSize=8, leading=10, alignment=TA_RIGHT)
        ),
    )
    return styles


# TODO to be removed
# def get_taxes(invoice, party, counterparty):
#     vat = 0
#     social_charges = 0
#     if invoice.favour == 'COUNTERPARTY':
#         vat = counterparty.accounting_information.vat if counterparty.accounting_information.vat else 0
#         social_charges = counterparty.accounting_information.social_charges if counterparty.accounting_information.social_charges else 0
#     else:
#         vat = party.vat if party is not None and party.vat else 0
#         social_charges = party.accounting_information.social_charges if party is not None and party.accounting_information.social_charges else 0
#     if invoice.vat or invoice.vat == 0:
#         vat = invoice.vat
#     if invoice.social_charges or invoice.social_charges == 0:
#         social_charges = invoice.social_charges
#     return vat, social_charges

# def banking_block(entry, invoice, styles, banking=None):
#     elements = list()
#     if banking is None:
#         bankings = entry.banking.all() if entry else None
#         if bankings:
#             if bankings.filter(currency=invoice.base_currency).exists():
#                 banking = bankings.filter(currency=invoice.base_currency).first()
#             elif bankings.filter(primary=True).exists():
#                 banking = bankings.filter(primary=True).first()
#         else:
#             return elements
#     elements.append(Paragraph('{}'.format(banking.institute), styles['Default-Linebreak-Before']))
#     if banking.institute_additional:
#         elements.append(Paragraph('{}'.format(banking.institute_additional), styles['Default']))
#     elements.append(Paragraph('IBAN: {}'.format(banking.iban), styles['Default']))
#     if banking.swift_bic:
#         elements.append(Paragraph('SWIFT: {}'.format(banking.swift_bic), styles['Default']))
#     return elements


def address_block(entry, invoice, styles, right=False, address=None, tax_id=None):
    elements = list()
    if address is None:
        addresses = entry.addresses.all() if entry is not None else None
        if addresses:
            if addresses.filter(primary=True).exists():
                address = addresses.filter(primary=True).first()
            elif addresses.count() > 0:
                address = addresses.first()
        else:
            return elements

    if right:
        default_style = styles["Default-Right"]
        default_linebreak_style = styles["Default-Right-Linebreak"]
    else:
        default_style = styles["Default"]
        default_linebreak_style = styles["Default-Linebreak"]

    casted_entry = entry.get_casted_entry()
    if entry.is_company:
        elements.append(Paragraph("<b>{0.name}</b>".format(casted_entry), default_style))
    else:
        elements.append(Paragraph("<b>{0.first_name} {0.last_name}</b>".format(casted_entry), default_style))

    elements.append(Paragraph(address.street, default_style))
    if address.street_additional is not None and address.street_additional != "":
        elements.append(Paragraph(address.street_additional, default_style))
    elements.append(Paragraph("{} {}".format(address.zip, address.geography_city), default_style))
    elements.append(Paragraph(address.geography_city.parent.parent.name, default_linebreak_style))

    if tax_id and entry.entry_accounting_information.tax_id:
        elements.append(Paragraph(f"VAT: {entry.entry_accounting_information.tax_id}", default_linebreak_style))

    return elements


def city_and_date_block(invoice, styles, entry=None, city=None, date=None):
    elements = list()
    if date is None:
        date = invoice.invoice_date
    if city is None:
        primary_address = entry.primary_address_contact() if entry else None
        if primary_address:
            city = primary_address.geography_city
    if city:
        elements.append(Paragraph("{}, {:%d.%m.%Y}".format(city, date), styles["Default-Right-Linebreak"]))
    else:
        elements.append(Paragraph("{:%d.%m.%Y}".format(date), styles["Default-Right-Linebreak"]))
    return elements


def logo_block(image):
    # print(image)
    reportlab_image = utils.ImageReader(image)
    width, height = reportlab_image.getSize()
    ratio = float(width) / float(height)
    image = Image(image, width=30 * ratio, height=30)
    return image, ratio


def signature_block(signees, styles):
    elements = list()
    if signees:
        elements.append(Paragraph("Best Regards,", styles["Default-Double-Linebreak-With-Before"]))
        for signee in signees:
            if signee is not None and signee.signature.name is not None and signee.signature.name != "":
                reportlab_image = utils.ImageReader(signee.signature)
                width, height = reportlab_image.getSize()
                ratio = float(width) / float(height)

                image = Image(signee.signature, width=50 * ratio, height=50)
                image.hAlign = "LEFT"
                elements.append(image)
                elements.append(Paragraph("{}".format(signee.computed_str), styles["Default"]))
    return elements


def add_text_block_with_context(text, invoice, styles):
    elements = list()
    if text:
        elements.append(Paragraph("", styles["Default-Linebreak"]))
        elements.append(Paragraph(Template(text).render(Context(invoice.get_context())), styles["Default-Linebreak"]))
    return elements


def add_transfer_block(invoice, receiver, styles, total_amount_gross):
    elements = list()

    if invoice.is_counterparty_invoice:
        text = f"The amount of <b>{invoice.invoice_currency} {format_invoice_number(total_amount_gross)}</b> will be transfered to the following bank account:"
    else:
        text = f"Please transfer <b>{invoice.invoice_currency} {format_invoice_number(total_amount_gross)}</b> to the following bank account:"

    elements.append(Paragraph(text, styles["Default-Linebreak-Before"]))

    bank_accounts = receiver.banking.all()
    if bank_accounts.exists():
        try:
            bank_account = bank_accounts.get(currency=invoice.invoice_currency)
        except Exception:
            bank_account = bank_accounts.first()

        elements.append(Paragraph(bank_account.institute, styles["Default"]))

        if bank_account.institute_additional:
            elements.append(Paragraph(bank_account.institute_additional, styles["Default"]))

        if bank_account.iban and bank_account.iban != "":
            elements.append(Paragraph(f"IBAN: {bank_account.iban}", styles["Default"]))
        if bank_account.swift_bic:
            elements.append(Paragraph(f"SWIFT: {bank_account.swift_bic}", styles["Default"]))
        if bank_account.additional_information and bank_account.additional_information != "":
            elements.append(Paragraph(bank_account.additional_information, styles["Default"]))

    return elements


def get_gross_and_net_value(invoice):
    multiplier = 1 if not invoice.is_counterparty_invoice else -1

    total_gross = 0
    total_net = 0
    for booking_entry in invoice.booking_entries.all():
        if booking_entry.currency != invoice.invoice_currency:
            conversion_rate = booking_entry.currency.convert(booking_entry.booking_date, invoice.invoice_currency)
            total_net += multiplier * booking_entry.net_value * conversion_rate
            total_gross += multiplier * booking_entry.gross_value * conversion_rate
        else:
            total_net += multiplier * booking_entry.net_value
            total_gross += multiplier * booking_entry.gross_value

    return total_gross, total_net


def add_booking_entries(invoice, styles, inverse=False):
    multiplier = 1 if not invoice.is_counterparty_invoice else -1

    tables = list()
    for vat in invoice.booking_entries.all().distinct("vat").values_list("vat", flat=True):
        table_data = list()

        table_data.append([Paragraph("", styles["Default"])] * 2)
        table_data.append(
            [
                Paragraph("Title", styles["Default-Table-Header"]),
                Paragraph("Amount", styles["Default-Table-Header-Right"]),
            ]
        )

        for booking_entry in invoice.booking_entries.filter(vat=vat).order_by("title"):
            title_col = [Paragraph(f"{booking_entry.title}", styles["Default"])]
            amount_col = list()

            if booking_entry.currency != invoice.invoice_currency:
                conversion_rate = booking_entry.currency.convert(booking_entry.booking_date, invoice.invoice_currency)

                title_col.append(
                    Paragraph(
                        f"<i>1.00 {booking_entry.currency.key} = {conversion_rate:.4f} {invoice.invoice_currency.key}</i>",
                        styles["Annotation"],
                    )
                )

                amount_col.append(
                    Paragraph(
                        f"<i>{format_invoice_number(multiplier * conversion_rate * booking_entry.gross_value)} {invoice.invoice_currency.key}</i>",
                        styles["Default-Right"],
                    )
                )
                amount_col.append(
                    Paragraph(
                        f"{format_invoice_number(multiplier * booking_entry.gross_value)} {booking_entry.currency}",
                        styles["Annotation-Right"],
                    )
                )
            else:
                amount_col.append(
                    Paragraph(
                        f"{format_invoice_number(multiplier * booking_entry.gross_value)} {booking_entry.currency}",
                        styles["Default-Right"],
                    )
                )

            if (
                (params := booking_entry.parameters)
                and (from_date := params.get("from_date"))
                and (to_date := params.get("to_date"))
            ):
                title_col.append(
                    Paragraph(
                        f"<i>{from_date} - {to_date}</i>",
                        styles["Annotation"],
                    )
                )

            table_data.append([title_col, amount_col])

        total_gross, total_net = get_gross_and_net_value(invoice)
        table_data.append([Paragraph("", styles["Default"])] * 2)
        table_data.append(
            [
                [
                    Paragraph("<strong>Total Amount</strong>", styles["Default"]),
                    Paragraph(f"<i>Vat: {vat*100:.2f}%</i>", styles["Annotation"]),
                    Paragraph(f"Total Amount (excl. {vat*100:.2f}% VAT)", styles["Annotation"]),
                ],
                [
                    Paragraph(
                        f"<strong>{format_invoice_number(total_gross)} {invoice.invoice_currency}</strong>",
                        styles["Default-Right"],
                    ),
                    Paragraph(
                        f"<i>{format_invoice_number(total_gross - total_net)} {invoice.invoice_currency}</i>",
                        styles["Annotation-Right"],
                    ),
                    Paragraph(
                        f"{format_invoice_number(total_net)} {invoice.invoice_currency}",
                        styles["Annotation-Right"],
                    ),
                ],
            ]
        )
        table = Table(table_data, colWidths=[A4[0] - 6.4 * cm, 3.5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f37200")),
                    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f38a32")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        tables.append(table)

    return tables
