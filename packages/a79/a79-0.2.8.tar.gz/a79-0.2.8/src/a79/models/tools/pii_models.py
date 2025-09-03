from pydantic import BaseModel, Field

from . import ToolOutput


class RedactInput(BaseModel):
    text: str = Field(
        json_schema_extra={"mandatory": True},
        description="The original text to redact PII from",
        default="",
    )


class RedactOutput(ToolOutput):
    redacted_text: str = Field(
        description="The text with PII information redacted",
        json_schema_extra={"mandatory": True},
        default="",
    )
