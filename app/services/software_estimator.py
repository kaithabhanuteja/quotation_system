import json

from google.genai import types

from app.config import settings
from app.services.gemini_service import client

from app.industries.software.schemas import (
    SoftwareEstimatePlan,
)

from app.industries.software.calculator import (
    calculate_software_estimate,
)


def generate_software_estimate(email_content: str):

    prompt = f"""
You are a software project estimation assistant.

Analyze the customer's email and prepare a realistic
software project resource plan.

Identify:

1. Project title.
2. Project summary.
3. Required team members.
4. Number of people for each role.
5. Duration for each role in months.
6. Required resources such as laptops and cloud infrastructure.
7. Overall estimated project timeline.
8. Assumptions.
9. Missing information.

Available team roles:

- project_manager
- backend_developer
- frontend_developer
- fullstack_developer
- ui_ux_designer
- qa_engineer
- devops_engineer
- data_engineer

Available resource types:

- laptop
- cloud_infrastructure
- software_license
- testing_tools

IMPORTANT RULES:

- Do not invent customer requirements.
- Do not provide prices or calculate costs.
- Do not add unnecessary team members.
- Use reasonable estimates only where the email lacks details.
- Clearly mention assumptions.
- Identify missing information.
- Return valid JSON only.
- Follow the supplied JSON schema.

CUSTOMER EMAIL:

{email_content[:40000]}
"""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            response_schema=SoftwareEstimatePlan,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty estimation response.")

    try:
        plan_data = json.loads(response.text)

        plan = SoftwareEstimatePlan.model_validate(
            plan_data
        )

    except Exception as error:
        raise ValueError(
            f"Could not validate software estimate: {error}"
        ) from error

    # Python calculates the final estimate.
    quotation = calculate_software_estimate(plan)

    return quotation