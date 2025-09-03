# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.edgartool_models import (
    GetLatestCompanyFilingTextInput,
    GetLatestCompanyFilingTextOutput,
)

__all__ = [
    "GetLatestCompanyFilingTextInput",
    "GetLatestCompanyFilingTextOutput",
    "get_latest_company_filing_text",
]


def get_latest_company_filing_text(
    *, company_identifier: str, filing_types: list[str]
) -> GetLatestCompanyFilingTextOutput:
    """Get the latest company filing text by company identifier and filing types
    using Edgar API."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetLatestCompanyFilingTextInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="edgartool",
        name="get_latest_company_filing_text",
        input=input_model.model_dump(),
    )
    return GetLatestCompanyFilingTextOutput.model_validate(output_model)
