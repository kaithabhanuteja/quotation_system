
from app.industries.civil.schemas import (
    CivilEstimatePlan,
    CivilEstimateResponse,
    CivilQuotationLineItem,
)

from app.industries.civil.rates import CIVIL_RATES


def calculate_civil_estimate(
    plan: CivilEstimatePlan
) -> CivilEstimateResponse:

    line_items = []

    material_total = 0.0
    labour_total = 0.0
    machinery_total = 0.0

    for item in plan.items:

        unit_rate = CIVIL_RATES[item.rate_key]
        total = round(item.quantity * unit_rate, 2)

        line_items.append(
            CivilQuotationLineItem(
                category=item.category,
                description=item.item_name,
                quantity=item.quantity,
                unit=item.unit,
                unit_rate=unit_rate,
                total=total,
            )
        )

        if item.category == "material":
            material_total += total

        elif item.category == "labour":
            labour_total += total

        elif item.category == "machinery":
            machinery_total += total

    subtotal = (
        material_total
        + labour_total
        + machinery_total
    )

    return CivilEstimateResponse(
        project_title=plan.project_title,
        project_summary=plan.project_summary,
        project_area=plan.project_area,
        location=plan.location,
        line_items=line_items,
        material_total=round(material_total, 2),
        labour_total=round(labour_total, 2),
        machinery_total=round(machinery_total, 2),
        subtotal=round(subtotal, 2),
        estimated_timeline_months=plan.estimated_timeline_months,
        assumptions=plan.assumptions,
        missing_information=plan.missing_information,
        pricing_note=(
            "Indicative estimate using configurable sample rates. "
            "Material quantities, site conditions, specifications and "
            "rates require verification by a qualified professional."
        ),
    )
