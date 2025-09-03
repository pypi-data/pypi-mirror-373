# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.call_task_generator_models import (
    CallTaskDefinition,
    CallTaskGeneratorInput,
    CallTaskGeneratorOutput,
)

__all__ = [
    "CallTaskDefinition",
    "CallTaskGeneratorInput",
    "CallTaskGeneratorOutput",
    "generate_call_task",
]


def generate_call_task(
    *,
    task_name: str = DEFAULT,
    current_instructions: str = DEFAULT,
    current_call_task_definition: CallTaskDefinition | None = DEFAULT,
    new_instructions: str = DEFAULT,
) -> CallTaskGeneratorOutput:
    """
    Generate a call task using LLM to create or update a phone call task definition.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CallTaskGeneratorInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="call_task_generator",
        name="generate_call_task",
        input=input_model.model_dump(),
    )
    return CallTaskGeneratorOutput.model_validate(output_model)
