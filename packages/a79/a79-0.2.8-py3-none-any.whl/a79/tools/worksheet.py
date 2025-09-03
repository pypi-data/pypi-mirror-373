# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.worksheet_models import (
    CreateEnrichmentInput,
    CreateEnrichmentOutput,
    CreateWorksheetInput,
    CreateWorksheetOutput,
    ReadWorksheetInput,
    ReadWorksheetOutput,
)

__all__ = [
    "CreateEnrichmentInput",
    "CreateEnrichmentOutput",
    "CreateWorksheetInput",
    "CreateWorksheetOutput",
    "ReadWorksheetInput",
    "ReadWorksheetOutput",
    "read_worksheet",
    "create_worksheet",
    "create_enrichment",
]


def read_worksheet(
    *,
    worksheet_id: str = DEFAULT,
    tabular_filter_json: str = DEFAULT,
    column_list: list[str] = DEFAULT,
    page_size: int = DEFAULT,
) -> ReadWorksheetOutput:
    """Given a worksheet id, it will read the worksheet and return the content."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ReadWorksheetInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="worksheet", name="read_worksheet", input=input_model.model_dump()
    )
    return ReadWorksheetOutput.model_validate(output_model)


def create_worksheet(
    *,
    name: str = DEFAULT,
    description: str = DEFAULT,
    datasource_ids: list[int] = DEFAULT,
) -> CreateWorksheetOutput:
    """Create a worksheet from a list of datasources."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateWorksheetInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="worksheet", name="create_worksheet", input=input_model.model_dump()
    )
    return CreateWorksheetOutput.model_validate(output_model)


def create_enrichment(
    *,
    name: str = DEFAULT,
    description: str = DEFAULT,
    worksheet_id: int = DEFAULT,
    function_type: str | None = DEFAULT,
    function_data: dict[str, Any] = DEFAULT,
    column_mapping: list[dict[str, Any]] = DEFAULT,
    new_column_name: str | None = DEFAULT,
) -> CreateEnrichmentOutput:
    """Add a column to a worksheet with a specified enrichment function."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateEnrichmentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="worksheet", name="create_enrichment", input=input_model.model_dump()
    )
    return CreateEnrichmentOutput.model_validate(output_model)
