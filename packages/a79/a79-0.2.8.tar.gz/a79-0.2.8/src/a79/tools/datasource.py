# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.datasource_models import (
    CreateDatasourceInput,
    CreateDatasourceOutput,
    DeleteDatasourceInput,
    DeleteDatasourceOutput,
    Enum,
    FieldFormat,
    ReadDatasourcesOutput,
    SearchDatasourceByNameInput,
    SearchDatasourceByNameOutput,
)

__all__ = [
    "CreateDatasourceInput",
    "CreateDatasourceOutput",
    "DeleteDatasourceInput",
    "DeleteDatasourceOutput",
    "Enum",
    "FieldFormat",
    "ReadDatasourcesOutput",
    "SearchDatasourceByNameInput",
    "SearchDatasourceByNameOutput",
    "create_datasource",
    "search_datasource_by_name",
    "delete_datasource",
]


def create_datasource(
    *,
    content_base64: str = DEFAULT,
    content: str = DEFAULT,
    content_url: str = DEFAULT,
    content_csv: str = DEFAULT,
    content_type: str = DEFAULT,
    file_name: str = DEFAULT,
    folder_id: int | None = DEFAULT,
    wait_time_out: int = DEFAULT,
    skip_vector_indexing: bool = DEFAULT,
) -> CreateDatasourceOutput:
    """
    Write the results of the workflow to a datasource and save it.
    For Excel files (.xlsx), automatically use SharePoint as the storage backend.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateDatasourceInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="datasource", name="create_datasource", input=input_model.model_dump()
    )
    return CreateDatasourceOutput.model_validate(output_model)


def search_datasource_by_name(*, name: str = DEFAULT) -> SearchDatasourceByNameOutput:
    """
    Search for a datasource by name and return its ID if found.

    Args:
        input: SearchDatasourceByNameInput containing the name to search for

    Returns:
        SearchDatasourceByNameOutput containing the datasource ID if found
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchDatasourceByNameInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="datasource",
        name="search_datasource_by_name",
        input=input_model.model_dump(),
    )
    return SearchDatasourceByNameOutput.model_validate(output_model)


def delete_datasource(
    *,
    datasource_id: str,
    bypass_role_check: bool = DEFAULT,
    workflow_name: str | None = DEFAULT,
) -> DeleteDatasourceOutput:
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteDatasourceInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="datasource", name="delete_datasource", input=input_model.model_dump()
    )
    return DeleteDatasourceOutput.model_validate(output_model)
