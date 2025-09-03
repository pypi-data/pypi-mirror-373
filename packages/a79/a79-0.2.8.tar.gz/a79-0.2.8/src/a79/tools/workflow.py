# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.workflow_models import (
    NestedRunIdentifiers,
    RunnableConfig,
    RunWorkflowInput,
    RunWorkflowOutput,
    ToolStreamResponse,
    WorkflowCallbackHandler,
)

__all__ = [
    "NestedRunIdentifiers",
    "RunWorkflowInput",
    "RunWorkflowOutput",
    "RunnableConfig",
    "ToolStreamResponse",
    "WorkflowCallbackHandler",
    "run_workflow",
]


def run_workflow(
    *,
    workflow_name: str,
    workflow_inputs: dict[str, Any],
    output_vars: list[str] | None = DEFAULT,
    parent_run_id: str | None = DEFAULT,
    parent_node_id: str | None = DEFAULT,
) -> RunWorkflowOutput:
    """
    Run a workflow and wait for completion.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RunWorkflowInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="workflow", name="run_workflow", input=input_model.model_dump()
    )
    return RunWorkflowOutput.model_validate(output_model)
