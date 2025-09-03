from typing import Any

from pydantic import BaseModel, Field

from . import ToolOutput


class CallTaskDefinition(BaseModel):
    """Definition of a task for voice calls"""

    task_name: str
    instructions: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class CallTaskGeneratorInput(BaseModel):
    task_name: str = Field(
        json_schema_extra={"mandatory": True},
        description="The name of the task to generate a call script for",
        default="",
    )
    current_instructions: str = Field(
        json_schema_extra={"mandatory": True},
        description="The current instructions for the call task",
        default="",
    )
    current_call_task_definition: CallTaskDefinition | None = Field(
        json_schema_extra={"mandatory": True},
        description="The current definition of the call task",
        default=None,
    )
    new_instructions: str = Field(
        json_schema_extra={"mandatory": True},
        description="The new instructions on how to improve the call task definition",
        default="",
    )


class CallTaskGeneratorOutput(ToolOutput):
    task_name: str = Field(
        json_schema_extra={"mandatory": True},
        description="The name of the task to generate a call script for",
        default="",
    )
    call_task_definition: CallTaskDefinition | None = Field(
        json_schema_extra={"mandatory": True},
        description="The call task definition",
        default=None,
    )
