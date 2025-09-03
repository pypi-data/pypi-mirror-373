import os
import typing as t

from pydantic import BaseModel, Field

from ..core import CSVDataResponse
from . import ToolOutput


class SnowflakeConfig(BaseModel):
    account_name: str | None = Field(
        default=os.getenv("SNOWFLAKE_ACCOUNT", ""), description="Snowflake account name"
    )
    username: str | None = Field(
        default=os.getenv("SNOWFLAKE_USERNAME", ""), description="Snowflake username"
    )
    password: str | None = Field(
        default=os.getenv("SNOWFLAKE_PASSWORD", ""), description="Snowflake password"
    )
    warehouse: str | None = Field(
        default=os.getenv("SNOWFLAKE_WAREHOUSE", ""), description="Snowflake warehouse"
    )
    database: str | None = Field(
        default=os.getenv("SNOWFLAKE_DATABASE", ""), description="Snowflake database"
    )
    role: str | None = Field(
        default=os.getenv("SNOWFLAKE_ROLE", ""), description="Snowflake role"
    )
    schema_name: str | None = Field(
        default=os.getenv("SNOWFLAKE_SCHEMA", ""), description="Snowflake schema"
    )


class UploadDataInput(BaseModel):
    config: SnowflakeConfig = Field(
        description="Snowflake connection configuration", default_factory=SnowflakeConfig
    )
    dataframe: t.Any = Field(
        description="DataFrame or dict representation of DataFrame to upload"
    )
    table_name: str = Field(description="Name of the table to create/update")
    if_exists: t.Literal["fail", "replace", "append"] = Field(
        "replace", description="How to behave if the table already exists"
    )


class TableInfo(BaseModel):
    """Information about a Snowflake table."""

    table_name: str
    database: str | None
    schema_name: str | None
    rows_affected: int


class UploadDataOutput(ToolOutput):
    table_info: TableInfo


class ReadTableInput(BaseModel):
    """Input for reading a table from Snowflake."""

    config: SnowflakeConfig = Field(description="Snowflake connection configuration")
    table_name: str = Field(description="Name of the table to read")
    database: str | None = Field(
        None, description="Database containing the table (defaults to connection config)"
    )
    schema_name: str | None = Field(
        None, description="Schema containing the table (defaults to connection config)"
    )
    limit: int | None = Field(
        None, description="Maximum number of rows to read (None means all rows)"
    )


class ReadTableOutput(ToolOutput):
    table_info: TableInfo
    data: CSVDataResponse


class ExecuteQueryInput(BaseModel):
    """Input for executing a SQL query in Snowflake."""

    config: SnowflakeConfig = Field(description="Snowflake connection configuration")
    query: str = Field(..., description="SQL query to execute")
    page: int = Field(1, description="Page number for paginated results (1-indexed)")
    page_size: int = Field(100, description="Number of rows per page")


class ExecuteQueryOutput(ToolOutput):
    data: CSVDataResponse
