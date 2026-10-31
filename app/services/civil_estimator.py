
import json

from google.genai import types

from app.config import settings
from app.services.gemini_service import client

from app.industries.civil.schemas import CivilEstimatePlan
from app.industries.civil.calculator import calculate_civil_estimate


def generate_civil_estimate(email_content: str):

    prompt = f"""
You are a civil construction estimation assistant.

Analyze the customer enquiry and create a structured
civil construction resource estimate.

Extract or estimate:

1. Project title and summary.
2. Project area and location, if provided.
3. Required construction materials and quantities.
4. Labour requirements and person-days.
5. Machinery requirements and operating hours/trips.
6. Estimated project timeline in months.
7. Assumptions.
8. Missing information.

Only use these rate keys:

Materials:
- cement_bag (unit: bag)
- steel_kg (unit: kg)
- sand_cubic_ft (unit: cubic_ft)
- aggregate_cubic_ft (unit: cubic_ft)
- brick_piece (unit: piece)

Labour:
- mason_day (unit: person_day)
- helper_day (unit: person_day)
- supervisor_day (unit: person_day)

Machinery:
- excavator_hour (unit: hour)
- concrete_mixer_hour (unit: hour)
- truck_trip (unit: trip)

IMPORTANT:
- Do not return prices or calculate costs.
- Never present guessed quantities as customer-confirmed facts.
- If estimating quantities, clearly mention the assumptions.
- Do not invent project area, dimensions or specifications.
- If drawings, measurements or structural details are missing,
  list them under missing_information.
- Do not create unnecessary items.
- Return valid JSON matching the supplied schema.

CUSTOMER ENQUIRY:
{email_content[:40000]}
"""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            response_schema=CivilEstimatePlan,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty civil estimate.")

    try:
        plan_data = json.loads(response.text)
        plan = CivilEstimatePlan.model_validate(plan_data)

    except Exception as error:
        raise ValueError(
            f"Could not validate civil estimate: {error}"
        ) from error

    return calculate_civil_estimate(plan)
