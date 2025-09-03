from typing import Optional

from pydantic import BaseModel, Field

from . import ToolOutput


class MergeContentInput(BaseModel):
    """Input data model for MergeContent node."""

    separator: str = Field(
        default="\n\n\n\n", description="Separator to use between merged content sections"
    )
    content_headers: list[str] = Field(
        default=[], description="Headers for content sections"
    )
    content_texts: list[str] = Field(default=[], description="Texts for content sections")
    indent_level: int = Field(
        default=0, description="Indent level for the merged content"
    )
    title: Optional[str] = Field(default=None, description="Title for the merged content")


class MergeContentOutput(ToolOutput):
    """Output data model for MergeContent node."""

    merged_content: str = Field(
        default="",
        description="Merged content from multiple nodes with formatted headers",
    )
