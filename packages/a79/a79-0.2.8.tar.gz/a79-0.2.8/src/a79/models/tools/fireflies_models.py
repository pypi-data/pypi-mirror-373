# This is a generated file by scripts/codegen/composio.py, do not edit manually
# ruff: noqa: E501  # Ignore line length issues in generated files
from typing import Any, Optional

from pydantic import BaseModel, Field


class AddToLiveInput(BaseModel):
    """Input model for FIREFLIES_ADD_TO_LIVE"""

    attendees: Optional[list[Any]] = Field(
        default=None,
        description="""Array of Attendees for expected meeting participants.""",
    )  # noqa: E501

    duration: Optional[int] = Field(
        default=60,
        description="""Meeting duration in minutes. Minimum of 15 and maximum of 120 minutes. Defaults to 60 minutes if param is not provided. Please provide a value of type integer.""",
    )  # noqa: E501

    language: Optional[str] = Field(
        default="English",
        description="""Language of the meeting. Defaults to English if not provided. For a complete list of language codes, please view Language Codes. Please provide a value of type string.""",
    )  # noqa: E501

    meeting_link: str = Field(
        description="""A valid http URL for the meeting link, i.e. Google Meet, Zoom, etc. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    meeting_password: Optional[str] = Field(
        default=None,
        description="""Password for the meeting, if applicable. Please provide a value of type string.""",
    )  # noqa: E501

    title: Optional[str] = Field(
        default=None,
        description="""Title or name of the meeting, this will be used to identify the transcribed file. If title is not provided, a default title will be set automatically. Please provide a value of type string.""",
    )  # noqa: E501


class DeleteTranscriptByIdInput(BaseModel):
    """Input model for FIREFLIES_DELETE_TRANSCRIPT_BY_ID"""

    id: Optional[str] = Field(
        default=None,
        description="""The ID of the transcript to fetch. Please provide a value of type string.""",
    )  # noqa: E501


class FetchAiAppOutputsInput(BaseModel):
    """Input model for FIREFLIES_FETCH_AI_APP_OUTPUTS"""

    app_id: str = Field(
        description="""The app_id parameter retrieves all outputs against a specific AI App. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    limit: Optional[int] = Field(
        default=10,
        description="""Maximum number of apps outputs to fetch in a single query. The default query fetches 10 records, which is the maximum for a single request. Please provide a value of type integer.""",
    )  # noqa: E501

    skip: Optional[int] = Field(
        default=0,
        description="""Number of records to skip over. Helps paginate results when used in combination with the limit param. Please provide a value of type integer.""",
    )  # noqa: E501

    transcript_id: str = Field(
        description="""The transcript_id parameter retrieves all outputs against a specific meeting/transcript. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class GetBitesInput(BaseModel):
    """Input model for FIREFLIES_GET_BITES"""

    limit: Optional[int] = Field(
        default=None,
        description="""Maximum number of bites to fetch. Please provide a value of type integer.""",
    )  # noqa: E501

    mine: Optional[bool] = Field(
        default=None,
        description="""Filter to include only the user's own bites. Please provide a value of type boolean.""",
    )  # noqa: E501

    my_team: Optional[bool] = Field(
        default=None,
        description="""Filter to include bites from the user's team. Please provide a value of type boolean.""",
    )  # noqa: E501

    skip: Optional[int] = Field(
        default=None,
        description="""Number of bites to skip. Please provide a value of type integer.""",
    )  # noqa: E501

    transcript_id: Optional[str] = Field(
        default=None,
        description="""The ID of the transcript to fetch bites for. Please provide a value of type string.""",
    )  # noqa: E501


class GetBiteByIdInput(BaseModel):
    """Input model for FIREFLIES_GET_BITE_BY_ID"""

    id: Optional[str] = Field(
        default=None,
        description="""The ID of the bite to fetch. Please provide a value of type string.""",
    )  # noqa: E501


class GetTranscriptsInput(BaseModel):
    """Input model for FIREFLIES_GET_TRANSCRIPTS"""

    from_date: Optional[str] = Field(
        default=None,
        description="""Start date for filtering transcripts. Please provide a value of type string.""",
    )  # noqa: E501

    host_email: Optional[str] = Field(
        default=None,
        description="""Email of the host of the meeting. Please provide a value of type string.""",
    )  # noqa: E501

    limit: Optional[int] = Field(
        default=None,
        description="""Maximum number of transcripts to fetch. Please provide a value of type integer.""",
    )  # noqa: E501

    organizer_email: Optional[str] = Field(
        default=None,
        description="""Email of the organizer of the meeting. Please provide a value of type string.""",
    )  # noqa: E501

    participant_email: Optional[str] = Field(
        default=None,
        description="""Email of a participant in the meeting. Please provide a value of type string.""",
    )  # noqa: E501

    skip: Optional[int] = Field(
        default=None,
        description="""Number of transcripts to skip. Please provide a value of type integer.""",
    )  # noqa: E501

    title: Optional[str] = Field(
        default=None,
        description="""Title of the meeting. Please provide a value of type string.""",
    )  # noqa: E501

    to_date: Optional[str] = Field(
        default=None,
        description="""End date for filtering transcripts. Please provide a value of type string.""",
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default=None,
        description="""The User ID to fetch the transcripts of. Please provide a value of type string.""",
    )  # noqa: E501


class GetTranscriptByIdInput(BaseModel):
    """Input model for FIREFLIES_GET_TRANSCRIPT_BY_ID"""

    id: str = Field(
        description="""The ID of the transcript to fetch. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class GetUsersInput(BaseModel):
    """Input model for FIREFLIES_GET_USERS"""

    pass


class GetUserByIdInput(BaseModel):
    """Input model for FIREFLIES_GET_USER_BY_ID"""

    id: str = Field(
        description="""The User ID to the details of. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class UploadAudioInput(BaseModel):
    """Input model for FIREFLIES_UPLOAD_AUDIO"""

    attendees: Optional[list[Any]] = Field(
        default=None,
        description="""An array of objects containing Attendee objects. This is relevant if you have active integrations like Salesforce, Hubspot etc. Fireflies uses the attendees value to push meeting notes to your active CRM integrations where notes are added to an existing contact or a new contact is created. Each object contains - displayName, email, phoneNumber, client_reference_id""",
    )  # noqa: E501

    client_reference_id: Optional[str] = Field(
        default=None,
        description="""The client reference id of the attendee. Please provide a value of type string.""",
    )  # noqa: E501

    custom_language: Optional[str] = Field(
        default=None,
        description="""Specify a custom language code for your meeting, e.g. es for Spanish or de for German. For a complete list of language codes, please view Language Codes. Please provide a value of type string.""",
    )  # noqa: E501

    save_video: Optional[bool] = Field(
        default=False,
        description="""Specify whether the video should be saved or not. Please provide a value of type boolean.""",
    )  # noqa: E501

    title: str = Field(
        description="""Title or name of the meeting, this will be used to identify the transcribed file. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    url: str = Field(
        description="""The url of media file to be transcribed. It MUST be a valid https string and publicly accessible to enable us download the audio / video file. Double check to see if the media file is downloadable and that the link is not a preview link before making the request. The media file must be either of these formats - mp3, mp4, wav, m4a, ogg. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    webhook: Optional[str] = Field(
        default=None,
        description="""URL for the webhook that receives notifications when transcription completes. Please provide a value of type string.""",
    )  # noqa: E501
