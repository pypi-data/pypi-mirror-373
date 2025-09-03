# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.folder_models import (
    FolderPathInput,
    ListDatasourcesInput,
    ListDatasourcesOutput,
    ListFilesOutput,
    ListFoldersOutput,
    SearchInput,
    SearchNameInput,
    SearchNameOutput,
    SearchOutput,
    SearchResultItem,
)

__all__ = [
    "FolderPathInput",
    "ListDatasourcesInput",
    "ListDatasourcesOutput",
    "ListFilesOutput",
    "ListFoldersOutput",
    "SearchInput",
    "SearchNameInput",
    "SearchNameOutput",
    "SearchOutput",
    "SearchResultItem",
    "list_datasources",
    "list_files",
    "list_folders",
    "search",
    "search_files_by_name",
]


def list_datasources(
    *, folder_id: int, content_type: str = DEFAULT
) -> ListDatasourcesOutput:
    """
    Lists all datasources in a folder.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListDatasourcesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="folder", name="list_datasources", input=input_model.model_dump()
    )
    return ListDatasourcesOutput.model_validate(output_model)


def list_files(*, folder_path: str) -> ListFilesOutput:
    """List all files (datasources) in the specified folder.

    This tool lists all datasources (files) contained within a folder,
    returning both file names and their identifiers.

    Args:
        input: FolderPathInput containing folder_path to list files from

    Returns:
        ListFilesOutput containing file names and paths
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FolderPathInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="folder", name="list_files", input=input_model.model_dump()
    )
    return ListFilesOutput.model_validate(output_model)


def list_folders(*, folder_path: str) -> ListFoldersOutput:
    """List all subfolders in the specified folder.

    This tool lists all subfolders contained within a folder,
    returning folder names and their relative paths.

    Args:
        input: FolderPathInput containing folder_path to list subfolders from

    Returns:
        ListFoldersOutput containing folder names and relative paths
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FolderPathInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="folder", name="list_folders", input=input_model.model_dump()
    )
    return ListFoldersOutput.model_validate(output_model)


def search(*, folder_path: str, query: str, num_results: int = DEFAULT) -> SearchOutput:
    """Search for content within the specified folder using semantic and lexical search.

    This tool performs hybrid search (combining semantic and lexical search) across
    all files in the specified folder using Vespa indexing. Results are ranked by
    relevance score and include highlighted snippets.

    Args:
        input: SearchInput containing folder_path and search query

    Returns:
        SearchOutput containing ranked search results with scores and snippets
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="folder", name="search", input=input_model.model_dump()
    )
    return SearchOutput.model_validate(output_model)


def search_files_by_name(*, pattern: str, folder_path: str = DEFAULT) -> SearchNameOutput:
    """Search for files by filename pattern.

    This tool searches for files where the filename (not the full path) matches
    the specified pattern. It's useful for finding files with specific naming
    conventions regardless of their folder location.

    Args:
        input: SearchNameInput containing pattern and optional folder_path

    Returns:
        SearchNameOutput containing list of matching file paths
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchNameInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="folder", name="search_files_by_name", input=input_model.model_dump()
    )
    return SearchNameOutput.model_validate(output_model)
