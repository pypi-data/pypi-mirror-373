from pydantic import BaseModel, Field


class GetFileContentInput(BaseModel):
    """Input model for file content retrieval operations."""

    file_name: str = Field(description="Name of the file to retrieve content from")


class GetCSVContentInput(BaseModel):
    """Input model specifically for CSV file retrieval with pagination support."""

    file_name: str = Field(description="Name of the CSV file to retrieve content from")
    chunk_size: int = Field(description="Number of rows to return", default=100)
    offset: int = Field(
        description="Number of rows to skip from the beginning", default=0
    )


class GetFileContentOutput(BaseModel):
    """Output model for file content retrieval operations."""

    content: str | bytes = Field(description="File content")


class GetCSVContentOutput(BaseModel):
    """Output model specifically for CSV file retrieval with pagination support."""

    content: str = Field(description="CSV data as JSON string")
    total: int = Field(description="Total number of rows in the CSV file")
    offset: int = Field(description="Offset used for pagination")
    row_count: int = Field(description="Number of rows returned in this response")


class GetFileSearchInput(BaseModel):
    """Input model for file search operations."""

    file_name: str = Field(description="Name of the file to search in")
    query: str = Field(description="Search query to find relevant content")
    num_results: int = Field(description="Number of results to return", default=5)
