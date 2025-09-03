# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any, Literal

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.snowflake_models import (
    CSVDataResponse,
    ExecuteQueryInput,
    ExecuteQueryOutput,
    ReadTableInput,
    ReadTableOutput,
    SnowflakeConfig,
    TableInfo,
    UploadDataInput,
    UploadDataOutput,
)

__all__ = [
    "CSVDataResponse",
    "ExecuteQueryInput",
    "ExecuteQueryOutput",
    "ReadTableInput",
    "ReadTableOutput",
    "SnowflakeConfig",
    "TableInfo",
    "UploadDataInput",
    "UploadDataOutput",
    "upload_data",
    "read_table",
    "execute_query",
]


def upload_data(
    *,
    config: SnowflakeConfig = DEFAULT,
    dataframe: Any,
    table_name: str,
    if_exists: Literal["fail", "replace", "append"] = DEFAULT,
) -> UploadDataOutput:
    """
    Uploads a single dataframe to a Snowflake table.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = UploadDataInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="snowflake", name="upload_data", input=input_model.model_dump()
    )
    return UploadDataOutput.model_validate(output_model)


def read_table(
    *,
    config: SnowflakeConfig,
    table_name: str,
    database: str | None = DEFAULT,
    schema_name: str | None = DEFAULT,
    limit: int | None = DEFAULT,
) -> ReadTableOutput:
    """Reads data from a Snowflake table and returns it as a paginated response."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ReadTableInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="snowflake", name="read_table", input=input_model.model_dump()
    )
    return ReadTableOutput.model_validate(output_model)


def execute_query(
    *, config: SnowflakeConfig, query: str, page: int = DEFAULT, page_size: int = DEFAULT
) -> ExecuteQueryOutput:
    """
    Executes a SQL query against Snowflake and returns paginated results.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ExecuteQueryInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="snowflake", name="execute_query", input=input_model.model_dump()
    )
    return ExecuteQueryOutput.model_validate(output_model)
