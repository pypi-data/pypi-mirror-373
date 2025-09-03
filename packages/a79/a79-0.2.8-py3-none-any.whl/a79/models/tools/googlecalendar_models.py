# This is a generated file by scripts/codegen/composio.py, do not edit manually
# ruff: noqa: E501  # Ignore line length issues in generated files
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class CalendarsDeleteInput(BaseModel):
    """Input model for GOOGLECALENDAR_CALENDARS_DELETE"""

    calendar_id: str = Field(
        description="""Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you want to access the primary calendar of the currently logged in user, use the "primary" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class CalendarsUpdateInput(BaseModel):
    """Input model for GOOGLECALENDAR_CALENDARS_UPDATE"""

    calendarId: str = Field(
        description="""Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you want to access the primary calendar of the currently logged in user, use the "primary" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    description: Optional[str] = Field(
        default=None,
        description="""Description of the calendar. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    location: Optional[str] = Field(
        default=None,
        description="""Geographic location of the calendar as free-form text. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    summary: str = Field(
        description="""Title of the calendar. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    timeZone: Optional[str] = Field(
        default=None,
        description="""The time zone of the calendar. (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich".) Optional. Please provide a value of type string.""",
    )  # noqa: E501


class CalendarListInsertInput(BaseModel):
    """Input model for GOOGLECALENDAR_CALENDAR_LIST_INSERT"""

    background_color: Optional[str] = Field(
        default=None,
        description="""The background color of the calendar in the Web UI. (Hexadecimal color code). Please provide a value of type string.""",
    )  # noqa: E501

    color_id: Optional[str] = Field(
        default=None,
        description="""The color of the calendar. This is an ID referring to an entry in the calendarCore color palette. Please provide a value of type string.""",
    )  # noqa: E501

    color_rgb_format: Optional[bool] = Field(
        default=None,
        description="""Whether to use the foregroundColor and backgroundColor fields to write the calendar colors (RGB). If this feature is used, the index-based colorId field will be set to the best matching option automatically. Optional. The default is False. Please provide a value of type boolean.""",
    )  # noqa: E501

    default_reminders: Optional[list[Any]] = Field(
        default=None,
        description="""The default reminders that the authenticated user has for this calendar.""",
    )  # noqa: E501

    foreground_color: Optional[str] = Field(
        default=None,
        description="""The foreground color of the calendar in the Web UI. (Hexadecimal color code). Please provide a value of type string.""",
    )  # noqa: E501

    hidden: Optional[bool] = Field(
        default=None,
        description="""Whether the calendar has been hidden from the list. Default is False. Please provide a value of type boolean.""",
    )  # noqa: E501

    id: str = Field(
        description="""The identifier of the calendar to insert. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    notification_settings: Optional[dict[str, Any]] = Field(
        default=None,
        description="""The notifications that the authenticated user is receiving for this calendar.""",
    )  # noqa: E501

    selected: Optional[bool] = Field(
        default=None,
        description="""Whether the calendar is selected and visible in the calendar list. Default is True. Please provide a value of type boolean.""",
    )  # noqa: E501

    summary_override: Optional[str] = Field(
        default=None,
        description="""The summary that the authenticated user has set for this calendar. Please provide a value of type string.""",
    )  # noqa: E501


class CreateEventInput(BaseModel):
    """Input model for GOOGLECALENDAR_CREATE_EVENT"""

    attendees: Optional[list[Any]] = Field(
        default=None, description="""List of attendee emails (strings)."""
    )  # noqa: E501

    calendar_id: Optional[str] = Field(
        default="primary",
        description="""Target calendar: 'primary' for the user's main calendar, or the calendar's email address. Please provide a value of type string.""",
    )  # noqa: E501

    create_meeting_room: Optional[bool] = Field(
        default=None,
        description="""If true, a Google Meet link is created and added to the event. CRITICAL: As of 2024, this REQUIRES a paid Google Workspace account ($13+/month). Personal Gmail accounts will fail with 'Invalid conference type value' error. Solutions: 1) Upgrade to Workspace, 2) Use domain-wide delegation with Workspace user, 3) Use the new Google Meet REST API, or 4) Create events without conferences. See https://github.com/googleapis/google-api-nodejs-client/issues/3234. Please provide a value of type boolean.""",
    )  # noqa: E501

    description: Optional[str] = Field(
        default=None,
        description="""Description of the event. Can contain HTML. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    eventType: Optional[
        Literal["default", "outOfOffice", "focusTime", "workingLocation"]
    ] = Field(
        default="default",
        description="""Type of the event, immutable post-creation. Currently, only 'default' and 'workingLocation' can be created. Please provide a value of type string.""",
    )  # noqa: E501

    event_duration_hour: Optional[int] = Field(
        default=0,
        description="""Number of hours (0-24). Increase by 1 here rather than passing 60 in `event_duration_minutes`. Please provide a value of type integer.""",
    )  # noqa: E501

    event_duration_minutes: Optional[int] = Field(
        default=30,
        description="""Duration in minutes (0-59 ONLY). NEVER use 60+ minutes - use event_duration_hour=1 instead. Maximum value is 59. Please provide a value of type integer.""",
    )  # noqa: E501

    exclude_organizer: Optional[bool] = Field(
        default=False,
        description="""If True, the organizer will NOT be added as an attendee. Default is False (organizer is included). Please provide a value of type boolean.""",
    )  # noqa: E501

    guestsCanInviteOthers: Optional[bool] = Field(
        default=None,
        description="""Whether attendees other than the organizer can invite others to the event. Please provide a value of type boolean.""",
    )  # noqa: E501

    guestsCanSeeOtherGuests: Optional[bool] = Field(
        default=None,
        description="""Whether attendees other than the organizer can see who the event's attendees are. Please provide a value of type boolean.""",
    )  # noqa: E501

    guests_can_modify: Optional[bool] = Field(
        default=False,
        description="""If True, guests can modify the event. Please provide a value of type boolean.""",
    )  # noqa: E501

    location: Optional[str] = Field(
        default=None,
        description="""Geographic location of the event as free-form text. Please provide a value of type string.""",
    )  # noqa: E501

    recurrence: Optional[list[Any]] = Field(
        default=None,
        description="""List of RRULE, EXRULE, RDATE, EXDATE lines for recurring events. Supported frequencies are DAILY, WEEKLY, MONTHLY, YEARLY.""",
    )  # noqa: E501

    send_updates: Optional[bool] = Field(
        default=None,
        description="""Defaults to True. Whether to send updates to the attendees. Please provide a value of type boolean.""",
    )  # noqa: E501

    start_datetime: str = Field(
        description="""Naive date/time (YYYY-MM-DDTHH:MM:SS) with NO offsets or Z. e.g. '2025-01-16T13:00:00'. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    summary: Optional[str] = Field(
        default=None,
        description="""Summary (title) of the event. Please provide a value of type string.""",
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default=None,
        description="""IANA timezone name (e.g., 'America/New_York'). Required if datetime is naive. If datetime includes timezone info (Z or offset), this field is optional and defaults to UTC. Please provide a value of type string.""",
    )  # noqa: E501

    transparency: Optional[Literal["opaque", "transparent"]] = Field(
        default="opaque",
        description="""'opaque' (busy) or 'transparent' (available). Please provide a value of type string.""",
    )  # noqa: E501

    visibility: Optional[Literal["default", "public", "private", "confidential"]] = Field(
        default="default",
        description="""Event visibility: 'default', 'public', 'private', or 'confidential'. Please provide a value of type string.""",
    )  # noqa: E501


class DeleteEventInput(BaseModel):
    """Input model for GOOGLECALENDAR_DELETE_EVENT"""

    calendar_id: Optional[str] = Field(
        default="primary",
        description="""Identifier of the Google Calendar (e.g., email address, specific ID, or 'primary' for the authenticated user's main calendar) from which the event will be deleted. Please provide a value of type string.""",
    )  # noqa: E501

    event_id: str = Field(
        description="""Unique identifier of the event to delete, typically obtained upon event creation. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class DuplicateCalendarInput(BaseModel):
    """Input model for GOOGLECALENDAR_DUPLICATE_CALENDAR"""

    summary: Optional[str] = Field(
        default="",
        description="""Title for the new Google Calendar to be created. If an empty string is provided, the calendar will be created without a title. Please provide a value of type string.""",
    )  # noqa: E501


class EventsInstancesInput(BaseModel):
    """Input model for GOOGLECALENDAR_EVENTS_INSTANCES"""

    calendarId: str = Field(
        description="""Calendar identifier. To retrieve calendar IDs call the `calendarList.list` method. If you want to access the primary calendar of the currently logged in user, use the "primary" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    eventId: str = Field(
        description="""Recurring event identifier. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    maxAttendees: Optional[int] = Field(
        default=None,
        description="""The maximum number of attendees to include in the response. If there are more than the specified number of attendees, only the participant is returned. Optional. Please provide a value of type integer.""",
    )  # noqa: E501

    maxResults: Optional[int] = Field(
        default=None,
        description="""Maximum number of events returned on one result page. By default the value is 250 events. The page size can never be larger than 2500 events. Optional. Please provide a value of type integer.""",
    )  # noqa: E501

    originalStart: Optional[str] = Field(
        default=None,
        description="""The original start time of the instance in the result. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    pageToken: Optional[str] = Field(
        default=None,
        description="""Token specifying which result page to return. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    showDeleted: Optional[bool] = Field(
        default=None,
        description="""Whether to include deleted events (with status equals "cancelled") in the result. Cancelled instances of recurring events will still be included if `singleEvents` is False. Optional. The default is False. Please provide a value of type boolean.""",
    )  # noqa: E501

    timeMax: Optional[str] = Field(
        default=None,
        description="""Upper bound (exclusive) for an event's start time to filter by. Optional. The default is not to filter by start time. Must be an RFC3339 timestamp with mandatory time zone offset. Please provide a value of type string.""",
    )  # noqa: E501

    timeMin: Optional[str] = Field(
        default=None,
        description="""Lower bound (inclusive) for an event's end time to filter by. Optional. The default is not to filter by end time. Must be an RFC3339 timestamp with mandatory time zone offset. Please provide a value of type string.""",
    )  # noqa: E501

    timeZone: Optional[str] = Field(
        default=None,
        description="""Time zone used in the response. Optional. The default is the time zone of the calendar. Please provide a value of type string.""",
    )  # noqa: E501


class FindEventInput(BaseModel):
    """Input model for GOOGLECALENDAR_FIND_EVENT"""

    calendar_id: Optional[str] = Field(
        default="primary",
        description="""Identifier of the Google Calendar to query. Use 'primary' for the primary calendar of the authenticated user, an email address for a specific user's calendar, or a calendar ID for other calendars. Please provide a value of type string.""",
    )  # noqa: E501

    event_types: Optional[list[Any]] = Field(
        default=["default", "outOfOffice", "focusTime", "workingLocation"],
        description="""Event types to include: 'default' (regular event), 'focusTime' (focused work time), 'outOfOffice' (out-of-office time).""",
    )  # noqa: E501

    max_results: Optional[int] = Field(
        default=10,
        description="""Maximum number of events per page (1-2500). Please provide a value of type integer.""",
    )  # noqa: E501

    order_by: Optional[str] = Field(
        default=None,
        description="""Order of events: 'startTime' (ascending by start time) or 'updated' (ascending by last modification time). Please provide a value of type string.""",
    )  # noqa: E501

    page_token: Optional[str] = Field(
        default=None,
        description="""Token from a previous response's `nextPageToken` to fetch the subsequent page of results. Please provide a value of type string.""",
    )  # noqa: E501

    query: Optional[str] = Field(
        default=None,
        description="""Free-text search terms to find events. This query is matched against various event fields including summary, description, location, attendees' details (displayName, email), and organizer's details. Please provide a value of type string.""",
    )  # noqa: E501

    show_deleted: Optional[bool] = Field(
        default=None,
        description="""Include deleted events (status 'cancelled') in the result. Please provide a value of type boolean.""",
    )  # noqa: E501

    single_events: Optional[bool] = Field(
        default=True,
        description="""Expand recurring events into individual instances. If false, returns master recurring events. Please provide a value of type boolean.""",
    )  # noqa: E501

    timeMax: Optional[str] = Field(
        default=None,
        description="""Upper bound (exclusive) for an event's start time to filter by. Only events starting before this time are included. Accepts multiple formats:
1. RFC3339 timestamp (e.g., '2024-12-06T13:00:00Z')
2. Comma-separated date/time parts (e.g., '2024,12,06,13,00,00')
3. Simple datetime string (e.g., '2024-12-06 13:00:00'). Please provide a value of type string.""",
    )  # noqa: E501

    timeMin: Optional[str] = Field(
        default=None,
        description="""Lower bound (exclusive) for an event's end time to filter by. Only events ending after this time are included. Accepts multiple formats:
1. RFC3339 timestamp (e.g., '2024-12-06T13:00:00Z')
2. Comma-separated date/time parts (e.g., '2024,12,06,13,00,00')
3. Simple datetime string (e.g., '2024-12-06 13:00:00'). Please provide a value of type string.""",
    )  # noqa: E501

    updated_min: Optional[str] = Field(
        default=None,
        description="""Lower bound (exclusive) for an event's last modification time to filter by. Only events updated after this time are included. When specified, events deleted since this time are also included, regardless of the `show_deleted` parameter. Accepts multiple formats:
1. RFC3339 timestamp (e.g., '2024-12-06T13:00:00Z')
2. Comma-separated date/time parts (e.g., '2024,12,06,13,00,00')
3. Simple datetime string (e.g., '2024-12-06 13:00:00'). Please provide a value of type string.""",
    )  # noqa: E501


class FreeBusyQueryInput(BaseModel):
    """Input model for GOOGLECALENDAR_FREE_BUSY_QUERY"""

    calendarExpansionMax: Optional[int] = Field(
        default=None,
        description="""Maximal number of calendars for which FreeBusy information is to be provided. Optional. Maximum value is 50. Please provide a value of type integer.""",
    )  # noqa: E501

    groupExpansionMax: Optional[int] = Field(
        default=None,
        description="""Maximal number of calendar identifiers to be provided for a single group. Optional. An error is returned for a group with more members than this value. Maximum value is 100. Please provide a value of type integer.""",
    )  # noqa: E501

    items: list[Any] = Field(
        description="""List of calendars and/or groups to query. This parameter is required."""
    )  # noqa: E501

    timeMax: str = Field(
        description="""The end of the interval for the query formatted as per RFC3339. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    timeMin: str = Field(
        description="""The start of the interval for the query formatted as per RFC3339. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    timeZone: Optional[str] = Field(
        default=None,
        description="""Time zone used in the response. Optional. The default is UTC. Please provide a value of type string.""",
    )  # noqa: E501


class GetCalendarInput(BaseModel):
    """Input model for GOOGLECALENDAR_GET_CALENDAR"""

    calendar_id: Optional[str] = Field(
        default="primary",
        description="""Identifier of the Google Calendar to retrieve. 'primary' (the default) represents the user's main calendar; other valid identifiers include the calendar's email address. Please provide a value of type string.""",
    )  # noqa: E501


class PatchCalendarInput(BaseModel):
    """Input model for GOOGLECALENDAR_PATCH_CALENDAR"""

    calendar_id: str = Field(
        description="""Identifier of the Google Calendar to update; use 'primary' for the main calendar or a specific ID. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    description: Optional[str] = Field(
        default=None,
        description="""New description for the calendar. Please provide a value of type string.""",
    )  # noqa: E501

    location: Optional[str] = Field(
        default=None,
        description="""New geographic location of the calendar (e.g., 'Paris, France'). Please provide a value of type string.""",
    )  # noqa: E501

    summary: str = Field(
        description="""New title for the calendar; cannot be an empty string. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default=None,
        description="""New IANA Time Zone Database name for the calendar (e.g., 'Europe/Zurich', 'America/New_York'). Please provide a value of type string.""",
    )  # noqa: E501


class PatchEventInput(BaseModel):
    """Input model for GOOGLECALENDAR_PATCH_EVENT"""

    attendees: Optional[list[Any]] = Field(
        default=None,
        description="""List of email addresses for attendees. Replaces existing attendees. Provide an empty list to remove all.""",
    )  # noqa: E501

    calendar_id: str = Field(
        description="""Identifier of the calendar. Use 'primary' for the primary calendar of the logged-in user. To find other calendar IDs, use the `calendarList.list` method. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    conference_data_version: Optional[int] = Field(
        default=None,
        description="""API client's conference data support version. Set to 1 to manage conference details (e.g., Google Meet links); 0 (default) ignores conference data. Please provide a value of type integer.""",
    )  # noqa: E501

    description: Optional[str] = Field(
        default=None,
        description="""New description for the event; can include HTML. Please provide a value of type string.""",
    )  # noqa: E501

    end_time: Optional[str] = Field(
        default=None,
        description="""New end time (RFC3339 timestamp, e.g., '2024-07-01T11:00:00-07:00'). Uses `timezone` if provided, otherwise UTC. For all-day events, use YYYY-MM-DD format (exclusive end date). Please provide a value of type string.""",
    )  # noqa: E501

    event_id: str = Field(
        description="""Identifier of the event to update. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    location: Optional[str] = Field(
        default=None,
        description="""New geographic location (physical address or virtual meeting link). Please provide a value of type string.""",
    )  # noqa: E501

    max_attendees: Optional[int] = Field(
        default=None,
        description="""Maximum attendees in response; does not affect invited count. If more, response includes organizer only. Must be positive. Please provide a value of type integer.""",
    )  # noqa: E501

    rsvp_response: Optional[str] = Field(
        default=None,
        description="""RSVP response status for the authenticated user. Updates only the current user's response status without affecting other attendees. Possible values: 'needsAction', 'declined', 'tentative', 'accepted'. Please provide a value of type string.""",
    )  # noqa: E501

    send_updates: Optional[str] = Field(
        default=None,
        description="""Whether to send update notifications to attendees: 'all', 'externalOnly', or 'none'. Uses default user behavior if unspecified. Please provide a value of type string.""",
    )  # noqa: E501

    start_time: Optional[str] = Field(
        default=None,
        description="""New start time (RFC3339 timestamp, e.g., '2024-07-01T10:00:00-07:00'). Uses `timezone` if provided, otherwise UTC. For all-day events, use YYYY-MM-DD format. Please provide a value of type string.""",
    )  # noqa: E501

    summary: Optional[str] = Field(
        default=None,
        description="""New title for the event. Please provide a value of type string.""",
    )  # noqa: E501

    supports_attachments: Optional[bool] = Field(
        default=None,
        description="""Client application supports event attachments. Set to `True` if so. Please provide a value of type boolean.""",
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default=None,
        description="""IANA Time Zone Database name for start/end times (e.g., 'America/Los_Angeles'). Used if `start_time` and `end_time` are provided and not all-day dates; defaults to UTC if unset. Please provide a value of type string.""",
    )  # noqa: E501


class SyncEventsInput(BaseModel):
    """Input model for GOOGLECALENDAR_SYNC_EVENTS"""

    calendar_id: Optional[str] = Field(
        default="primary",
        description="""Google Calendar identifier; 'primary' refers to the authenticated user's main calendar. Please provide a value of type string.""",
    )  # noqa: E501

    event_types: Optional[list[Any]] = Field(
        default=None,
        description="""Filters events by specified types (e.g., 'default', 'focusTime', 'outOfOffice', 'workingLocation'). All types returned if omitted.""",
    )  # noqa: E501

    max_results: Optional[int] = Field(
        default=None,
        description="""Max events per page (max 2500); Google Calendar's default is used if unspecified. Please provide a value of type integer.""",
    )  # noqa: E501

    pageToken: Optional[str] = Field(
        default=None,
        description="""Token for paginating results, from a previous response's `nextPageToken`. Please provide a value of type string.""",
    )  # noqa: E501

    single_events: Optional[bool] = Field(
        default=None,
        description="""If True, expands recurring events into individual instances (excluding master event); otherwise, Google's default handling applies. Please provide a value of type boolean.""",
    )  # noqa: E501

    sync_token: Optional[str] = Field(
        default=None,
        description="""Token for incremental sync, retrieving only changes since issued. A 410 GONE response indicates an expired token, requiring a full sync. Please provide a value of type string.""",
    )  # noqa: E501


class UpdateEventInput(BaseModel):
    """Input model for GOOGLECALENDAR_UPDATE_EVENT"""

    attendees: Optional[list[Any]] = Field(
        default=None, description="""List of attendee emails (strings)."""
    )  # noqa: E501

    calendar_id: Optional[str] = Field(
        default="primary",
        description="""Identifier of the Google Calendar where the event resides. The value 'primary' targets the user's primary calendar. Please provide a value of type string.""",
    )  # noqa: E501

    create_meeting_room: Optional[bool] = Field(
        default=None,
        description="""If true, a Google Meet link is created and added to the event. CRITICAL: As of 2024, this REQUIRES a paid Google Workspace account ($13+/month). Personal Gmail accounts will fail with 'Invalid conference type value' error. Solutions: 1) Upgrade to Workspace, 2) Use domain-wide delegation with Workspace user, 3) Use the new Google Meet REST API, or 4) Create events without conferences. See https://github.com/googleapis/google-api-nodejs-client/issues/3234. Please provide a value of type boolean.""",
    )  # noqa: E501

    description: Optional[str] = Field(
        default=None,
        description="""Description of the event. Can contain HTML. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    eventType: Optional[
        Literal["default", "outOfOffice", "focusTime", "workingLocation"]
    ] = Field(
        default="default",
        description="""Type of the event, immutable post-creation. Currently, only 'default' and 'workingLocation' can be created. Please provide a value of type string.""",
    )  # noqa: E501

    event_duration_hour: Optional[int] = Field(
        default=0,
        description="""Number of hours (0-24). Increase by 1 here rather than passing 60 in `event_duration_minutes`. Please provide a value of type integer.""",
    )  # noqa: E501

    event_duration_minutes: Optional[int] = Field(
        default=30,
        description="""Duration in minutes (0-59 ONLY). NEVER use 60+ minutes - use event_duration_hour=1 instead. Maximum value is 59. Please provide a value of type integer.""",
    )  # noqa: E501

    event_id: str = Field(
        description="""The unique identifier of the event to be updated. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    guestsCanInviteOthers: Optional[bool] = Field(
        default=None,
        description="""Whether attendees other than the organizer can invite others to the event. Please provide a value of type boolean.""",
    )  # noqa: E501

    guestsCanSeeOtherGuests: Optional[bool] = Field(
        default=None,
        description="""Whether attendees other than the organizer can see who the event's attendees are. Please provide a value of type boolean.""",
    )  # noqa: E501

    guests_can_modify: Optional[bool] = Field(
        default=False,
        description="""If True, guests can modify the event. Please provide a value of type boolean.""",
    )  # noqa: E501

    location: Optional[str] = Field(
        default=None,
        description="""Geographic location of the event as free-form text. Please provide a value of type string.""",
    )  # noqa: E501

    recurrence: Optional[list[Any]] = Field(
        default=None,
        description="""List of RRULE, EXRULE, RDATE, EXDATE lines for recurring events. Supported frequencies are DAILY, WEEKLY, MONTHLY, YEARLY.""",
    )  # noqa: E501

    send_updates: Optional[bool] = Field(
        default=None,
        description="""Defaults to True. Whether to send updates to the attendees. Please provide a value of type boolean.""",
    )  # noqa: E501

    start_datetime: str = Field(
        description="""Naive date/time (YYYY-MM-DDTHH:MM:SS) with NO offsets or Z. e.g. '2025-01-16T13:00:00'. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    summary: Optional[str] = Field(
        default=None,
        description="""Summary (title) of the event. Please provide a value of type string.""",
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default=None,
        description="""IANA timezone name (e.g., 'America/New_York'). Required if datetime is naive. If datetime includes timezone info (Z or offset), this field is optional and defaults to UTC. Please provide a value of type string.""",
    )  # noqa: E501

    transparency: Optional[Literal["opaque", "transparent"]] = Field(
        default="opaque",
        description="""'opaque' (busy) or 'transparent' (available). Please provide a value of type string.""",
    )  # noqa: E501

    visibility: Optional[Literal["default", "public", "private", "confidential"]] = Field(
        default="default",
        description="""Event visibility: 'default', 'public', 'private', or 'confidential'. Please provide a value of type string.""",
    )  # noqa: E501


class GooglecalendarCalendarListUpdateInput(BaseModel):
    """Input model for GOOGLECALENDAR_GOOGLECALENDAR_CALENDAR_LIST_UPDATE"""

    backgroundColor: Optional[str] = Field(
        default=None,
        description="""Hex color for calendar background. Please provide a value of type string.""",
    )  # noqa: E501

    calendar_id: str = Field(
        description="""Calendar identifier. Use "primary" for the primary calendar. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    colorId: Optional[str] = Field(
        default=None,
        description="""ID for calendar color from colors endpoint. Please provide a value of type string.""",
    )  # noqa: E501

    colorRgbFormat: Optional[bool] = Field(
        default=None,
        description="""Whether to use RGB for foreground/background colors. Please provide a value of type boolean.""",
    )  # noqa: E501

    defaultReminders: Optional[list[Any]] = Field(
        default=None, description="""List of default reminders."""
    )  # noqa: E501

    foregroundColor: Optional[str] = Field(
        default=None,
        description="""Hex color for calendar foreground. Please provide a value of type string.""",
    )  # noqa: E501

    hidden: Optional[bool] = Field(
        default=None,
        description="""Whether calendar is hidden. Please provide a value of type boolean.""",
    )  # noqa: E501

    notificationSettings: Optional[dict[str, Any]] = Field(
        default=None, description="""Notification settings for the calendar."""
    )  # noqa: E501

    selected: Optional[bool] = Field(
        default=None,
        description="""Whether calendar content shows in UI. Please provide a value of type boolean.""",
    )  # noqa: E501

    summaryOverride: Optional[str] = Field(
        default=None,
        description="""User-set summary for the calendar. Please provide a value of type string.""",
    )  # noqa: E501


class ClearCalendarInput(BaseModel):
    """Input model for GOOGLECALENDAR_CLEAR_CALENDAR"""

    calendar_id: str = Field(
        description="""Calendar identifier. To retrieve calendar IDs call the `calendarList.list` method. If you want to access the primary calendar of the currently logged in user, use the "`primary`" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class EventsListInput(BaseModel):
    """Input model for GOOGLECALENDAR_EVENTS_LIST"""

    alwaysIncludeEmail: Optional[bool] = Field(
        default=None,
        description="""Deprecated and ignored. Please provide a value of type boolean.""",
    )  # noqa: E501

    calendarId: str = Field(
        description="""Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you want to access the primary calendar of the currently logged in user, use the "primary" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    eventTypes: Optional[str] = Field(
        default=None,
        description="""Event types to return. Optional. This parameter can be repeated multiple times to return events of different types. If unset, returns all event types. Acceptable values are: "birthday", "default", "focusTime", "fromGmail", "outOfOffice", "workingLocation". Please provide a value of type string.""",
    )  # noqa: E501

    iCalUID: Optional[str] = Field(
        default=None,
        description="""Specifies an event ID in the iCalendar format to be provided in the response. Optional. Use this if you want to search for an event by its iCalendar ID. Please provide a value of type string.""",
    )  # noqa: E501

    maxAttendees: Optional[int] = Field(
        default=None,
        description="""The maximum number of attendees to include in the response. If there are more than the specified number of attendees, only the participant is returned. Optional. Please provide a value of type integer.""",
    )  # noqa: E501

    maxResults: Optional[int] = Field(
        default=None,
        description="""Maximum number of events returned on one result page. The number of events in the resulting page may be less than this value, or none at all, even if there are more events matching the query. Incomplete pages can be detected by a non-empty nextPageToken field in the response. By default the value is 250 events. The page size can never be larger than 2500 events. Optional. Please provide a value of type integer.""",
    )  # noqa: E501

    orderBy: Optional[str] = Field(
        default=None,
        description="""The order of the events returned in the result. Optional. The default is an unspecified, stable order. Acceptable values are: "startTime", "updated". Please provide a value of type string.""",
    )  # noqa: E501

    pageToken: Optional[str] = Field(
        default=None,
        description="""Token specifying which result page to return. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    privateExtendedProperty: Optional[str] = Field(
        default=None,
        description="""Extended properties constraint specified as propertyName=value. Matches only private properties. This parameter might be repeated multiple times to return events that match all given constraints. Please provide a value of type string.""",
    )  # noqa: E501

    q: Optional[str] = Field(
        default=None,
        description="""Free text search terms to find events that match these terms in various fields. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    sharedExtendedProperty: Optional[str] = Field(
        default=None,
        description="""Extended properties constraint specified as propertyName=value. Matches only shared properties. This parameter might be repeated multiple times to return events that match all given constraints. Please provide a value of type string.""",
    )  # noqa: E501

    showDeleted: Optional[bool] = Field(
        default=None,
        description="""Whether to include deleted events (with status equals "cancelled") in the result. Optional. The default is False. Please provide a value of type boolean.""",
    )  # noqa: E501

    showHiddenInvitations: Optional[bool] = Field(
        default=None,
        description="""Whether to include hidden invitations in the result. Optional. The default is False. Please provide a value of type boolean.""",
    )  # noqa: E501

    singleEvents: Optional[bool] = Field(
        default=None,
        description="""Whether to expand recurring events into instances and only return single one-off events and instances of recurring events. Optional. The default is False. Please provide a value of type boolean.""",
    )  # noqa: E501

    syncToken: Optional[str] = Field(
        default=None,
        description="""Token obtained from the nextSyncToken field returned on the last page of results from the previous list request. Optional. The default is to return all entries. Please provide a value of type string.""",
    )  # noqa: E501

    timeMax: Optional[str] = Field(
        default="2025-08-20T11:25:35.543745Z",
        description="""Upper bound (exclusive) for an event's start time to filter by. Optional. The default is not to filter by start time. Must be an RFC3339 timestamp with mandatory time zone offset, for example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z. Milliseconds may be provided but are ignored. If timeMin is set, timeMax must be greater than timeMin. Please provide a value of type string.""",
    )  # noqa: E501

    timeMin: Optional[str] = Field(
        default="2025-08-13T11:25:35.543771Z",
        description="""Lower bound (exclusive) for an event's end time to filter by. Optional. The default is not to filter by end time. Must be an RFC3339 timestamp with mandatory time zone offset, for example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z. Milliseconds may be provided but are ignored. If timeMax is set, timeMin must be smaller than timeMax. Please provide a value of type string.""",
    )  # noqa: E501

    timeZone: Optional[str] = Field(
        default=None,
        description="""Time zone used in the response. Optional. The default is the user's primary time zone. Please provide a value of type string.""",
    )  # noqa: E501

    updatedMin: Optional[str] = Field(
        default=None,
        description="""Lower bound for an event's last modification time (as a RFC3339 timestamp) to filter by. When specified, entries deleted since this time will always be included regardless of showDeleted. Optional. The default is not to filter by last modification time. Please provide a value of type string.""",
    )  # noqa: E501


class EventsMoveInput(BaseModel):
    """Input model for GOOGLECALENDAR_EVENTS_MOVE"""

    calendar_id: str = Field(
        description="""Calendar identifier of the source calendar. To retrieve calendar IDs call the calendarList.list method. If you want to access the primary calendar of the currently logged in user, use the "primary" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    destination: str = Field(
        description="""Calendar identifier of the destination calendar. To retrieve calendar IDs call the calendarList.list method. If you want to access the primary calendar of the currently logged in user, use the "primary" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    event_id: str = Field(
        description="""Event identifier. To retrieve event identifiers call the events.list method. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    send_updates: Optional[str] = Field(
        default=None,
        description="""Guests who should receive notifications about the change of the event's organizer. Acceptable values are: "all": Notifications are sent to all guests. "externalOnly": Notifications are sent to non-Google Calendar guests only. "none": No notifications are sent. This is the default value if left unspecified. Please provide a value of type string.""",
    )  # noqa: E501


class EventsWatchInput(BaseModel):
    """Input model for GOOGLECALENDAR_EVENTS_WATCH"""

    address: str = Field(
        description="""The address where notifications are delivered for this channel. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    calendarId: str = Field(
        description="""Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you want to access the primary calendar of the currently logged in user, use the "primary" keyword. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    id: str = Field(
        description="""A UUID or similar unique string that identifies this channel. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    params: Optional[dict[str, Any]] = Field(
        default=None,
        description="""Additional parameters controlling delivery channel behavior. Optional.""",
    )  # noqa: E501

    payload: Optional[bool] = Field(
        default=None,
        description="""A Boolean value to indicate whether payload is wanted. Optional. Please provide a value of type boolean.""",
    )  # noqa: E501

    token: Optional[str] = Field(
        default=None,
        description="""An arbitrary string delivered to the target address with each notification delivered over this channel. Optional. Please provide a value of type string.""",
    )  # noqa: E501

    type: Optional[str] = Field(
        default="web_hook",
        description="""The type of delivery mechanism used for this channel. Please provide a value of type string.""",
    )  # noqa: E501


class FindFreeSlotsInput(BaseModel):
    """Input model for GOOGLECALENDAR_FIND_FREE_SLOTS"""

    calendar_expansion_max: Optional[int] = Field(
        default=50,
        description="""Maximum calendars for which FreeBusy information is provided. Max allowed: 50. Please provide a value of type integer.""",
    )  # noqa: E501

    group_expansion_max: Optional[int] = Field(
        default=100,
        description="""Maximum calendar identifiers to return for a single group; exceeding this causes an error. Max allowed: 100. Please provide a value of type integer.""",
    )  # noqa: E501

    items: Optional[list[Any]] = Field(
        default=["primary"],
        description="""List of calendar identifiers (primary ID 'primary', user/calendar email, or unique calendar ID) to query for free/busy information.""",
    )  # noqa: E501

    time_max: Optional[str] = Field(
        default=None,
        description="""End datetime for the query interval. Accepts ISO, comma-separated, or simple datetime formats. Please provide a value of type string.""",
    )  # noqa: E501

    time_min: Optional[str] = Field(
        default=None,
        description="""Start datetime for the query interval. Accepts ISO, comma-separated, or simple datetime formats. Please provide a value of type string.""",
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default="UTC",
        description="""IANA timezone identifier (e.g., 'America/New_York', 'Europe/London') for interpreting `time_min` and `time_max` if they lack timezone info, and for expanding recurring events. Please provide a value of type string.""",
    )  # noqa: E501
