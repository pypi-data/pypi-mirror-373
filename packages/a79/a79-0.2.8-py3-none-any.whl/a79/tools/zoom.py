# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any, Dict, List, Literal

from pydantic import BaseModel

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.composio_models import ComposioResult
from ..models.tools.zoom_models import (
    AddAMeetingRegistrantInput,
    AddAWebinarRegistrantInput,
    CreateAMeetingInput,
    DeleteMeetingRecordingsInput,
    GetAMeetingInput,
    GetAMeetingSummaryInput,
    GetAWebinarInput,
    GetDailyUsageReportInput,
    GetMeetingRecordingsInput,
    GetPastMeetingParticipantsInput,
    ListAllRecordingsInput,
    ListArchivedFilesInput,
    ListDevicesInput,
    ListMeetingsInput,
    ListWebinarParticipantsInput,
    ListWebinarsInput,
    UpdateAMeetingInput,
)


__all__ = [
    "AddAMeetingRegistrantInput",
    "AddAWebinarRegistrantInput",
    "CreateAMeetingInput",
    "DeleteMeetingRecordingsInput",
    "GetAMeetingInput",
    "GetAMeetingSummaryInput",
    "GetAWebinarInput",
    "GetDailyUsageReportInput",
    "GetMeetingRecordingsInput",
    "GetPastMeetingParticipantsInput",
    "ListAllRecordingsInput",
    "ListArchivedFilesInput",
    "ListDevicesInput",
    "ListMeetingsInput",
    "ListWebinarParticipantsInput",
    "ListWebinarsInput",
    "UpdateAMeetingInput",
    "create_a_meeting",
    "get_a_meeting",
    "get_a_meeting_summary",
    "get_meeting_recordings",
    "list_all_recordings",
    "list_meetings",
    "add_a_meeting_registrant",
    "add_a_webinar_registrant",
    "delete_meeting_recordings",
    "get_a_webinar",
    "get_daily_usage_report",
    "get_past_meeting_participants",
    "list_archived_files",
    "list_devices",
    "list_webinars",
    "list_webinar_participants",
    "update_a_meeting",
]


