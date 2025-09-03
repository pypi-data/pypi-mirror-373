# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.composio_models import ComposioResult
from ..models.tools.fireflies_models import (
    AddToLiveInput,
    DeleteTranscriptByIdInput,
    FetchAiAppOutputsInput,
    GetBiteByIdInput,
    GetBitesInput,
    GetTranscriptByIdInput,
    GetTranscriptsInput,
    GetUserByIdInput,
    GetUsersInput,
    UploadAudioInput,
)

__all__ = [
    "AddToLiveInput",
    "DeleteTranscriptByIdInput",
    "FetchAiAppOutputsInput",
    "GetBiteByIdInput",
    "GetBitesInput",
    "GetTranscriptByIdInput",
    "GetTranscriptsInput",
    "GetUserByIdInput",
    "GetUsersInput",
    "UploadAudioInput",
    "add_to_live",
    "delete_transcript_by_id",
    "fetch_ai_app_outputs",
    "get_bites",
    "get_bite_by_id",
    "get_transcripts",
    "get_transcript_by_id",
    "get_users",
    "get_user_by_id",
    "upload_audio",
]


def add_to_live(
    *,
    attendees: list[Any] | None = DEFAULT,
    duration: int | None = DEFAULT,
    language: str | None = DEFAULT,
    meeting_link: str,
    meeting_password: str | None = DEFAULT,
    title: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Fireflies: Add To Live"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = AddToLiveInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="add_to_live", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_transcript_by_id(*, id: str | None = DEFAULT) -> ComposioResult:
    """Execute Fireflies: Delete Transcript By Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteTranscriptByIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies",
        name="delete_transcript_by_id",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def fetch_ai_app_outputs(
    *,
    app_id: str,
    limit: int | None = DEFAULT,
    skip: int | None = DEFAULT,
    transcript_id: str,
) -> ComposioResult:
    """Execute Fireflies: Fetch Ai App Outputs"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FetchAiAppOutputsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="fetch_ai_app_outputs", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_bites(
    *,
    limit: int | None = DEFAULT,
    mine: bool | None = DEFAULT,
    my_team: bool | None = DEFAULT,
    skip: int | None = DEFAULT,
    transcript_id: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Fireflies: Get Bites"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetBitesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="get_bites", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_bite_by_id(*, id: str | None = DEFAULT) -> ComposioResult:
    """Execute Fireflies: Get Bite By Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetBiteByIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="get_bite_by_id", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_transcripts(
    *,
    from_date: str | None = DEFAULT,
    host_email: str | None = DEFAULT,
    limit: int | None = DEFAULT,
    organizer_email: str | None = DEFAULT,
    participant_email: str | None = DEFAULT,
    skip: int | None = DEFAULT,
    title: str | None = DEFAULT,
    to_date: str | None = DEFAULT,
    user_id: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Fireflies: Get Transcripts"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetTranscriptsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="get_transcripts", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_transcript_by_id(*, id: str) -> ComposioResult:
    """Execute Fireflies: Get Transcript By Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetTranscriptByIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="get_transcript_by_id", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_users() -> ComposioResult:
    """Execute Fireflies: Get Users"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetUsersInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="get_users", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_user_by_id(*, id: str) -> ComposioResult:
    """Execute Fireflies: Get User By Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetUserByIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="get_user_by_id", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def upload_audio(
    *,
    attendees: list[Any] | None = DEFAULT,
    client_reference_id: str | None = DEFAULT,
    custom_language: str | None = DEFAULT,
    save_video: bool | None = DEFAULT,
    title: str,
    url: str,
    webhook: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Fireflies: Upload Audio"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = UploadAudioInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="fireflies", name="upload_audio", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)
