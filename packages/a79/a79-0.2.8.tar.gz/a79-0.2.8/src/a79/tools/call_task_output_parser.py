# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.call_task_output_parser_models import (
    CallTaskOutputParserInput,
    CallTaskOutputParserOutput,
)

__all__ = [
    "CallTaskOutputParserInput",
    "CallTaskOutputParserOutput",
    "parse_call_task_output",
]


def parse_call_task_output(
    *, transcript: str = DEFAULT, output_schema: dict[str, Any] = DEFAULT
) -> CallTaskOutputParserOutput:
    """
    Parse a call transcript using LLM to extract structured output according to a schema.

    This tool analyzes call transcripts and extracts information that matches the
    provided output schema, which is typically from a CallTaskDefinition.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CallTaskOutputParserInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="call_task_output_parser",
        name="parse_call_task_output",
        input=input_model.model_dump(),
    )
    return CallTaskOutputParserOutput.model_validate(output_model)
