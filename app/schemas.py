from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class EmailUploadResponse(BaseModel):
    id: int
    source: str
    original_filename: str
    sender: str | None
    subject: str | None
    body: str
    attachment_text: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)




class RequirementExtractionRequest(BaseModel):
    email_id: int = Field(gt=0)


class ExtractedItem(BaseModel):
    name: str
    description: str | None = None
    quantity: float | None = None
    unit: str | None = None
    brand_or_model: str | None = None
    customer_specified: bool = False


class RequirementExtractionResult(BaseModel):
    industry: Literal["software", "civil", "medical", "unknown"]
    confidence: float = Field(ge=0, le=1)
    project_title: str
    customer_name: str | None = None
    customer_email: str | None = None
    project_summary: str
    requirements: list[str] = Field(default_factory=list)
    items: list[ExtractedItem] = Field(default_factory=list)
    requested_timeline: str | None = None
    location: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    assumptions_or_uncertainties: list[str] = Field(default_factory=list)
    source_facts: list[str] = Field(default_factory=list)