from pydantic import BaseModel, Field

from .. import enums
from . import ToolOutput


class ReactAgentInput(BaseModel):
    """Input model for the React agent tool."""

    task: str = Field(
        description="The task or question to be solved by the React agent",
        json_schema_extra={"mandatory": True},
    )
    max_iterations: int = Field(
        default=15, description="Maximum number of iterations before giving up"
    )
    context: str = Field(default="", description="Additional context for the React agent")
    available_tools: str = Field(
        default="",
        description="Available tools for the agent to use and their definitions",
    )
    model_name: str = Field(
        default=enums.ModelName.GPT_4O,
        description="The LLM model to use for the React agent",
    )
    system_message: str = Field(
        default="You are a Python coding assistant that solves problems step by step"
        " using code.",
        description="System message for the LLM",
    )
    num_examples: int = Field(
        default=2, description="Number of k-shot examples to include"
    )


class ReactAgentOutput(ToolOutput):
    """Output model for the React agent tool."""

    answer: str = Field(description="The final answer from the React agent")
    success: bool = Field(description="Whether the agent completed successfully")
    reasoning_trace: list[str] | None = Field(
        default=None, description="The full reasoning trace if requested"
    )
