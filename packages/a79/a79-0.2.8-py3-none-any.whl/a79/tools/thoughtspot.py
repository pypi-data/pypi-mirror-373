# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.thoughtspot_models import (
    ConnectionDetails,
    ConnectionResponse,
    CreateConnectionInput,
    CreateConnectionOutput,
    CreateLiveboardInput,
    CreateLiveboardOutput,
    PinAnswerInput,
    PinAnswerOutput,
    SearchDataInput,
    SearchDataOutput,
    SearchDataResponse,
    SearchMetadataInput,
    SearchMetadataOutput,
    TableInfo,
)

__all__ = [
    "ConnectionDetails",
    "ConnectionResponse",
    "CreateConnectionInput",
    "CreateConnectionOutput",
    "CreateLiveboardInput",
    "CreateLiveboardOutput",
    "PinAnswerInput",
    "PinAnswerOutput",
    "SearchDataInput",
    "SearchDataOutput",
    "SearchDataResponse",
    "SearchMetadataInput",
    "SearchMetadataOutput",
    "TableInfo",
    "create_connection",
    "create_liveboard",
    "pin_answer",
    "search_metadata",
    "search_data",
]


def create_connection(
    *,
    data_store_connector_id: str | None = DEFAULT,
    data_store_connector_name: str | None = DEFAULT,
    data_store_config: dict[str, Any] = DEFAULT,
) -> CreateConnectionOutput:
    """
    "Creates a connection to a data source in Thoughtspot."
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateConnectionInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="thoughtspot", name="create_connection", input=input_model.model_dump()
    )
    return CreateConnectionOutput.model_validate(output_model)


def create_liveboard(
    *, liveboard_name: str, liveboard_description: str | None = DEFAULT
) -> CreateLiveboardOutput:
    """
    Creates a new liveboard in Thoughtspot to host visualizations.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateLiveboardInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="thoughtspot", name="create_liveboard", input=input_model.model_dump()
    )
    return CreateLiveboardOutput.model_validate(output_model)


def pin_answer(
    *,
    table_id: str,
    answer_name: str,
    liveboard_id: str,
    chart_type: str,
    answer_data: SearchDataResponse,
) -> PinAnswerOutput:
    """
    "Pins an answer to a liveboard in Thoughtspot.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = PinAnswerInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="thoughtspot", name="pin_answer", input=input_model.model_dump()
    )
    return PinAnswerOutput.model_validate(output_model)


def search_metadata(*, query: str) -> SearchMetadataOutput:
    """
    Searches metadata in Thoughtspot.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchMetadataInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="thoughtspot", name="search_metadata", input=input_model.model_dump()
    )
    return SearchMetadataOutput.model_validate(output_model)


def search_data(*, query: str, logical_table_identifier: str) -> SearchDataOutput:
    """
    Searches data in Thoughtspot.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchDataInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="thoughtspot", name="search_data", input=input_model.model_dump()
    )
    return SearchDataOutput.model_validate(output_model)
