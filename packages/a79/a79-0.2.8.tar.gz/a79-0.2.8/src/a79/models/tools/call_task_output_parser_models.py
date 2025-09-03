from typing import Any

from pydantic import BaseModel, Field

from . import ToolOutput


class CallTaskOutputParserInput(BaseModel):
    """Input model for the call task output parser tool."""

    transcript: str = Field(
        json_schema_extra={"mandatory": True},
        description="The call transcript to parse",
        default="",
    )
    output_schema: dict[str, Any] = Field(
        json_schema_extra={"mandatory": True},
        description="The JSON schema that defines the expected output structure",
        default={},
    )


class CallTaskOutputParserOutput(ToolOutput):
    """Output model for the call task output parser tool."""

    parsed_output: dict[str, Any] = Field(
        json_schema_extra={"mandatory": True},
        description="The extracted data from the transcript in the output schema. ",
        default={},
    )
