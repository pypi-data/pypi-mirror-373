# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.sourcescrub_models import (
    GetCompanyByCompanyIdentifierInput,
    GetCompanyByCompanyIdentifierOutput,
    GetCompanyInfoInput,
    GetCompanyInfoOutput,
    GetMarketIntelligenceInput,
    GetMarketIntelligenceOutput,
    GetSourcesByCompanyIdentifierInput,
    GetSourcesByCompanyIdentifierOutput,
    SearchCompaniesInput,
    SearchCompaniesOutput,
    SearchSourcesInput,
    SearchSourcesOutput,
)

__all__ = [
    "GetCompanyByCompanyIdentifierInput",
    "GetCompanyByCompanyIdentifierOutput",
    "GetCompanyInfoInput",
    "GetCompanyInfoOutput",
    "GetMarketIntelligenceInput",
    "GetMarketIntelligenceOutput",
    "GetSourcesByCompanyIdentifierInput",
    "GetSourcesByCompanyIdentifierOutput",
    "SearchCompaniesInput",
    "SearchCompaniesOutput",
    "SearchSourcesInput",
    "SearchSourcesOutput",
    "get_company_info",
    "search_companies",
    "get_market_intelligence",
    "get_company_by_company_identifier",
    "get_sources_by_company_identifier",
    "search_sources",
]


def get_company_info(
    *, domain: str, data: dict[str, Any] = DEFAULT, timeout: float = DEFAULT
) -> GetCompanyInfoOutput:
    """Get detailed information about a specific company by domain."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetCompanyInfoInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="sourcescrub", name="get_company_info", input=input_model.model_dump()
    )
    return GetCompanyInfoOutput.model_validate(output_model)


def search_companies(
    *, data: dict[str, Any] = DEFAULT, timeout: float = DEFAULT
) -> SearchCompaniesOutput:
    """Search for companies using SourceScrub API."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchCompaniesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="sourcescrub", name="search_companies", input=input_model.model_dump()
    )
    return SearchCompaniesOutput.model_validate(output_model)


def get_market_intelligence(
    *, company_identifier: str = DEFAULT, timeout: float = DEFAULT
) -> GetMarketIntelligenceOutput:
    """Search market intelligence by company identifier using SourceScrub API."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetMarketIntelligenceInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="sourcescrub",
        name="get_market_intelligence",
        input=input_model.model_dump(),
    )
    return GetMarketIntelligenceOutput.model_validate(output_model)


def get_company_by_company_identifier(
    *, company_identifier: str = DEFAULT, timeout: float = DEFAULT
) -> GetCompanyByCompanyIdentifierOutput:
    """Get company by company identifier using SourceScrub API."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetCompanyByCompanyIdentifierInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="sourcescrub",
        name="get_company_by_company_identifier",
        input=input_model.model_dump(),
    )
    return GetCompanyByCompanyIdentifierOutput.model_validate(output_model)


def get_sources_by_company_identifier(
    *, company_identifier: str = DEFAULT, timeout: float = DEFAULT
) -> GetSourcesByCompanyIdentifierOutput:
    """Get sources by company identifier using SourceScrub API."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetSourcesByCompanyIdentifierInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="sourcescrub",
        name="get_sources_by_company_identifier",
        input=input_model.model_dump(),
    )
    return GetSourcesByCompanyIdentifierOutput.model_validate(output_model)


def search_sources(
    *, data: dict[str, Any] = DEFAULT, timeout: float = DEFAULT
) -> SearchSourcesOutput:
    """Search sources using SourceScrub API."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchSourcesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="sourcescrub", name="search_sources", input=input_model.model_dump()
    )
    return SearchSourcesOutput.model_validate(output_model)
