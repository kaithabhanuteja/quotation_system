from typing import Literal
from pydantic import BaseModel, Field


class SoftwareRole(BaseModel):
    role: Literal[
        "project_manager",
        "backend_developer",
        "frontend_developer",
        "fullstack_developer",
        "ui_ux_designer",
        "qa_engineer",
        "devops_engineer",
        "data_engineer"
    ]

    headcount: int = Field(gt=0)
    duration_months: float = Field(gt=0)
    responsibilities: str


class SoftwareResource(BaseModel):
    resource_type: Literal[
        "laptop",
        "cloud_infrastructure",
        "software_license",
        "testing_tools"
    ]

    quantity: int = Field(gt=0)
    duration_months: float = Field(default=1, gt=0)
    purpose: str


class SoftwareEstimatePlan(BaseModel):
    project_title: str
    project_summary: str

    team: list[SoftwareRole] = Field(default_factory=list)

    resources: list[SoftwareResource] = Field(default_factory=list)

    estimated_timeline_months: float = Field(gt=0)

    assumptions: list[str] = Field(default_factory=list)

    missing_information: list[str] = Field(default_factory=list)


class QuotationLineItem(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_rate: float
    total: float


class SoftwareEstimateResponse(BaseModel):
    industry: str = "software"
    project_title: str
    project_summary: str

    team: list[SoftwareRole]

    line_items: list[QuotationLineItem]

    subtotal: float
    currency: str = "INR"

    estimated_timeline_months: float

    assumptions: list[str]
    missing_information: list[str]

    pricing_note: str