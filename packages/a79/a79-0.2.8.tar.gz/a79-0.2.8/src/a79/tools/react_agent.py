# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.react_agent_models import ReactAgentInput, ReactAgentOutput

__all__ = ["ReactAgentInput", "ReactAgentOutput", "react_agent"]


def react_agent(
    *,
    task: str,
    max_iterations: int = DEFAULT,
    context: str = DEFAULT,
    available_tools: str = DEFAULT,
    model_name: str = DEFAULT,
    system_message: str = DEFAULT,
    num_examples: int = DEFAULT,
) -> ReactAgentOutput:
    """
    Execute a React agent to solve a task using code and tool execution.

    This tool utilizes the PythonReActAgent to solve tasks by thinking, running code,
    observing results, and iterating until it finds an answer.
    This is used when you want to put a react tool within a node
    if you want to just create the workflow with react there is a different way to do it
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ReactAgentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="react_agent", name="react_agent", input=input_model.model_dump()
    )
    return ReactAgentOutput.model_validate(output_model)