def create_a_meeting(
    *,
    agenda: str | None = DEFAULT,
    default_password: bool | None = DEFAULT,
    duration: int | None = DEFAULT,
    password: str | None = DEFAULT,
    pre_schedule: bool | None = DEFAULT,
    recurrence__end__date__time: str | None = DEFAULT,
    recurrence__end__times: int | None = DEFAULT,
    recurrence__monthly__day: int | None = DEFAULT,
    recurrence__monthly__week: int | None = DEFAULT,
    recurrence__monthly__week__day: int | None = DEFAULT,
    recurrence__repeat__interval: int | None = DEFAULT,
    recurrence__type: int | None = DEFAULT,
    recurrence__weekly__days: Literal["1", "2", "3", "4", "5", "6", "7"] | None = DEFAULT,
    schedule_for: str | None = DEFAULT,
    settings__additional__data__center__regions: list[Any] | None = DEFAULT,
    settings__allow__multiple__devices: bool | None = DEFAULT,
    settings__alternative__host__update__polls: bool | None = DEFAULT,
    settings__alternative__hosts: str | None = DEFAULT,
    settings__alternative__hosts__email__notification: bool | None = DEFAULT,
    settings__approval__type: int | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__approved__list: list[Any]
    | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__denied__list: list[Any]
    | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__enable: bool | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__method: Literal[
        "approve", "deny"
    ]
    | None = DEFAULT,
    settings__audio: Literal["both", "telephony", "voip", "thirdParty"] | None = DEFAULT,
    settings__audio__conference__info: str | None = DEFAULT,
    settings__authentication__domains: str | None = DEFAULT,
    settings__authentication__exception: list[Any] | None = DEFAULT,
    settings__authentication__option: str | None = DEFAULT,
    settings__auto__recording: Literal["local", "cloud", "none"] | None = DEFAULT,
    settings__auto__start__ai__companion__questions: bool | None = DEFAULT,
    settings__auto__start__meeting__summary: bool | None = DEFAULT,
    settings__breakout__room__enable: bool | None = DEFAULT,
    settings__breakout__room__rooms: list[Any] | None = DEFAULT,
    settings__calendar__type: int | None = DEFAULT,
    settings__close__registration: bool | None = DEFAULT,
    settings__cn__meeting: bool | None = DEFAULT,
    settings__contact__email: str | None = DEFAULT,
    settings__contact__name: str | None = DEFAULT,
    settings__continuous__meeting__chat__auto__add__invited__external__users: bool
    | None = DEFAULT,
    settings__continuous__meeting__chat__enable: bool | None = DEFAULT,
    settings__email__notification: bool | None = DEFAULT,
    settings__encryption__type: Literal["enhanced_encryption", "e2ee"] | None = DEFAULT,
    settings__focus__mode: bool | None = DEFAULT,
    settings__global__dial__in__countries: list[Any] | None = DEFAULT,
    settings__host__save__video__order: bool | None = DEFAULT,
    settings__host__video: bool | None = DEFAULT,
    settings__in__meeting: bool | None = DEFAULT,
    settings__internal__meeting: bool | None = DEFAULT,
    settings__jbh__time: int | None = DEFAULT,
    settings__join__before__host: bool | None = DEFAULT,
    settings__language__interpretation__enable: bool | None = DEFAULT,
    settings__language__interpretation__interpreters: list[Any] | None = DEFAULT,
    settings__meeting__authentication: bool | None = DEFAULT,
    settings__meeting__invitees: list[Any] | None = DEFAULT,
    settings__mute__upon__entry: bool | None = DEFAULT,
    settings__participant__focused__meeting: bool | None = DEFAULT,
    settings__participant__video: bool | None = DEFAULT,
    settings__private__meeting: bool | None = DEFAULT,
    settings__push__change__to__calendar: bool | None = DEFAULT,
    settings__registrants__confirmation__email: bool | None = DEFAULT,
    settings__registrants__email__notification: bool | None = DEFAULT,
    settings__registration__type: int | None = DEFAULT,
    settings__resources: list[Any] | None = DEFAULT,
    settings__show__share__button: bool | None = DEFAULT,
    settings__sign__language__interpretation__enable: bool | None = DEFAULT,
    settings__sign__language__interpretation__interpreters: list[Any] | None = DEFAULT,
    settings__use__pmi: bool | None = DEFAULT,
    settings__waiting__room: bool | None = DEFAULT,
    settings__watermark: bool | None = DEFAULT,
    start_time: str | None = DEFAULT,
    template_id: str | None = DEFAULT,
    timezone: str | None = DEFAULT,
    topic: str | None = DEFAULT,
    tracking_fields: list[Any] | None = DEFAULT,
    type: int | None = DEFAULT,
    userId: str,
) -> ComposioResult:
    """Execute Zoom: Create A Meeting"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateAMeetingInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="create_a_meeting", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_a_meeting(
    *,
    meetingId: int,
    occurrence_id: str | None = DEFAULT,
    show_previous_occurrences: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: Get A Meeting"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetAMeetingInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="get_a_meeting", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_a_meeting_summary(*, meetingId: str) -> ComposioResult:
    """Execute Zoom: Get A Meeting Summary"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetAMeetingSummaryInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="get_a_meeting_summary", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_meeting_recordings(
    *, include_fields: str | None = DEFAULT, meetingId: str, ttl: int | None = DEFAULT
) -> ComposioResult:
    """Execute Zoom: Get Meeting Recordings"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetMeetingRecordingsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="get_meeting_recordings", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def list_all_recordings(
    *,
    from_: str | None = DEFAULT,
    mc: str | None = DEFAULT,
    meeting_id: int | None = DEFAULT,
    next_page_token: str | None = DEFAULT,
    page_size: int | None = DEFAULT,
    to_: str | None = DEFAULT,
    trash: bool | None = DEFAULT,
    trash_type: str | None = DEFAULT,
    userId: str,
) -> ComposioResult:
    """Execute Zoom: List All Recordings"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListAllRecordingsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="list_all_recordings", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def list_meetings(
    *,
    from_: str | None = DEFAULT,
    next_page_token: str | None = DEFAULT,
    page_number: int | None = DEFAULT,
    page_size: int | None = DEFAULT,
    timezone: str | None = DEFAULT,
    to_: str | None = DEFAULT,
    type: Literal[
        "scheduled", "live", "upcoming", "upcoming_meetings", "previous_meetings"
    ]
    | None = DEFAULT,
    userId: str,
) -> ComposioResult:
    """Execute Zoom: List Meetings"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListMeetingsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="list_meetings", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def add_a_meeting_registrant(
    *,
    address: str | None = DEFAULT,
    auto_approve: bool | None = DEFAULT,
    city: str | None = DEFAULT,
    comments: str | None = DEFAULT,
    country: str | None = DEFAULT,
    custom_questions: list[Any] | None = DEFAULT,
    email: str,
    first_name: str,
    industry: str | None = DEFAULT,
    job_title: str | None = DEFAULT,
    language: Literal[
        "en-US",
        "de-DE",
        "es-ES",
        "fr-FR",
        "jp-JP",
        "pt-PT",
        "ru-RU",
        "zh-CN",
        "zh-TW",
        "ko-KO",
        "it-IT",
        "vi-VN",
        "pl-PL",
        "Tr-TR",
    ]
    | None = DEFAULT,
    last_name: str | None = DEFAULT,
    meetingId: int,
    no_of_employees: Literal[
        "",
        "1-20",
        "21-50",
        "51-100",
        "101-500",
        "500-1,000",
        "1,001-5,000",
        "5,001-10,000",
        "More than 10,000",
    ]
    | None = DEFAULT,
    occurrence_ids: str | None = DEFAULT,
    org: str | None = DEFAULT,
    phone: str | None = DEFAULT,
    purchasing_time_frame: Literal[
        "",
        "Within a month",
        "1-3 months",
        "4-6 months",
        "More than 6 months",
        "No timeframe",
    ]
    | None = DEFAULT,
    role_in_purchase_process: Literal[
        "", "Decision Maker", "Evaluator/Recommender", "Influencer", "Not involved"
    ]
    | None = DEFAULT,
    state: str | None = DEFAULT,
    zip: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: Add A Meeting Registrant"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = AddAMeetingRegistrantInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="add_a_meeting_registrant", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def add_a_webinar_registrant(
    *,
    address: str | None = DEFAULT,
    city: str | None = DEFAULT,
    comments: str | None = DEFAULT,
    country: str | None = DEFAULT,
    custom_questions: list[Any] | None = DEFAULT,
    email: str,
    first_name: str,
    industry: str | None = DEFAULT,
    job_title: str | None = DEFAULT,
    language: Literal[
        "en-US",
        "de-DE",
        "es-ES",
        "fr-FR",
        "jp-JP",
        "pt-PT",
        "ru-RU",
        "zh-CN",
        "zh-TW",
        "ko-KO",
        "it-IT",
        "vi-VN",
        "pl-PL",
        "Tr-TR",
    ]
    | None = DEFAULT,
    last_name: str | None = DEFAULT,
    no_of_employees: Literal[
        "",
        "1-20",
        "21-50",
        "51-100",
        "101-500",
        "500-1,000",
        "1,001-5,000",
        "5,001-10,000",
        "More than 10,000",
    ]
    | None = DEFAULT,
    occurrence_ids: str | None = DEFAULT,
    org: str | None = DEFAULT,
    phone: str | None = DEFAULT,
    purchasing_time_frame: Literal[
        "",
        "Within a month",
        "1-3 months",
        "4-6 months",
        "More than 6 months",
        "No timeframe",
    ]
    | None = DEFAULT,
    role_in_purchase_process: Literal[
        "", "Decision Maker", "Evaluator/Recommender", "Influencer", "Not involved"
    ]
    | None = DEFAULT,
    source_id: str | None = DEFAULT,
    state: str | None = DEFAULT,
    webinarId: int,
    zip: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: Add A Webinar Registrant"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = AddAWebinarRegistrantInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="add_a_webinar_registrant", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_meeting_recordings(
    *, action: Literal["trash", "delete"] | None = DEFAULT, meetingId: str
) -> ComposioResult:
    """Execute Zoom: Delete Meeting Recordings"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteMeetingRecordingsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="delete_meeting_recordings", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_a_webinar(
    *,
    occurrence_id: str | None = DEFAULT,
    show_previous_occurrences: bool | None = DEFAULT,
    webinarId: str,
) -> ComposioResult:
    """Execute Zoom: Get A Webinar"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetAWebinarInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="get_a_webinar", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_daily_usage_report(
    *,
    group_id: str | None = DEFAULT,
    month: int | None = DEFAULT,
    year: int | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: Get Daily Usage Report"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetDailyUsageReportInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="get_daily_usage_report", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_past_meeting_participants(
    *,
    meetingId: str,
    next_page_token: str | None = DEFAULT,
    page_size: int | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: Get Past Meeting Participants"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetPastMeetingParticipantsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom",
        name="get_past_meeting_participants",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def list_archived_files(
    *,
    from_: str | None = DEFAULT,
    group_id: str | None = DEFAULT,
    next_page_token: str | None = DEFAULT,
    page_size: int | None = DEFAULT,
    query_date_type: Literal["meeting_start_time", "archive_complete_time"]
    | None = DEFAULT,
    to_: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: List Archived Files"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListArchivedFilesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="list_archived_files", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def list_devices(
    *,
    device_model: str | None = DEFAULT,
    device_status: int | None = DEFAULT,
    device_type: int | None = DEFAULT,
    device_vendor: str | None = DEFAULT,
    is_enrolled_in_zdm: bool | None = DEFAULT,
    next_page_token: str | None = DEFAULT,
    page_size: int | None = DEFAULT,
    platform_os: Literal["win", "mac", "ipad", "iphone", "android", "linux"]
    | None = DEFAULT,
    search_text: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: List Devices"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListDevicesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="list_devices", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def list_webinars(
    *,
    page_number: int | None = DEFAULT,
    page_size: int | None = DEFAULT,
    type: Literal["scheduled", "upcoming"] | None = DEFAULT,
    userId: str,
) -> ComposioResult:
    """Execute Zoom: List Webinars"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListWebinarsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="list_webinars", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def list_webinar_participants(
    *,
    next_page_token: str | None = DEFAULT,
    page_size: int | None = DEFAULT,
    webinarId: str,
) -> ComposioResult:
    """Execute Zoom: List Webinar Participants"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListWebinarParticipantsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="list_webinar_participants", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def update_a_meeting(
    *,
    agenda: str | None = DEFAULT,
    duration: int | None = DEFAULT,
    meetingId: int,
    occurrence_id: str | None = DEFAULT,
    password: str | None = DEFAULT,
    pre_schedule: bool | None = DEFAULT,
    recurrence__end__date__time: str | None = DEFAULT,
    recurrence__end__times: int | None = DEFAULT,
    recurrence__monthly__day: int | None = DEFAULT,
    recurrence__monthly__week: int | None = DEFAULT,
    recurrence__monthly__week__day: int | None = DEFAULT,
    recurrence__repeat__interval: int | None = DEFAULT,
    recurrence__type: int | None = DEFAULT,
    recurrence__weekly__days: Literal["1", "2", "3", "4", "5", "6", "7"] | None = DEFAULT,
    schedule_for: str | None = DEFAULT,
    settings__allow__multiple__devices: bool | None = DEFAULT,
    settings__alternative__host__update__polls: bool | None = DEFAULT,
    settings__alternative__hosts: str | None = DEFAULT,
    settings__alternative__hosts__email__notification: bool | None = DEFAULT,
    settings__approval__type: int | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__approved__list: list[Any]
    | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__denied__list: list[Any]
    | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__enable: bool | None = DEFAULT,
    settings__approved__or__denied__countries__or__regions__method: Literal[
        "approve", "deny"
    ]
    | None = DEFAULT,
    settings__audio: Literal["both", "telephony", "voip", "thirdParty"] | None = DEFAULT,
    settings__audio__conference__info: str | None = DEFAULT,
    settings__authentication__domains: str | None = DEFAULT,
    settings__authentication__exception: list[Any] | None = DEFAULT,
    settings__authentication__name: str | None = DEFAULT,
    settings__authentication__option: str | None = DEFAULT,
    settings__auto__recording: Literal["local", "cloud", "none"] | None = DEFAULT,
    settings__auto__start__ai__companion__questions: bool | None = DEFAULT,
    settings__auto__start__meeting__summary: bool | None = DEFAULT,
    settings__breakout__room__enable: bool | None = DEFAULT,
    settings__breakout__room__rooms: list[Any] | None = DEFAULT,
    settings__calendar__type: int | None = DEFAULT,
    settings__close__registration: bool | None = DEFAULT,
    settings__cn__meeting: bool | None = DEFAULT,
    settings__contact__email: str | None = DEFAULT,
    settings__contact__name: str | None = DEFAULT,
    settings__continuous__meeting__chat__auto__add__invited__external__users: bool
    | None = DEFAULT,
    settings__continuous__meeting__chat__enable: bool | None = DEFAULT,
    settings__custom__keys: list[Any] | None = DEFAULT,
    settings__email__notification: bool | None = DEFAULT,
    settings__encryption__type: Literal["enhanced_encryption", "e2ee"] | None = DEFAULT,
    settings__enforce__login: bool | None = DEFAULT,
    settings__enforce__login__domains: str | None = DEFAULT,
    settings__focus__mode: bool | None = DEFAULT,
    settings__global__dial__in__countries: list[Any] | None = DEFAULT,
    settings__global__dial__in__numbers: list[Any] | None = DEFAULT,
    settings__host__save__video__order: bool | None = DEFAULT,
    settings__host__video: bool | None = DEFAULT,
    settings__in__meeting: bool | None = DEFAULT,
    settings__internal__meeting: bool | None = DEFAULT,
    settings__jbh__time: int | None = DEFAULT,
    settings__join__before__host: bool | None = DEFAULT,
    settings__language__interpretation__enable: bool | None = DEFAULT,
    settings__language__interpretation__interpreters: list[Any] | None = DEFAULT,
    settings__meeting__authentication: bool | None = DEFAULT,
    settings__meeting__invitees: list[Any] | None = DEFAULT,
    settings__mute__upon__entry: bool | None = DEFAULT,
    settings__participant__focused__meeting: bool | None = DEFAULT,
    settings__participant__video: bool | None = DEFAULT,
    settings__private__meeting: bool | None = DEFAULT,
    settings__registrants__confirmation__email: bool | None = DEFAULT,
    settings__registrants__email__notification: bool | None = DEFAULT,
    settings__registration__type: int | None = DEFAULT,
    settings__resources: list[Any] | None = DEFAULT,
    settings__show__share__button: bool | None = DEFAULT,
    settings__sign__language__interpretation__enable: bool | None = DEFAULT,
    settings__sign__language__interpretation__interpreters: list[Any] | None = DEFAULT,
    settings__use__pmi: bool | None = DEFAULT,
    settings__waiting__room: bool | None = DEFAULT,
    settings__watermark: bool | None = DEFAULT,
    start_time: str | None = DEFAULT,
    template_id: str | None = DEFAULT,
    timezone: str | None = DEFAULT,
    topic: str | None = DEFAULT,
    tracking_fields: list[Any] | None = DEFAULT,
    type: int | None = DEFAULT,
) -> ComposioResult:
    """Execute Zoom: Update A Meeting"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = UpdateAMeetingInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="zoom", name="update_a_meeting", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)
