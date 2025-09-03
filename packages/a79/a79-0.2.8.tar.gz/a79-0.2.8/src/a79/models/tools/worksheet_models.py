import typing as t

from pydantic import BaseModel, Field

from .. import core
from . import ToolOutput


class ReadWorksheetInput(BaseModel):
    worksheet_id: str = Field(
        default="", json_schema_extra={"mandatory": True, "field_type": "worksheet"}
    )
    tabular_filter_json: str = Field(default="")
    column_list: list[str] = Field(default=[])
    page_size: int = Field(default=50)


class ReadWorksheetOutput(ToolOutput):
    worksheet_data: core.CSVDataResponse | None = Field(default=None)


class CreateWorksheetInput(BaseModel):
    name: str = Field(default="Workflow generated worksheet")
    description: str = Field(default="")
    datasource_ids: list[int] = Field(
        default_factory=list, json_schema_extra={"mandatory": True}
    )


class CreateWorksheetOutput(ToolOutput):
    worksheet_id: int = Field()


class CreateEnrichmentInput(BaseModel):
    name: str = Field(default="Workflow generated worksheet enrichment")
    description: str = Field(default="")
    worksheet_id: int = Field(default=0)
    function_type: str | None = Field(default=None)
    function_data: dict[str, t.Any] = Field(default_factory=dict)
    column_mapping: list[dict[str, t.Any]] = Field(default_factory=lambda: [])
    new_column_name: str | None = Field(default=None)
    # enrichment_fn_create: ws_model.EnrichmentFunctionCreate = Field(
    #    default_factory=ws_model.EnrichmentFunctionCreate
    # )


class CreateEnrichmentOutput(ToolOutput):
    worksheet_id: int = Field()
