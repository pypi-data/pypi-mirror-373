from pydantic import BaseModel, Field

from . import ToolOutput


class SearchInput(BaseModel):
    query: str = Field(description="The search query for Google search.")
    num_results: int = 10
    num_pages: int = 1
    num_extracts: int = 3
    extraction_method: str = "goose"


class SearchOutput(ToolOutput):
    results: list[dict[str, str]]
