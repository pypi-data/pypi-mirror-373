from pydantic import BaseModel

from . import ToolOutput


class GetLatestCompanyFilingTextInput(BaseModel):
    company_identifier: str
    filing_types: list[str]


class GetLatestCompanyFilingTextOutput(ToolOutput):
    content: dict[str, str]
