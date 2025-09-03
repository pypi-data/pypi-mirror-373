import typing as t

from pydantic import BaseModel, Field

from . import ToolOutput


class GetCompanyInfoInput(BaseModel):
    domain: str
    data: dict[str, t.Any] = Field(
        default_factory=dict, description="Parameter to provide payload."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class GetCompanyInfoOutput(ToolOutput):
    content: dict[str, t.Any]


class SearchCompaniesInput(BaseModel):
    data: dict[str, t.Any] = Field(
        default_factory=dict, description="Parameter to provide payload."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class SearchCompaniesOutput(ToolOutput):
    content: dict[str, t.Any]


class GetMarketIntelligenceInput(BaseModel):
    company_identifier: str = Field(
        default="", description="Parameter to provide payload."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class GetMarketIntelligenceOutput(ToolOutput):
    content: dict[str, t.Any]


class GetCompanyByCompanyIdentifierInput(BaseModel):
    company_identifier: str = Field(
        default="", description="Parameter to provide payload."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class GetCompanyByCompanyIdentifierOutput(ToolOutput):
    content: dict[str, t.Any]


class GetSourcesByCompanyIdentifierInput(BaseModel):
    company_identifier: str = Field(
        default="", description="Parameter to provide payload."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class GetSourcesByCompanyIdentifierOutput(ToolOutput):
    content: dict[str, t.Any]


class SearchSourcesInput(BaseModel):
    data: dict[str, t.Any] = Field(
        default_factory=dict, description="Parameter to provide payload."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class SearchSourcesOutput(ToolOutput):
    content: dict[str, t.Any]
