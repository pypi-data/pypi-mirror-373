from pydantic import BaseModel, Field

from . import ToolOutput

TEXT_RESEARCH_USECASE = "text-research"


class CreateProjectInput(BaseModel):
    name: str = Field(default="Workflow generated project")
    description: str = Field(default="")
    datasource_ids: list[int] = Field(default=[])
    worksheet_id: int | None = Field(default=None, json_schema_extra={"mandatory": True})
    use_case: str = Field(default=TEXT_RESEARCH_USECASE)


class CreateProjectOutput(ToolOutput):
    project_id: int = Field()
