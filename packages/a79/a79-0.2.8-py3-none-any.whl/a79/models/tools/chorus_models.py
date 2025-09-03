"""Pydantic models for Chorus API integration."""

import typing as t
from enum import Enum

from pydantic import BaseModel, Field

from . import ToolSummary


class ChorusEngagementType(str, Enum):
    """Engagement types in Chorus."""

    MEETING = "meeting"
    EMAIL = "email"
    CONTENT_VIEWED = "content_viewed"


class EngagementType(str, Enum):
    """Internal engagement types for processing."""

    MEETING = "meeting"
    EMAIL = "email"
    CONTENT_VIEWED = "content_viewed"

    @classmethod
    def from_string(cls, value: str) -> "EngagementType":
        """Convert string value to EngagementType enum.

        Args:
            value: String representation of engagement type

        Returns:
            EngagementType enum value

        Raises:
            ValueError: If value is not a valid engagement type
        """
        if not value:
            return cls.MEETING  # Default to meeting for empty/None values

        normalized_value = value.lower().strip()

        for engagement_type in cls:
            if engagement_type.value == normalized_value:
                return engagement_type

        # Fallback to MEETING for unknown types to maintain compatibility
        return cls.MEETING


# Base response models
class ChorusError(BaseModel):
    """Error response model from Chorus API."""

    code: str
    detail: str
    id: str
    source: dict[str, str] = Field(default_factory=dict)
    status: str
    title: str


class ChorusErrorResponse(BaseModel):
    """Error response wrapper."""

    errors: list[ChorusError]


class ChorusUsersResponse(BaseModel):
    """Multiple users response."""

    data: list[dict[str, t.Any]]


# Input/Output models
class GetConversationsInput(BaseModel):
    """Input for getting multiple conversations."""

    compliance: t.Optional[str] = Field(
        None, description="Call recording compliance flag"
    )
    continuation_key: t.Optional[str] = Field(
        None, description="Continuation key for pagination"
    )
    disposition_connected: t.Optional[bool] = Field(
        None, description="Chorus disposition - connected"
    )
    disposition_gatekeeper: t.Optional[bool] = Field(
        None, description="Chorus disposition - gatekeeper"
    )
    disposition_tree: t.Optional[bool] = Field(
        None, description="Chorus disposition - phone tree"
    )
    disposition_voicemail: t.Optional[bool] = Field(
        None, description="Chorus disposition - voicemail"
    )
    engagement_id: t.Optional[str] = Field(
        None, description="Comma-separated list of engagement ids"
    )
    engagement_type: t.Optional[ChorusEngagementType] = Field(
        None, description="Type of engagement"
    )
    max_date: t.Optional[str] = Field(
        None, description="Max date of engagement (format: YYYY-MM-DDTHH:MM:SSZ)"
    )
    max_duration: t.Optional[float] = Field(
        None, description="Max duration of meeting (in seconds)"
    )
    min_date: t.Optional[str] = Field(
        None, description="Min date of engagement (format: YYYY-MM-DDTHH:MM:SSZ)"
    )
    min_duration: t.Optional[float] = Field(
        None, description="Min duration of meeting (in seconds)"
    )
    participants_email: t.Optional[str] = Field(
        None, description="The email address of a participant"
    )
    team_id: t.Optional[str] = Field(
        None, description="Comma-separated list of Team ID(s) for engagement owner"
    )
    user_id: t.Optional[str] = Field(
        None, description="Comma-separated list of User ID(s) for engagement owner"
    )
    with_trackers: t.Optional[bool] = Field(
        None, description="Return tracker information with results"
    )


class GetConversationsOutput(BaseModel):
    """Output for getting conversations."""

    conversations: list[dict[str, t.Any]]
    total_count: t.Optional[int] = None
    continuation_key: t.Optional[str] = None
    tool_summary: ToolSummary


class GetUsersInput(BaseModel):
    """Input for getting users."""

    page_size: int = Field(20, description="Number of results per page")
    page_number: int = Field(1, description="Page number to fetch")


class GetUsersOutput(BaseModel):
    """Output for getting users."""

    users: ChorusUsersResponse
    total_count: t.Optional[int] = None
    tool_summary: ToolSummary


class GetMomentsInput(BaseModel):
    """Input for getting moments."""

    shared_on: t.Optional[str] = Field(None, description="Filter by shared on date")


class GetMomentsOutput(BaseModel):
    """Output for getting moments."""

    moments: list[dict[str, t.Any]]
    total_count: t.Optional[int] = None
    tool_summary: ToolSummary


class GetEmailInput(BaseModel):
    """Input for getting an email."""

    id: str = Field(description="The email ID to retrieve")


class GetEmailOutput(BaseModel):
    """Output for getting an email."""

    email_data: dict[str, t.Any]
    tool_summary: ToolSummary


class GetMeetingsInput(BaseModel):
    """Input for getting meetings with enhanced data."""

    user_name: t.Optional[str] = Field(
        None, description="Name of the user to filter meetings by"
    )
    company_name: t.Optional[str] = Field(
        None, description="Company name to filter meetings by"
    )
    start_date: t.Optional[str] = Field(
        None,
        description="Start date for date range (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)",
    )
    end_date: t.Optional[str] = Field(
        None,
        description="End date for date range (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)",
    )


class MeetingData(BaseModel):
    """Enhanced meeting data with transcripts and emails."""

    engagement_id: str
    email_content: t.Optional[t.Any] = None
    audio_transcription_of_meeting: t.Optional[str] = None
    meeting_summary: t.Optional[str] = None
    date_time: str
    participants_info: list[dict[str, t.Any]]
    engagement_type: EngagementType
    thread_id: t.Optional[str] = None


class GetMeetingsOutput(BaseModel):
    """Output for getting meetings with enhanced data."""

    meetings: dict[str, MeetingData]
    total_count: int
    tool_summary: ToolSummary
