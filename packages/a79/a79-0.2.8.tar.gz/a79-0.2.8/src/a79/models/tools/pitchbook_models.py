import typing as t

from pydantic import BaseModel, Field

from . import ToolOutput


class SearchCompaniesInput(BaseModel):
    """Input data for the PitchBook Tool."""

    data: dict = Field(default={}, description="Parameter to provide payload.")
    params: dict = Field(
        default={}, description="Parameter to provide GET parameters in URL."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class SearchCompaniesOutput(ToolOutput):
    """Output data from the PitchBook Tool."""

    content: t.Any = Field(
        default=None, description="Structured content from the operation"
    )


class GetCompanyInfoInput(BaseModel):
    """Input data for the PitchBook Tool."""

    data: dict = Field(default={}, description="Parameter to provide payload.")
    params: dict = Field(
        default={}, description="Parameter to provide GET parameters in URL."
    )
    timeout: float = Field(default=60, description="Request timeout in seconds")


class GetCompanyInfoOutput(ToolOutput):
    """Output data from the PitchBook Tool."""

    content: t.Any = Field(
        default=None, description="Structured content from the operation"
    )
