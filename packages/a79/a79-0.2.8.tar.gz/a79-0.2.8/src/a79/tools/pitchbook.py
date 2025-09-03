# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.pitchbook_models import (
    GetCompanyInfoInput,
    GetCompanyInfoOutput,
    SearchCompaniesInput,
    SearchCompaniesOutput,
)

__all__ = [
    "GetCompanyInfoInput",
    "GetCompanyInfoOutput",
    "SearchCompaniesInput",
    "SearchCompaniesOutput",
    "search_companies",
    "get_company_info",
]


def search_companies(
    *, data: dict = DEFAULT, params: dict = DEFAULT, timeout: float = DEFAULT
) -> SearchCompaniesOutput:
    """Search for companies using PitchBook API."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchCompaniesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="pitchbook", name="search_companies", input=input_model.model_dump()
    )
    return SearchCompaniesOutput.model_validate(output_model)


def get_company_info(
    *, data: dict = DEFAULT, params: dict = DEFAULT, timeout: float = DEFAULT
) -> GetCompanyInfoOutput:
    """Get detailed information about a specific company."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetCompanyInfoInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="pitchbook", name="get_company_info", input=input_model.model_dump()
    )
    return GetCompanyInfoOutput.model_validate(output_model)
