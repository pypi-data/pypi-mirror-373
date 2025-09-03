import typing as t

from pydantic import BaseModel, Field

from .. import enums
from . import ToolOutput


class PodcastSection(BaseModel):
    """Model for a section of the podcast."""

    title: str
    key_points: list[str]
    estimated_turns: int


class CreatePodcastInput(BaseModel):
    model: str = Field(
        default=enums.ModelName.GPT_4O,
        description="The model to use for the podcast creation",
    )
    user_1_profile: str = Field(
        default="", description="Profile/description of the first speaker"
    )
    user_2_profile: str = Field(
        default="", description="Profile/description of the second speaker"
    )
    content: str = Field(
        default="", description="The content to be discussed in the podcast"
    )


class CreatePodcastOutput(ToolOutput):
    result: dict[str, t.Any]
