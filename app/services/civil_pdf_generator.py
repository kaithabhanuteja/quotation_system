
from io import BytesIO
from uuid import uuid4
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


NAVY = colors.HexColor("#17324D")
GREEN = colors.HexColor("#2E7D5B")
LIGHT_GREEN = colors.HexColor("#EAF4EF")
LIGHT_GREY = colors.HexColor("#F1F5F9")
DARK = colors.HexColor("#263238")
GREY = colors.HexColor("#64748B")


def money(value):
    return f"INR {value:,.2f}"


def safe(value):
    return escape(str(value or "-"))


def generate_civil_pdf(quotation, customer):

    buffer = BytesIO()

    quote_number = (
        f"CIV-{datetime.now():%Y%m%d}-"
        f"{uuid4().hex[:6].upper()}"
    )

    quote_date = datetime.now().strftime("%d %B %Y")

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=f"Civil Quotation - {quotation.project_title}",
        author="Quotation Generator",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CivilTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="CivilSection",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="CivilBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=DARK,
    ))

    styles.add(ParagraphStyle(
        name="CivilSmall",
        parent=styles["Normal"],
        fontSize=8,
        leading=12,
        textColor=GREY,
    ))

    styles.add(ParagraphStyle(
        name="CivilWhite",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=colors.white,
    ))

    story = []

    # Header
    story.append(Paragraph(
        "CIVIL CONSTRUCTION",
        styles["CivilTitle"]
    ))

    story.append(Paragraph(
        "PROJECT ESTIMATION & COST PROPOSAL",
        styles["CivilSmall"]
    ))

    story.append(Spacer(1, 8))

    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=GREEN,
        spaceAfter=12,
    ))

    # Quotation information
    details = [
        ["Quotation Number", quote_number,
         "Quotation Date", quote_date],
        ["Industry", "Civil / Construction",
         "Currency", "INR"],
    ]

    details_table = Table(
        details,
        colWidths=[32 * mm, 55 * mm, 25 * mm, 45 * mm],
    )

    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.white),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(details_table)

    # Customer details
    story.append(Paragraph(
        "CUSTOMER DETAILS",
        styles["CivilSection"]
    ))

    customer_data = [
        ["Customer Name", safe(customer.get("name"))],
        ["Email Address", safe(customer.get("email"))],
    ]

    customer_table = Table(
        customer_data,
        colWidths=[45 * mm, 120 * mm],
    )

    customer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(customer_table)

    # Project overview
    story.append(Paragraph(
        "PROJECT OVERVIEW",
        styles["CivilSection"]
    ))

    story.append(Paragraph(
        f"<b>{safe(quotation.project_title)}</b>",
        styles["CivilBody"]
    ))

    story.append(Spacer(1, 5))

    story.append(Paragraph(
        safe(quotation.project_summary),
        styles["CivilBody"]
    ))

    story.append(Spacer(1, 5))

    story.append(Paragraph(
        f"<b>Project Area:</b> {safe(quotation.project_area)}",
        styles["CivilBody"]
    ))

    story.append(Paragraph(
        f"<b>Project Location:</b> {safe(quotation.location)}",
        styles["CivilBody"]
    ))

    story.append(Paragraph(
        f"<b>Estimated Timeline:</b> "
        f"{quotation.estimated_timeline_months} months",
        styles["CivilBody"]
    ))

    # Cost breakdown
    story.append(Paragraph(
        "CONSTRUCTION COST BREAKDOWN",
        styles["CivilSection"]
    ))

    pricing_data = [[
        Paragraph("Category", styles["CivilWhite"]),
        Paragraph("Description", styles["CivilWhite"]),
        Paragraph("Quantity", styles["CivilWhite"]),
        Paragraph("Unit", styles["CivilWhite"]),
        Paragraph("Rate", styles["CivilWhite"]),
        Paragraph("Amount", styles["CivilWhite"]),
    ]]

    for item in quotation.line_items:
        pricing_data.append([
            safe(item.category.title()),
            Paragraph(safe(item.description), styles["CivilBody"]),
            f"{item.quantity:g}",
            safe(item.unit),
            money(item.unit_rate),
            money(item.total),
        ])

    pricing_table = Table(
        pricing_data,
        colWidths=[
            25 * mm, 43 * mm, 20 * mm,
            20 * mm, 28 * mm, 31 * mm
        ],
        repeatRows=1,
    )

    pricing_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white, LIGHT_GREY
        ]),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(pricing_table)
    story.append(Spacer(1, 12))

    # Category totals
    totals_data = [
        ["Material Cost", money(quotation.material_total)],
        ["Labour Cost", money(quotation.labour_total)],
        ["Machinery Cost", money(quotation.machinery_total)],
        ["Estimated Subtotal", money(quotation.subtotal)],
    ]

    totals_table = Table(
        totals_data,
        colWidths=[120 * mm, 45 * mm],
    )

    totals_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 2), LIGHT_GREY),
        ("BACKGROUND", (0, 3), (-1, 3), LIGHT_GREEN),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), NAVY),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(totals_table)

    # Assumptions
    story.append(Paragraph(
        "ESTIMATION ASSUMPTIONS",
        styles["CivilSection"]
    ))

    if quotation.assumptions:
        for assumption in quotation.assumptions:
            story.append(Paragraph(
                f"- {safe(assumption)}",
                styles["CivilBody"]
            ))
    else:
        story.append(Paragraph(
            "No assumptions provided.",
            styles["CivilBody"]
        ))

    # Missing information
    story.append(Paragraph(
        "PENDING INFORMATION",
        styles["CivilSection"]
    ))

    if quotation.missing_information:
        for item in quotation.missing_information:
            story.append(Paragraph(
                f"- {safe(item)}",
                styles["CivilBody"]
            ))
    else:
        story.append(Paragraph(
            "No additional information currently requested.",
            styles["CivilBody"]
        ))

    story.append(Spacer(1, 12))

    story.append(Paragraph(
        f"<b>Pricing note:</b> {safe(quotation.pricing_note)}",
        styles["CivilSmall"]
    ))

    story.append(Spacer(1, 10))

    story.append(HRFlowable(
        width="100%",
        thickness=0.6,
        color=GREY,
    ))

    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "This is an indicative estimate, not a final engineering "
        "or construction commitment. Quantities, drawings, structural "
        "specifications, site conditions and supplier rates must be "
        "verified by qualified professionals before approval.",
        styles["CivilSmall"]
    ))

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY)

        canvas.drawString(
            18 * mm,
            10 * mm,
            f"Quotation: {quote_number}"
        )

        canvas.drawRightString(
            A4[0] - 18 * mm,
            10 * mm,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    buffer.seek(0)

    return buffer, quote_number
