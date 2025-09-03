import typing as t

from pydantic import BaseModel, Field

from . import ToolOutput


class ChatMessage(BaseModel):
    """Message in a chat completion request/response."""

    content: str
    role: t.Literal["system", "user", "assistant"]


class ChatOptions(BaseModel):
    """Options for configuring Perplexity chat behavior."""

    model: str = "sonar"
    system_message: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    stream: bool = False

    # New parameters added
    search_domain_filter: list[str] | None = None
    search_recency_filter: str | None = None

    # Dict for additional keyword arguments
    additional_options: dict[str, t.Any] = Field(default_factory=dict)


class ChatInput(BaseModel):
    input: str | list[dict[str, t.Any]] | t.Any = Field(
        default="", json_schema_extra={"mandatory": True}
    )
    chat_options: ChatOptions = Field(
        default_factory=ChatOptions, description="The options for chat configuration"
    )
    timeout: int = Field(default=600)


class ChatOutput(ToolOutput):
    content: dict[str, t.Any] = Field(
        default_factory=dict, description="The content of the chat completion"
    )
