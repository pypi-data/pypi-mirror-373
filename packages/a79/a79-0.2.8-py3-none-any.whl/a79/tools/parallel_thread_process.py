# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.parallel_thread_process_models import (
    RunTasksInParallelInput,
    RunTasksInParallelOutput,
)

__all__ = ["RunTasksInParallelInput", "RunTasksInParallelOutput", "run_tasks_in_parallel"]


def run_tasks_in_parallel(
    *,
    func_to_run: Any,
    items_to_process: list[Any],
    shared_args: list[Any],
    max_workers: int = DEFAULT,
) -> RunTasksInParallelOutput:
    """Run tasks in parallel.

    Args:
        input: RunTasksInParallelInput containing:
            - func_to_run: The function to execute
            - items_to_process: List of items to process
            - shared_args: Additional arguments to pass to each function call
            - max_workers: Maximum number of parallel workers (default: 5)

    Returns:
        RunTasksInParallelOutput containing the list of results
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RunTasksInParallelInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="parallel_thread_process",
        name="run_tasks_in_parallel",
        input=input_model.model_dump(),
    )
    return RunTasksInParallelOutput.model_validate(output_model)
