
from io import BytesIO
from uuid import uuid4
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
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


NAVY = colors.HexColor("#172554")
BLUE = colors.HexColor("#2563EB")
LIGHT_BLUE = colors.HexColor("#EFF6FF")
GREY = colors.HexColor("#64748B")
LIGHT_GREY = colors.HexColor("#F1F5F9")
DARK = colors.HexColor("#1E293B")


def money(value):
    return f"INR {value:,.2f}"


def generate_software_pdf(quotation, customer):
    buffer = BytesIO()

    quote_number = f"SW-{datetime.now():%Y%m%d}-{uuid4().hex[:6].upper()}"
    quote_date = datetime.now().strftime("%d %B %Y")

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title=f"Software Quotation - {quotation.project_title}",
        author="Quotation Generator",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CompanyTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="SmallText",
        parent=styles["Normal"],
        fontSize=8,
        leading=12,
        textColor=GREY,
    ))

    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=DARK,
    ))

    styles.add(ParagraphStyle(
        name="WhiteHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.white,
    ))

    story = []

    # Header
    story.append(Paragraph(
        "SOFTWARE QUOTATION",
        styles["CompanyTitle"]
    ))

    story.append(Paragraph(
        "Software Development & Technology Services",
        styles["SmallText"]
    ))

    story.append(Spacer(1, 8))

    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=BLUE,
        spaceAfter=12,
    ))

    # Quotation details
    quote_data = [
        [
            Paragraph("<b>Quotation Number</b>", styles["BodyTextCustom"]),
            quote_number,
            Paragraph("<b>Date</b>", styles["BodyTextCustom"]),
            quote_date,
        ],
        [
            Paragraph("<b>Industry</b>", styles["BodyTextCustom"]),
            "Software",
            Paragraph("<b>Currency</b>", styles["BodyTextCustom"]),
            "INR",
        ],
    ]

    quote_table = Table(
        quote_data,
        colWidths=[32 * mm, 55 * mm, 20 * mm, 45 * mm],
    )

    quote_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(quote_table)

    # Customer details
    story.append(Paragraph(
        "CUSTOMER DETAILS",
        styles["SectionHeading"]
    ))

    customer_name = customer.get("name") or "Not provided"
    customer_email = customer.get("email") or "Not provided"

    customer_data = [
        ["Customer Name", customer_name],
        ["Email Address", customer_email],
    ]

    customer_table = Table(
        customer_data,
        colWidths=[45 * mm, 120 * mm],
    )

    customer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREY),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(customer_table)

    # Project details
    story.append(Paragraph(
        "PROJECT OVERVIEW",
        styles["SectionHeading"]
    ))

    story.append(Paragraph(
        f"<b>{quotation.project_title}</b>",
        styles["BodyTextCustom"]
    ))

    story.append(Spacer(1, 5))

    story.append(Paragraph(
        quotation.project_summary,
        styles["BodyTextCustom"]
    ))

    story.append(Spacer(1, 5))

    story.append(Paragraph(
        f"<b>Estimated Timeline:</b> "
        f"{quotation.estimated_timeline_months} months",
        styles["BodyTextCustom"]
    ))

    # Team details
    story.append(Paragraph(
        "PROJECT TEAM",
        styles["SectionHeading"]
    ))

    team_data = [[
        Paragraph("Role", styles["WhiteHeader"]),
        Paragraph("Members", styles["WhiteHeader"]),
        Paragraph("Duration", styles["WhiteHeader"]),
        Paragraph("Responsibilities", styles["WhiteHeader"]),
    ]]

    for member in quotation.team:
        team_data.append([
            member.role.replace("_", " ").title(),
            str(member.headcount),
            f"{member.duration_months} months",
            Paragraph(
                member.responsibilities or "-",
                styles["BodyTextCustom"]
            ),
        ])

    team_table = Table(
        team_data,
        colWidths=[40 * mm, 20 * mm, 30 * mm, 75 * mm],
        repeatRows=1,
    )

    team_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white, LIGHT_GREY
        ]),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(team_table)

    # Pricing details
    story.append(Paragraph(
        "COST BREAKDOWN",
        styles["SectionHeading"]
    ))

    pricing_data = [[
        Paragraph("Description", styles["WhiteHeader"]),
        Paragraph("Quantity", styles["WhiteHeader"]),
        Paragraph("Unit", styles["WhiteHeader"]),
        Paragraph("Unit Rate", styles["WhiteHeader"]),
        Paragraph("Total", styles["WhiteHeader"]),
    ]]

    for item in quotation.line_items:
        pricing_data.append([
            item.description,
            f"{item.quantity:g}",
            item.unit,
            money(item.unit_rate),
            money(item.total),
        ])

    pricing_table = Table(
        pricing_data,
        colWidths=[48 * mm, 22 * mm, 30 * mm, 35 * mm, 30 * mm],
        repeatRows=1,
    )

    pricing_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white, LIGHT_GREY
        ]),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(pricing_table)
    story.append(Spacer(1, 10))

    # Total
    total_table = Table(
        [
            ["Estimated Subtotal", money(quotation.subtotal)]
        ],
        colWidths=[125 * mm, 40 * mm],
    )

    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, -1), NAVY),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    story.append(total_table)

    # Assumptions
    story.append(Paragraph(
        "ASSUMPTIONS",
        styles["SectionHeading"]
    ))

    if quotation.assumptions:
        for assumption in quotation.assumptions:
            story.append(Paragraph(
                f"• {assumption}",
                styles["BodyTextCustom"]
            ))
    else:
        story.append(Paragraph(
            "No assumptions provided.",
            styles["BodyTextCustom"]
        ))

    # Missing information
    story.append(Paragraph(
        "PENDING CUSTOMER INFORMATION",
        styles["SectionHeading"]
    ))

    if quotation.missing_information:
        for item in quotation.missing_information:
            story.append(Paragraph(
                f"• {item}",
                styles["BodyTextCustom"]
            ))
    else:
        story.append(Paragraph(
            "No additional information currently requested.",
            styles["BodyTextCustom"]
        ))

    # Pricing note
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        f"<b>Pricing note:</b> {quotation.pricing_note}",
        styles["SmallText"]
    ))

    story.append(Spacer(1, 12))

    story.append(HRFlowable(
        width="100%",
        thickness=0.6,
        color=GREY,
    ))

    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "This quotation is indicative and subject to review, "
        "confirmation of requirements, and commercial approval.",
        styles["SmallText"]
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
