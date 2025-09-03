# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.perplexity_models import (
    ChatInput,
    ChatMessage,
    ChatOptions,
    ChatOutput,
)

__all__ = ["ChatInput", "ChatMessage", "ChatOptions", "ChatOutput", "chat"]


def chat(
    *,
    input: str | list[dict[str, Any]] | Any = DEFAULT,
    chat_options: ChatOptions = DEFAULT,
    timeout: int = DEFAULT,
) -> ChatOutput:
    """
    A tool for generating chat completions using Perplexity AI's API.

    Input should be a valid ChatInput.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ChatInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="perplexity", name="chat", input=input_model.model_dump()
    )
    return ChatOutput.model_validate(output_model)
