import typing as t

from pydantic import BaseModel, Field

from . import ToolOutput


class TableInfo(BaseModel):
    """Table information in a Snowflake connection."""

    name: str
    type: str
    id: str
    schemaStripe: str
    databaseStripe: str


class ConnectionDetails(BaseModel):
    """Detailed information about a Snowflake connection."""

    name: str
    type: str
    id: str
    scheduled: bool
    connectionType: str
    configuration: str
    tables: list[TableInfo] = []


class ConnectionResponse(BaseModel):
    """Response model for Snowflake connection creation."""

    id: str
    name: str
    data_warehouse_type: str
    details: ConnectionDetails


class SearchDataResponse(BaseModel):
    """Response model for the search_data API."""

    column_names: list[str]
    available_data_row_count: int


class CreateConnectionInput(BaseModel):
    """Configuration for creating a connection to a data source."""

    data_store_connector_id: str | None = None
    data_store_connector_name: str | None = Field(
        None,  # if None, we will use the name of the Connector from ID.
        description="Name of the connector whose payload will be used to create a "
        "Thoughtspot connection (e.g., Snowflake)",
    )
    data_store_config: dict[str, t.Any] = Field(default_factory=dict)


class CreateConnectionOutput(ToolOutput):
    connection: ConnectionResponse


class CreateLiveboardInput(BaseModel):
    """Configuration for creating a Thoughtspot liveboard."""

    liveboard_name: str = Field(description="Name of the liveboard to create")
    liveboard_description: str | None = Field(
        None, description="Description of the liveboard to create"
    )


class CreateLiveboardOutput(ToolOutput):
    liveboard_id: str


class PinAnswerInput(BaseModel):
    """Configuration for pinning an answer to a liveboard."""

    table_id: str = Field(description="ID of the table to pin an answer to")
    answer_name: str = Field(description="Name of the answer to pin")
    liveboard_id: str = Field(description="ID of the liveboard to pin to")
    chart_type: str = Field(description="Type of chart to use for the answer")
    answer_data: SearchDataResponse = Field(description="Data for the answer")


class PinAnswerOutput(ToolOutput):
    liveboard_id: str = Field(description="ID of the liveboard to pin an answer to")


class SearchMetadataInput(BaseModel):
    """Configuration for searching metadata in Thoughtspot."""

    query: str = Field(description="Query to search for")


class SearchMetadataOutput(ToolOutput):
    result: list[dict[str, t.Any]]


class SearchDataInput(BaseModel):
    """Configuration for searching data in Thoughtspot."""

    query: str = Field(description="Query to search for")
    logical_table_identifier: str = Field(
        description="Logical table identifier to search for"
    )


class SearchDataOutput(ToolOutput):
    result: SearchDataResponse
