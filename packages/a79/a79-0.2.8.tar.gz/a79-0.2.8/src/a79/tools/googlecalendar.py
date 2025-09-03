# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any, Dict, List, Literal

from pydantic import BaseModel

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.composio_models import ComposioResult
from ..models.tools.googlecalendar_models import (
    CalendarListInsertInput,
    CalendarsDeleteInput,
    CalendarsUpdateInput,
    ClearCalendarInput,
    CreateEventInput,
    DeleteEventInput,
    DuplicateCalendarInput,
    EventsInstancesInput,
    EventsListInput,
    EventsMoveInput,
    EventsWatchInput,
    FindEventInput,
    FindFreeSlotsInput,
    FreeBusyQueryInput,
    GetCalendarInput,
    GooglecalendarCalendarListUpdateInput,
    PatchCalendarInput,
    PatchEventInput,
    SyncEventsInput,
    UpdateEventInput,
)


__all__ = [
    "CalendarListInsertInput",
    "CalendarsDeleteInput",
    "CalendarsUpdateInput",
    "ClearCalendarInput",
    "CreateEventInput",
    "DeleteEventInput",
    "DuplicateCalendarInput",
    "EventsInstancesInput",
    "EventsListInput",
    "EventsMoveInput",
    "EventsWatchInput",
    "FindEventInput",
    "FindFreeSlotsInput",
    "FreeBusyQueryInput",
    "GetCalendarInput",
    "GooglecalendarCalendarListUpdateInput",
    "PatchCalendarInput",
    "PatchEventInput",
    "SyncEventsInput",
    "UpdateEventInput",
    "calendars_delete",
    "calendars_update",
    "calendar_list_insert",
    "create_event",
    "delete_event",
    "duplicate_calendar",
    "events_instances",
    "find_event",
    "free_busy_query",
    "get_calendar",
    "patch_calendar",
    "patch_event",
    "sync_events",
    "update_event",
    "googlecalendar_calendar_list_update",
    "clear_calendar",
    "events_list",
    "events_move",
    "events_watch",
    "find_free_slots",
]


