# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.file_models import (
    GetCSVContentInput,
    GetCSVContentOutput,
    GetFileContentInput,
    GetFileContentOutput,
    GetFileSearchInput,
)
from ..models.tools.folder_models import SearchOutput

__all__ = [
    "GetCSVContentInput",
    "GetCSVContentOutput",
    "GetFileContentInput",
    "GetFileContentOutput",
    "GetFileSearchInput",
    "SearchOutput",
    "read_csv",
    "read_document",
    "extract_audio_transcript",
    "search",
]


def read_csv(
    *, file_name: str, chunk_size: int = DEFAULT, offset: int = DEFAULT
) -> GetCSVContentOutput:
    """Read CSV file content from PostgreSQL table and return as DataFrame.

    This tool reads CSV files that have been uploaded and stored as PostgreSQL tables.
    It supports pagination through chunk_size and offset parameters.

    Args:
        input: GetCSVContentInput containing file_name, chunk_size, and offset

    Returns:
        GetCSVContentOutput containing CSV data as DataFrame and pagination metadata
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetCSVContentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="file", name="read_csv", input=input_model.model_dump()
    )
    return GetCSVContentOutput.model_validate(output_model)


def read_document(*, file_name: str) -> GetFileContentOutput:
    """Read PDF file content and return as extracted text.

    This tool specifically handles PDF files and returns the extracted text
    content along with PDF-specific metadata.

    Args:
        input: GetFileContentInput containing file_name to query

    Returns:
        GetFileContentOutput containing PDF text content and metadata
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetFileContentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="file", name="read_document", input=input_model.model_dump()
    )
    return GetFileContentOutput.model_validate(output_model)


def extract_audio_transcript(*, file_name: str) -> GetFileContentOutput:
    """Extract transcript from audio file.

    This tool specifically handles audio files and returns the extracted
    transcript text.

    Args:
        input: GetFileContentInput containing file_name to query

    Returns:
        GetFileContentOutput containing audio transcript and metadata
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetFileContentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="file", name="extract_audio_transcript", input=input_model.model_dump()
    )
    return GetFileContentOutput.model_validate(output_model)


def search(*, file_name: str, query: str, num_results: int = DEFAULT) -> SearchOutput:
    """Search for content within a specific file using semantic and lexical search.

    This tool performs hybrid search (combining semantic and lexical search) within
    a specific file using Vespa indexing. Results are ranked by relevance score
    and include highlighted snippets.

    Args:
        input: SearchInput containing folder_path (treated as file_name) and search query

    Returns:
        SearchOutput containing ranked search results with scores and snippets
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetFileSearchInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="file", name="search", input=input_model.model_dump()
    )
    return SearchOutput.model_validate(output_model)
