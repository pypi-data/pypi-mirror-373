# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.chorus_models import (
    ChorusEngagementType,
    ChorusError,
    ChorusErrorResponse,
    ChorusUsersResponse,
    EngagementType,
    Enum,
    GetConversationsInput,
    GetConversationsOutput,
    GetEmailInput,
    GetEmailOutput,
    GetMeetingsInput,
    GetMeetingsOutput,
    GetMomentsInput,
    GetMomentsOutput,
    GetUsersInput,
    GetUsersOutput,
    MeetingData,
)

__all__ = [
    "ChorusEngagementType",
    "ChorusError",
    "ChorusErrorResponse",
    "ChorusUsersResponse",
    "EngagementType",
    "Enum",
    "GetConversationsInput",
    "GetConversationsOutput",
    "GetEmailInput",
    "GetEmailOutput",
    "GetMeetingsInput",
    "GetMeetingsOutput",
    "GetMomentsInput",
    "GetMomentsOutput",
    "GetUsersInput",
    "GetUsersOutput",
    "MeetingData",
    "get_conversations",
    "get_moments",
    "get_email",
    "get_users",
    "get_meetings",
]


def get_conversations(
    *,
    compliance: str | None = DEFAULT,
    continuation_key: str | None = DEFAULT,
    disposition_connected: bool | None = DEFAULT,
    disposition_gatekeeper: bool | None = DEFAULT,
    disposition_tree: bool | None = DEFAULT,
    disposition_voicemail: bool | None = DEFAULT,
    engagement_id: str | None = DEFAULT,
    engagement_type: ChorusEngagementType | None = DEFAULT,
    max_date: str | None = DEFAULT,
    max_duration: float | None = DEFAULT,
    min_date: str | None = DEFAULT,
    min_duration: float | None = DEFAULT,
    participants_email: str | None = DEFAULT,
    team_id: str | None = DEFAULT,
    user_id: str | None = DEFAULT,
    with_trackers: bool | None = DEFAULT,
) -> GetConversationsOutput:
    """
    Retrieve multiple conversations with filtering options.

    Supports filtering by date range, participant email, engagement type,
    disposition filters, and other criteria.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetConversationsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="chorus", name="get_conversations", input=input_model.model_dump()
    )
    return GetConversationsOutput.model_validate(output_model)


def get_moments(*, shared_on: str | None = DEFAULT) -> GetMomentsOutput:
    """
    Fetch moments with filtering options.

    Retrieve conversation moments (key highlights) based on conversation,
    type, date range, owner, and tags.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetMomentsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="chorus", name="get_moments", input=input_model.model_dump()
    )
    return GetMomentsOutput.model_validate(output_model)


def get_email(*, id: str) -> GetEmailOutput:
    """
    Retrieve a specific email by ID.

    Returns detailed email information including body, participants,
    deal information, and associated metadata.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetEmailInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="chorus", name="get_email", input=input_model.model_dump()
    )
    return GetEmailOutput.model_validate(output_model)


def get_users(*, page_size: int = DEFAULT, page_number: int = DEFAULT) -> GetUsersOutput:
    """
    Retrieve all users in the Chorus organization.

    Returns paginated list of users with their profile information
    and team associations.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetUsersInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="chorus", name="get_users", input=input_model.model_dump()
    )
    return GetUsersOutput.model_validate(output_model)


def get_meetings(
    *,
    user_name: str | None = DEFAULT,
    company_name: str | None = DEFAULT,
    start_date: str | None = DEFAULT,
    end_date: str | None = DEFAULT,
) -> GetMeetingsOutput:
    """
    Get meetings with enhanced data including audio transcripts and email content.

    Retrieves conversations, processes meeting audio to extract transcripts,
    and fetches email content for comprehensive meeting analysis.

    Args:
        input: GetMeetingsInput with filtering parameters

    Returns:
        GetMeetingsOutput with structured meeting data including transcripts

    Raises:
        ValueError: If neither user_name nor company_name is provided
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetMeetingsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="chorus", name="get_meetings", input=input_model.model_dump()
    )
    return GetMeetingsOutput.model_validate(output_model)