def calendars_delete(*, calendar_id: str) -> ComposioResult:
    """Execute Googlecalendar: Calendars Delete"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CalendarsDeleteInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="calendars_delete", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def calendars_update(
    *,
    calendarId: str,
    description: str | None = DEFAULT,
    location: str | None = DEFAULT,
    summary: str,
    timeZone: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Calendars Update"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CalendarsUpdateInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="calendars_update", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def calendar_list_insert(
    *,
    background_color: str | None = DEFAULT,
    color_id: str | None = DEFAULT,
    color_rgb_format: bool | None = DEFAULT,
    default_reminders: list[Any] | None = DEFAULT,
    foreground_color: str | None = DEFAULT,
    hidden: bool | None = DEFAULT,
    id: str,
    notification_settings: dict[str, Any] | None = DEFAULT,
    selected: bool | None = DEFAULT,
    summary_override: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Calendar List Insert"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CalendarListInsertInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar",
        name="calendar_list_insert",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def create_event(
    *,
    attendees: list[Any] | None = DEFAULT,
    calendar_id: str | None = DEFAULT,
    create_meeting_room: bool | None = DEFAULT,
    description: str | None = DEFAULT,
    eventType: Literal["default", "outOfOffice", "focusTime", "workingLocation"]
    | None = DEFAULT,
    event_duration_hour: int | None = DEFAULT,
    event_duration_minutes: int | None = DEFAULT,
    exclude_organizer: bool | None = DEFAULT,
    guestsCanInviteOthers: bool | None = DEFAULT,
    guestsCanSeeOtherGuests: bool | None = DEFAULT,
    guests_can_modify: bool | None = DEFAULT,
    location: str | None = DEFAULT,
    recurrence: list[Any] | None = DEFAULT,
    send_updates: bool | None = DEFAULT,
    start_datetime: str,
    summary: str | None = DEFAULT,
    timezone: str | None = DEFAULT,
    transparency: Literal["opaque", "transparent"] | None = DEFAULT,
    visibility: Literal["default", "public", "private", "confidential"] | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Create Event"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateEventInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="create_event", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_event(*, calendar_id: str | None = DEFAULT, event_id: str) -> ComposioResult:
    """Execute Googlecalendar: Delete Event"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteEventInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="delete_event", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def duplicate_calendar(*, summary: str | None = DEFAULT) -> ComposioResult:
    """Execute Googlecalendar: Duplicate Calendar"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DuplicateCalendarInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar",
        name="duplicate_calendar",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def events_instances(
    *,
    calendarId: str,
    eventId: str,
    maxAttendees: int | None = DEFAULT,
    maxResults: int | None = DEFAULT,
    originalStart: str | None = DEFAULT,
    pageToken: str | None = DEFAULT,
    showDeleted: bool | None = DEFAULT,
    timeMax: str | None = DEFAULT,
    timeMin: str | None = DEFAULT,
    timeZone: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Events Instances"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = EventsInstancesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="events_instances", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def find_event(
    *,
    calendar_id: str | None = DEFAULT,
    event_types: list[Any] | None = DEFAULT,
    max_results: int | None = DEFAULT,
    order_by: str | None = DEFAULT,
    page_token: str | None = DEFAULT,
    query: str | None = DEFAULT,
    show_deleted: bool | None = DEFAULT,
    single_events: bool | None = DEFAULT,
    timeMax: str | None = DEFAULT,
    timeMin: str | None = DEFAULT,
    updated_min: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Find Event"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FindEventInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="find_event", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def free_busy_query(
    *,
    calendarExpansionMax: int | None = DEFAULT,
    groupExpansionMax: int | None = DEFAULT,
    items: list[Any],
    timeMax: str,
    timeMin: str,
    timeZone: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Free Busy Query"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FreeBusyQueryInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="free_busy_query", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_calendar(*, calendar_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Googlecalendar: Get Calendar"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetCalendarInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="get_calendar", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def patch_calendar(
    *,
    calendar_id: str,
    description: str | None = DEFAULT,
    location: str | None = DEFAULT,
    summary: str,
    timezone: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Patch Calendar"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = PatchCalendarInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="patch_calendar", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def patch_event(
    *,
    attendees: list[Any] | None = DEFAULT,
    calendar_id: str,
    conference_data_version: int | None = DEFAULT,
    description: str | None = DEFAULT,
    end_time: str | None = DEFAULT,
    event_id: str,
    location: str | None = DEFAULT,
    max_attendees: int | None = DEFAULT,
    rsvp_response: str | None = DEFAULT,
    send_updates: str | None = DEFAULT,
    start_time: str | None = DEFAULT,
    summary: str | None = DEFAULT,
    supports_attachments: bool | None = DEFAULT,
    timezone: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Patch Event"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = PatchEventInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="patch_event", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def sync_events(
    *,
    calendar_id: str | None = DEFAULT,
    event_types: list[Any] | None = DEFAULT,
    max_results: int | None = DEFAULT,
    pageToken: str | None = DEFAULT,
    single_events: bool | None = DEFAULT,
    sync_token: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Sync Events"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SyncEventsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="sync_events", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def update_event(
    *,
    attendees: list[Any] | None = DEFAULT,
    calendar_id: str | None = DEFAULT,
    create_meeting_room: bool | None = DEFAULT,
    description: str | None = DEFAULT,
    eventType: Literal["default", "outOfOffice", "focusTime", "workingLocation"]
    | None = DEFAULT,
    event_duration_hour: int | None = DEFAULT,
    event_duration_minutes: int | None = DEFAULT,
    event_id: str,
    guestsCanInviteOthers: bool | None = DEFAULT,
    guestsCanSeeOtherGuests: bool | None = DEFAULT,
    guests_can_modify: bool | None = DEFAULT,
    location: str | None = DEFAULT,
    recurrence: list[Any] | None = DEFAULT,
    send_updates: bool | None = DEFAULT,
    start_datetime: str,
    summary: str | None = DEFAULT,
    timezone: str | None = DEFAULT,
    transparency: Literal["opaque", "transparent"] | None = DEFAULT,
    visibility: Literal["default", "public", "private", "confidential"] | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Update Event"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = UpdateEventInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="update_event", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def googlecalendar_calendar_list_update(
    *,
    backgroundColor: str | None = DEFAULT,
    calendar_id: str,
    colorId: str | None = DEFAULT,
    colorRgbFormat: bool | None = DEFAULT,
    defaultReminders: list[Any] | None = DEFAULT,
    foregroundColor: str | None = DEFAULT,
    hidden: bool | None = DEFAULT,
    notificationSettings: dict[str, Any] | None = DEFAULT,
    selected: bool | None = DEFAULT,
    summaryOverride: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Googlecalendar Calendar List Update"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GooglecalendarCalendarListUpdateInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar",
        name="googlecalendar_calendar_list_update",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def clear_calendar(*, calendar_id: str) -> ComposioResult:
    """Execute Googlecalendar: Clear Calendar"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ClearCalendarInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="clear_calendar", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def events_list(
    *,
    alwaysIncludeEmail: bool | None = DEFAULT,
    calendarId: str,
    eventTypes: str | None = DEFAULT,
    iCalUID: str | None = DEFAULT,
    maxAttendees: int | None = DEFAULT,
    maxResults: int | None = DEFAULT,
    orderBy: str | None = DEFAULT,
    pageToken: str | None = DEFAULT,
    privateExtendedProperty: str | None = DEFAULT,
    q: str | None = DEFAULT,
    sharedExtendedProperty: str | None = DEFAULT,
    showDeleted: bool | None = DEFAULT,
    showHiddenInvitations: bool | None = DEFAULT,
    singleEvents: bool | None = DEFAULT,
    syncToken: str | None = DEFAULT,
    timeMax: str | None = DEFAULT,
    timeMin: str | None = DEFAULT,
    timeZone: str | None = DEFAULT,
    updatedMin: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Events List"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = EventsListInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="events_list", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def events_move(
    *,
    calendar_id: str,
    destination: str,
    event_id: str,
    send_updates: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Events Move"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = EventsMoveInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="events_move", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def events_watch(
    *,
    address: str,
    calendarId: str,
    id: str,
    params: dict[str, Any] | None = DEFAULT,
    payload: bool | None = DEFAULT,
    token: str | None = DEFAULT,
    type: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Events Watch"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = EventsWatchInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="events_watch", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def find_free_slots(
    *,
    calendar_expansion_max: int | None = DEFAULT,
    group_expansion_max: int | None = DEFAULT,
    items: list[Any] | None = DEFAULT,
    time_max: str | None = DEFAULT,
    time_min: str | None = DEFAULT,
    timezone: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googlecalendar: Find Free Slots"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FindFreeSlotsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googlecalendar", name="find_free_slots", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)
