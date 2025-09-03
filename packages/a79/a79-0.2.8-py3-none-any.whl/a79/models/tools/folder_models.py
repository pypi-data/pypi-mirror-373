from pydantic import BaseModel, Field

from .. import enums
from . import ToolOutput


class ListDatasourcesInput(BaseModel):
    folder_id: int = Field(
        description="The ID of the folder to read datasources from",
        json_schema_extra={"field_type": enums.CustomDataType.FOLDER.value},
    )
    content_type: str = Field(default="", description="Filter by content type")


class ListDatasourcesOutput(ToolOutput):
    datasource_ids: list[int] = Field(default_factory=list)


class FolderPathInput(BaseModel):
    """Input model for folder path operations."""

    folder_path: str = Field(
        description="Path or name of the folder to operate on. Can be folder name or "
        "folder ID as string."
    )


class ListFilesOutput(BaseModel):
    """Output model for listing files in a folder."""

    file_names: list[str] = Field(default_factory=list)
    file_paths: list[str] = Field(default_factory=list)


class ListFoldersOutput(BaseModel):
    """Output model for listing folders."""

    folder_names: list[str] = Field(default_factory=list)
    folder_paths: list[str] = Field(default_factory=list)


class SearchInput(BaseModel):
    """Input model for search operations."""

    folder_path: str = Field(
        description="Path or name of the folder to search in. Can be folder name or "
        "folder ID as string."
    )
    query: str = Field(description="Search query to find relevant content")
    num_results: int = Field(description="Number of results to return", default=5)


class SearchResultItem(BaseModel):
    """Individual search result item."""

    file_path: str = Field(description="Path to the file containing the result")
    chunk_text: str = Field(description="Text content of the matching chunk")
    score: float = Field(description="Relevance score for this result")
    title: str = Field(description="Title or identifier of the source document")
    snippet: str = Field(description="Highlighted snippet showing the match context")


class SearchOutput(BaseModel):
    """Output model for search operations."""

    results: list[SearchResultItem] = Field(default_factory=list)
    total_results: int = Field(description="Total number of search results found")


class SearchNameInput(BaseModel):
    """Input model for searching files by name pattern."""

    pattern: str = Field(
        description="Regex or glob pattern to search for files by name (e.g., '*.txt', "
        "'report_*.pdf')"
    )
    folder_path: str = Field(
        default="root",
        description="Starting folder path to search from. Defaults to 'root' to search "
        "all folders.",
    )


class SearchNameOutput(BaseModel):
    """Output model for file name search."""

    file_paths: list[str] = Field(
        default_factory=list, description="List of file paths matching the name pattern"
    )
