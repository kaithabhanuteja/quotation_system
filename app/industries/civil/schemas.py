
from typing import Literal
from pydantic import BaseModel, Field


class CivilCostItem(BaseModel):
    category: Literal["material", "labour", "machinery"]

    item_name: str

    rate_key: Literal[
        "cement_bag",
        "steel_kg",
        "sand_cubic_ft",
        "aggregate_cubic_ft",
        "brick_piece",
        "mason_day",
        "helper_day",
        "supervisor_day",
        "excavator_hour",
        "concrete_mixer_hour",
        "truck_trip",
    ]

    quantity: float = Field(gt=0)
    unit: str
    description: str = ""


class CivilEstimatePlan(BaseModel):
    project_title: str
    project_summary: str

    project_area: str | None = None
    location: str | None = None

    items: list[CivilCostItem] = Field(default_factory=list)

    estimated_timeline_months: float = Field(gt=0)

    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class CivilQuotationLineItem(BaseModel):
    category: str
    description: str
    quantity: float
    unit: str
    unit_rate: float
    total: float


class CivilEstimateResponse(BaseModel):
    industry: str = "civil"
    project_title: str
    project_summary: str
    project_area: str | None
    location: str | None

    line_items: list[CivilQuotationLineItem]

    material_total: float
    labour_total: float
    machinery_total: float
    subtotal: float

    currency: str = "INR"
    estimated_timeline_months: float

    assumptions: list[str]
    missing_information: list[str]

    pricing_note: str
