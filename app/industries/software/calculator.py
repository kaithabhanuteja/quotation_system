from app.industries.software.schemas import (
    SoftwareEstimatePlan,
    SoftwareEstimateResponse,
    QuotationLineItem,
)

from app.industries.software.rates import (
    SOFTWARE_ROLE_RATES,
    SOFTWARE_RESOURCE_RATES,
    CURRENCY,
)


def calculate_software_estimate(
    plan: SoftwareEstimatePlan
) -> SoftwareEstimateResponse:

    line_items = []
    subtotal = 0.0

    # Calculate team costs
    for member in plan.team:

        monthly_rate = SOFTWARE_ROLE_RATES[member.role]

        total = (
            member.headcount
            * member.duration_months
            * monthly_rate
        )

        line_items.append(
            QuotationLineItem(
                description=f"{member.role.replace('_', ' ').title()}",
                quantity=member.headcount * member.duration_months,
                unit="person-month",
                unit_rate=monthly_rate,
                total=round(total, 2),
            )
        )

        subtotal += total

    # Calculate software resources
    for resource in plan.resources:

        unit_rate = SOFTWARE_RESOURCE_RATES[
            resource.resource_type
        ]

        if resource.resource_type == "laptop":
            # One-time purchase cost
            total = resource.quantity * unit_rate
            unit = "unit"

        else:
            # Monthly recurring resource cost
            total = (
                resource.quantity
                * resource.duration_months
                * unit_rate
            )
            unit = "quantity-month"

        line_items.append(
            QuotationLineItem(
                description=resource.resource_type.replace(
                    "_", " "
                ).title(),
                quantity=resource.quantity,
                unit=unit,
                unit_rate=unit_rate,
                total=round(total, 2),
            )
        )

        subtotal += total

    return SoftwareEstimateResponse(
        project_title=plan.project_title,
        project_summary=plan.project_summary,
        team=plan.team,
        line_items=line_items,
        subtotal=round(subtotal, 2),
        estimated_timeline_months=plan.estimated_timeline_months,
        assumptions=plan.assumptions,
        missing_information=plan.missing_information,
        pricing_note=(
            "Indicative estimate based on configurable sample rates. "
            "Actual costs require business review and approval."
        ),
    )