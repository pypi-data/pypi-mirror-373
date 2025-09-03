from pydantic import BaseModel, Field

from . import ToolOutput


class CreateAudioInput(BaseModel):
    conversation: list[tuple[str, str]] = Field(
        default_factory=list,
        description="List of tuples where first element is voice and second is text",
        json_schema_extra={"mandatory": True},
    )
    pause_duration: float = Field(
        default=1.0, description="Duration of pause between conversation turns in seconds"
    )
    voice: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary of voice names and their corresponding OpenAI voice IDs",
    )


class CreateAudioOutput(ToolOutput):
    audio_content: str = Field(default="", description="Base64 encoded audio content")
