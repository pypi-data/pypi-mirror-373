import enum
from typing import Any

from pydantic import BaseModel, Field

from ..models.tools import ToolOutput


class InputMethod(str, enum.Enum):
    console = "console"
    api = "api"


class InputAction(str, enum.Enum):
    text = "text"
    row_selection = "row_selection"
    row_selection_with_feedback = "row_selection_with_feedback"
    chart_config_selection = "chart_config_selection"
    worksheet_document_upload = "worksheet_document_upload"


class HumanFeedbackToolInput(BaseModel):
    input: str = Field(default="")
    tabular_data: list[dict[str, Any]] = Field(default_factory=list)
    chart_config_data: dict[str, Any] | None = None
    input_method: InputMethod = InputMethod.console
    input_action: InputAction = Field(default=InputAction.text)
    input_question: str = Field(default="")
    worksheet_id: int | None = Field(default=None)


class HumanFeedbackToolOutput(ToolOutput):
    content: dict[str, Any] = Field(default_factory=dict)
    input: str = Field(default="")
    tabular_data: dict[str, Any] = Field(default_factory=dict)
    chart_config_data: dict[str, Any] | None = None
    input_action: InputAction = Field(default=InputAction.text)
    input_question: str = Field(default="")
    worksheet_id: int | None = Field(default=None)
