import typing as t
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pydantic.json_schema import SkipJsonSchema

from .. import enums
from . import ToolOutput


class ErrorHandling(BaseModel):
    """
    Configuration for error handling in nodes.

    Attributes:
        timeout_seconds (float | None): Timeout in seconds for node execution.
        retry_interval_seconds (float): Interval between retries in seconds.
        max_retries (int): Maximum number of retries.
        backoff_rate (float): Rate of increase for retry intervals.
    """

    timeout_seconds: float | None = (
        900  # 15 minutes because sub-workflows can be run in the python node
    )
    retry_interval_seconds: float = 1
    max_retries: int = 0
    backoff_rate: float = 1


class InferenceMode(str, Enum):
    """
    Enumeration of inference types.
    """

    DEFAULT = "DEFAULT"
    XML = "XML"
    FUNCTION_CALLING = "FUNCTION_CALLING"
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"


class LLMUsageData(BaseModel):
    prompt_tokens: int
    prompt_tokens_cost_usd: float | None
    completion_tokens: int
    completion_tokens_cost_usd: float | None
    total_tokens: int
    total_tokens_cost_usd: float | None


class ChatInput(BaseModel):
    MODEL_PREFIX: t.ClassVar[str | None] = None

    schema: dict[str, t.Any] | type[BaseModel] | None = None  # type: ignore
    model: str = enums.ModelName.GPT_4O_MINI
    prompt_str: str | None = None
    file_data: str | None = None
    file_name: str | None = None
    temperature: float = 0.1
    stop: list[str] | None = None
    error_handling: ErrorHandling = ErrorHandling(timeout_seconds=600)
    top_p: float | None = None
    seed: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    tool_choice: str | None = None
    inference_mode: InferenceMode = InferenceMode.DEFAULT
    output_schema: dict[str, t.Any] | type[BaseModel] | None = Field(
        default=None, description="Schema for structured output or function calling."
    )
    stream: bool = Field(default=False, description="Enable streaming response")

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    @field_serializer("output_schema")
    def serialize_schema(self, value: t.Any | None, _info) -> dict[str, t.Any] | None:  # type: ignore
        if value is None:
            return None  # type: ignore
        elif isinstance(value, type) and issubclass(value, BaseModel):
            return value.model_json_schema()
        else:
            return value  # type: ignore

    @field_validator("model")
    @classmethod
    def set_model(cls, value: str | None) -> str:
        """Set the model with the appropriate prefix.

        Args:
            value (str | None): The model value.

        Returns:
            str: The model value with the prefix.
        """
        if cls.MODEL_PREFIX is not None and not value.startswith(cls.MODEL_PREFIX):  # type: ignore
            value = f"{cls.MODEL_PREFIX}{value}"
        return value  # type: ignore


class ChatOutput(ToolOutput):
    llm_call: SkipJsonSchema[dict[str, t.Any]] = Field(default_factory=dict)
    content: str | None = Field(default="")
    schema_result_json: dict[str, t.Any] | None = Field(default=None)
    tool_calls: SkipJsonSchema[list[dict[str, t.Any]] | None] = Field(default=None)
