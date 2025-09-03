from typing import Any

from pydantic import BaseModel, Field

from . import ToolOutput


class RunTasksInParallelInput(BaseModel):
    """Input for running tasks in parallel."""

    func_to_run: Any = Field(description="The function to execute in parallel")
    items_to_process: list[Any] = Field(
        description="List of items to process in parallel"
    )
    shared_args: list[Any] = Field(
        description="Additional arguments to pass to each function call"
    )
    max_workers: int = Field(default=5, description="Maximum number of workers to use")


class RunTasksInParallelOutput(ToolOutput):
    """Output from running tasks in parallel."""

    results: list[Any] = Field(description="List of results from parallel execution")
