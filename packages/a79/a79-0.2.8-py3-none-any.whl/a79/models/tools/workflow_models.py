import typing as t
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkflowCallbackHandler(BaseModel):
    """Simple callback protocol for workflow events."""

    # TODO: Add callbacks for workflow start, end, node start, end, error
    # if we need them in the external sdk


class RunWorkflowInput(BaseModel):
    """Input data model for workflow runner."""

    workflow_name: str = Field(description="Name of the workflow to run")
    workflow_inputs: dict[str, t.Any] = Field(
        description="Optional input data to pass to the workflow"
    )
    output_vars: list[str] | None = Field(
        default=None,
        description="Optional list of output variables to return from the workflow",
    )
    parent_run_id: str | None = None
    parent_node_id: str | None = None


class RunWorkflowOutput(BaseModel):
    content: dict[str, t.Any] = Field(description="Output of the workflow")


StreamId = t.NewType("StreamId", str)


class ToolStreamResponse(BaseModel):
    stream_id: StreamId
    tool_name: t.Optional[str]
    package_name: t.Optional[str]


class NestedRunIdentifiers(BaseModel):
    """
    Identifies a specific workflow run within a potentially nested workflow hierarchy.

    For root/top-level workflow runs:
    - nested_run_id = str(run_id)  # String version of root run_id
    - parent_node_id = None
    - parent_run_id = None

    For nested workflow runs:
    - nested_run_id = "<uuid>"  # UUID string for nested runs
    - parent_node_id = "<node-id>"  # ID of node that triggered this nested workflow
    - parent_run_id = "<parent-run-id>"  # Parent's run identifier
    """

    # ID for this specific nested workflow run
    nested_run_id: str = Field(default_factory=lambda: str(uuid4()))

    # ID of the node that triggered this nested workflow (None for root runs)
    parent_node_id: str | None = None

    # Run ID of the parent workflow (None for root runs)
    parent_run_id: str | None = None


class RunnableConfig(BaseModel):
    """Configuration class for Runnable objects."""

    # Workflow id is used to identify the workflow definition
    workflow_id: str | None = None

    # Global id unique for the run of the workflow.
    root_run_id: str | None = None

    # Identifies this specific workflow run in the execution hierarchy
    run_identifiers: NestedRunIdentifiers = Field(
        default_factory=lambda: NestedRunIdentifiers()
    )

    artifacts_folder_id: int | None = None
    callbacks: list[WorkflowCallbackHandler] = []
    max_node_workers: int | None = None

    # Conversation ID for the workflow run
    # TODO: Will deprecate this in favor of a run_id. Workflow runs will be independent
    # of conversations. This will be removed in a future PR. Will add support for
    # run_id in a future PR.
    conversation_id: int | None = None

    #### Variables for React Chat Workflow Execution ####
    # These variables are used to identify the workflow run in the React Chat Workflow
    # Execution and stream updates back to the conversation.

    # Session ID for the workflow run
    react_session_id: str | None = None

    # Canvas ID for the workflow run
    react_canvas_id: str | None = None

    # Task ID for the workflow run
    react_task_id: str | None = None

    #### End of React Chat Workflow Execution variables ####

    # Cache invalidation flag - when True, bypasses cached results forces fresh execution
    invalidate_cache: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("root_run_id", mode="before")
    @classmethod
    def convert_root_run_id_to_str(cls, v: Any) -> str | None:
        """Ensure root_run_id is always a string if provided.

        This handles backward compatibility for older runs
        """
        if isinstance(v, int):
            return str(v)
        # Allow None or existing strings
        if v is None or isinstance(v, str):
            return v
        # Raise error for other unexpected types
        raise ValueError("root_run_id must be a string or integer")
