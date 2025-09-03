# This is a generated file by scripts/codegen/composio.py, do not edit manually
# ruff: noqa: E501  # Ignore line length issues in generated files
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class CreateAMeetingInput(BaseModel):
    """Input model for ZOOM_CREATE_A_MEETING"""

    agenda: Optional[str] = Field(
        default=None,
        description="""The meeting"s agenda. This value has a maximum length of 2,000 characters. . Please provide a value of type string.""",
    )  # noqa: E501

    default_password: Optional[bool] = Field(
        default=False,
        description="""Whether to generate a default passcode using the user"s settings. This value defaults to `false`.  If this value is `true` and the user has the PMI setting enabled with a passcode, then the user"s meetings will use the PMI passcode. It will **not** use a default passcode. . Please provide a value of type boolean.""",
    )  # noqa: E501

    duration: Optional[int] = Field(
        default=None,
        description="""The meeting"s scheduled duration, in minutes. This field is only used for scheduled meetings (`2`). . Please provide a value of type integer.""",
    )  # noqa: E501

    password: Optional[str] = Field(
        default=None,
        description="""The passcode required to join the meeting. By default, a passcode can **only** have a maximum length of 10 characters and only contain alphanumeric characters and the `@`, `-`, `_`, and `*` characters.  * If the account owner or administrator has configured [minimum passcode requirement settings](https://support.zoom.us/hc/en-us/articles/360033559832-Meeting-and-webinar-passwords#h_a427384b-e383-4f80-864d-794bf0a37604), the passcode **must** meet those requirements.  * If passcode requirements are enabled, use the [**Get user settings**](https://developers.zoom.us/docs/api-reference/zoom-api/methods#operation/userSettings) API or the [**Get account settings**](https://developers.zoom.us/docs/api-reference/zoom-api/ma#operation/accountSettings) API to get the requirements. . Please provide a value of type string.""",
    )  # noqa: E501

    pre_schedule: Optional[bool] = Field(
        default=False,
        description="""Whether to create a prescheduled meeting via the [GSuite app](https://support.zoom.us/hc/en-us/articles/360020187492-Zoom-for-GSuite-add-on). This **only** supports the meeting `type` value of `2` (scheduled meetings) and `3` (recurring meetings with no fixed time).  * `true` - Create a prescheduled meeting.  * `false` - Create a regular meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    recurrence__end__date__time: Optional[str] = Field(
        default=None,
        description="""Select the final date when the meeting will recur before it is canceled. Should be in UTC time, such as 2017-11-25T12:00:00Z. Cannot be used with `end_times`. . Please provide a value of type string.""",
    )  # noqa: E501

    recurrence__end__times: Optional[int] = Field(
        default=1,
        description="""Select how many times the meeting should recur before it is canceled. If `end_times` is set to 0, it means there is no end time. The maximum number of recurring is 60. Cannot be used with `end_date_time`. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__monthly__day: Optional[int] = Field(
        default=1,
        description="""Use this field **only if you"re scheduling a recurring meeting of type** `3` to state the day in a month when the meeting should recur. The value range is from 1 to 31. For the meeting to recur on 23rd of each month, provide `23` as this field"s value and `1` as the `repeat_interval` field"s value. Instead, if you would like the meeting to recur every three months, on 23rd of the month, change the value of the `repeat_interval` field to `3`. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__monthly__week: Optional[int] = Field(
        default=None,
        description="""Use this field **only if you"re scheduling a recurring meeting of type** `3` to state the week of the month when the meeting should recur. If you use this field, you must also use the `monthly_week_day` field to state the day of the week when the meeting should recur.     `-1` - Last week of the month.    `1` - First week of the month.    `2` - Second week of the month.    `3` - Third week of the month.    `4` - Fourth week of the month. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__monthly__week__day: Optional[int] = Field(
        default=None,
        description="""Use this field **only if you"re scheduling a recurring meeting of type** `3` to state a specific day in a week when the monthly meeting should recur. To use this field, you must also use the `monthly_week` field.      `1` - Sunday.    `2` - Monday.    `3` - Tuesday.    `4` -  Wednesday.    `5` - Thursday.    `6` - Friday.    `7` - Saturday. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__repeat__interval: Optional[int] = Field(
        default=None,
        description="""Define the interval when the meeting should recur. For instance, to schedule a meeting that recurs every two months, set this field"s value as `2` and the value of the `type` parameter as `3`.  For a daily meeting, the maximum interval you can set is `90` days. For a weekly meeting the maximum interval that you can set is  of `12` weeks. For a monthly meeting, there is a maximum of `3` months.  . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__type: Optional[int] = Field(
        default=2,
        description="""Recurrence meeting types.  `1` - Daily.    `2` - Weekly.    `3` - Monthly. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__weekly__days: Optional[Literal["1", "2", "3", "4", "5", "6", "7"]] = (
        Field(
            default="1",
            description="""This field is required if you"re scheduling a recurring meeting of type `2` to state the days of the week when the meeting should repeat.       The value for this field could be a number between `1` to `7` in string format. For instance, if the meeting should recur on Sunday, provide `1` as this field"s value.         **Note:** To set the meeting to occur on multiple days of a week, provide comma separated values for this field. For instance, if the meeting should recur on Sundays and Tuesdays, provide `1,3` as this field"s value.      `1` - Sunday.     `2` - Monday.    `3` - Tuesday.    `4` -  Wednesday.    `5` -  Thursday.    `6` - Friday.    `7` - Saturday. . Please provide a value of type string.""",
        )
    )  # noqa: E501

    schedule_for: Optional[str] = Field(
        default=None,
        description="""The email address or user ID of the user to schedule a meeting for. Please provide a value of type string.""",
    )  # noqa: E501

    settings__additional__data__center__regions: Optional[list[Any]] = Field(
        default=None,
        description="""Add additional meeting [data center regions](https://support.zoom.us/hc/en-us/articles/360042411451-Selecting-data-center-regions-for-hosted-meetings-and-webinars). Provide this value as an array of [country codes](https://developers.zoom.us/docs/api/rest/other-references/abbreviation-lists/#countries) for the countries available as data center regions in the [**Account Profile**](https://zoom.us/account/setting) interface but have been opted out of in the [user settings](https://zoom.us/profile). For example, the data center regions selected in your [**Account Profile**](https://zoom.us/account) are `Europe`, `Hong Kong SAR`, `Australia`, `India`, `Japan`, `China`, `United States`, and `Canada`. However, in the [**My Profile**](https://zoom.us/profile) settings, you did **not** select `India` and `Japan` for meeting and webinar traffic routing. To include `India` and `Japan` as additional data centers, use the `[IN, TY]` value for this field. """,
    )  # noqa: E501

    settings__allow__multiple__devices: Optional[bool] = Field(
        default=None,
        description="""Whether to allow attendees to join a meeting from multiple devices. This setting is only applied to meetings with registration enabled. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__alternative__host__update__polls: Optional[bool] = Field(
        default=None,
        description="""Whether the **Allow alternative hosts to add or edit polls** feature is enabled. This requires Zoom version 5.8.0 or higher. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__alternative__hosts: Optional[str] = Field(
        default=None,
        description="""A semicolon-separated list of the meeting"s alternative hosts" email addresses or IDs. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__alternative__hosts__email__notification: Optional[bool] = Field(
        default=True,
        description="""Whether to send email notifications to alternative hosts. This value defaults to `true`. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__approval__type: Optional[int] = Field(
        default=2,
        description="""Enable meeting registration approval. * `0` - Automatically approve registration. * `1` - Manually approve registration. * `2` - No registration required. This value defaults to `2`. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__approved__or__denied__countries__or__regions__approved__list: Optional[
        list[Any]
    ] = Field(default=None, description="""The list of approved countries or regions.""")  # noqa: E501

    settings__approved__or__denied__countries__or__regions__denied__list: Optional[
        list[Any]
    ] = Field(default=None, description="""The list of blocked countries or regions.""")  # noqa: E501

    settings__approved__or__denied__countries__or__regions__enable: Optional[bool] = (
        Field(
            default=None,
            description="""Whether to enable the [**Approve or block entry for users from specific countries/regions**](https://support.zoom.us/hc/en-us/articles/360060086231-Approve-or-block-entry-for-users-from-specific-countries-regions) setting. . Please provide a value of type boolean.""",
        )
    )  # noqa: E501

    settings__approved__or__denied__countries__or__regions__method: Optional[
        Literal["approve", "deny"]
    ] = Field(
        default=None,
        description="""Whether to allow or block users from specific countries or regions. * `approve` - Allow users from specific countries or regions to join the meeting. If you select this setting, include the approved countries or regions in the `approved_list` field.  * `deny` - Block users from specific countries or regions from joining the meeting. If you select this setting, include the blocked countries or regions in the `denied_list` field. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__audio: Optional[Literal["both", "telephony", "voip", "thirdParty"]] = Field(
        default="both",
        description="""How participants join the audio portion of the meeting. * `both` - Both telephony and VoIP.  * `telephony` - Telephony only.  * `voip` - VoIP only.  * `thirdParty` - Third party audio conference. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__audio__conference__info: Optional[str] = Field(
        default=None,
        description="""Third party audio conference info. Please provide a value of type string.""",
    )  # noqa: E501

    settings__authentication__domains: Optional[str] = Field(
        default=None,
        description="""The meeting"s authenticated domains. Only Zoom users whose email address contains an authenticated domain can join the meeting. Comma-separate multiple domains or use a wildcard for listing domains. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__authentication__exception: Optional[list[Any]] = Field(
        default=None,
        description="""A list of participants that can bypass meeting authentication. These participants will receive a unique meeting invite. """,
    )  # noqa: E501

    settings__authentication__option: Optional[str] = Field(
        default=None,
        description="""If the `meeting_authentication` value is `true`, the type of authentication required for users to join a meeting. To get this value, use the `authentication_options` array"s `id` value in the [**Get user settings**](https://developers.zoom.us/docs/api-reference/zoom-api/methods#operation/userSettings) API response. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__auto__recording: Optional[Literal["local", "cloud", "none"]] = Field(
        default="none",
        description="""The automatic recording settings.  * `local` - Record the meeting locally.  * `cloud` - Record the meeting to the cloud.  * `none` - Auto-recording disabled. This value defaults to `none`. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__auto__start__ai__companion__questions: Optional[bool] = Field(
        default=False,
        description="""Whether to automatically start AI Companion questions. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__auto__start__meeting__summary: Optional[bool] = Field(
        default=False,
        description="""Whether to automatically start a meeting summary. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__breakout__room__enable: Optional[bool] = Field(
        default=None,
        description="""Whether to enable the [**Breakout Room pre-assign**](https://support.zoom.us/hc/en-us/articles/360032752671-Pre-assigning-participants-to-breakout-rooms) option. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__breakout__room__rooms: Optional[list[Any]] = Field(
        default=None, description="""Information about the breakout rooms."""
    )  # noqa: E501

    settings__calendar__type: Optional[int] = Field(
        default=None,
        description="""Indicates the type of calendar integration used to schedule the meeting. * `1` - [Zoom Outlook add-in](https://support.zoom.us/hc/en-us/articles/360031592971-Getting-started-with-Outlook-plugin-and-add-in)  * `2` - [Zoom for Google Workspace add-on](https://support.zoom.us/hc/en-us/articles/360020187492-Using-the-Zoom-for-Google-Workspace-add-on) Works with the `private_meeting` field to determine whether to share details of meetings or not. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__close__registration: Optional[bool] = Field(
        default=False,
        description="""Whether to close registration after the event date. This value defaults to `false`. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__cn__meeting: Optional[bool] = Field(
        default=False,
        description="""Whether to host the meeting in China (CN). This value defaults to `false`. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__contact__email: Optional[str] = Field(
        default=None,
        description="""The contact email address for meeting registration. Please provide a value of type string.""",
    )  # noqa: E501

    settings__contact__name: Optional[str] = Field(
        default=None,
        description="""The contact name for meeting registration. Please provide a value of type string.""",
    )  # noqa: E501

    settings__continuous__meeting__chat__auto__add__invited__external__users: Optional[
        bool
    ] = Field(
        default=None,
        description="""Whether to enable the **Automatically add invited external users** setting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__continuous__meeting__chat__enable: Optional[bool] = Field(
        default=None,
        description="""Whether to enable the **Enable continuous meeting chat** setting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__email__notification: Optional[bool] = Field(
        default=True,
        description="""Whether to send email notifications to [alternative hosts](https://support.zoom.us/hc/en-us/articles/208220166) and [users with scheduling privileges](https://support.zoom.us/hc/en-us/articles/201362803-Scheduling-privilege). This value defaults to `true`. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__encryption__type: Optional[Literal["enhanced_encryption", "e2ee"]] = Field(
        default=None,
        description="""The type of [end-to-end (E2EE) encryption](https://support.zoom.us/hc/en-us/articles/360048660871) to use for the meeting.  * `enhanced_encryption` - Enhanced encryption. Encryption is stored in the cloud when you enable this option.  * `e2ee` - End-to-end encryption. The encryption key is stored on your local device and **cannot** be obtained by anyone else. When you use E2EE encryption, [certain features](https://support.zoom.us/hc/en-us/articles/360048660871), such as cloud recording or phone and SIP/H.323 dial-in, are **disabled**. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__focus__mode: Optional[bool] = Field(
        default=None,
        description="""Whether to enable the [**Focus Mode** feature](https://support.zoom.us/hc/en-us/articles/360061113751-Using-focus-mode) when the meeting starts. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__global__dial__in__countries: Optional[list[Any]] = Field(
        default=None, description="""A list of available global dial-in countries."""
    )  # noqa: E501

    settings__host__save__video__order: Optional[bool] = Field(
        default=None,
        description="""Whether the **Allow host to save video order** feature is enabled. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__host__video: Optional[bool] = Field(
        default=None,
        description="""Whether to start meetings with the host video on. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__in__meeting: Optional[bool] = Field(
        default=False,
        description="""Whether to host the meeting in India (IN). This value defaults to `false`. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__internal__meeting: Optional[bool] = Field(
        default=False,
        description="""Whether to set the meeting as an internal meeting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__jbh__time: Optional[int] = Field(
        default=None,
        description="""If the value of the `join_before_host` field is `true`, this field indicates the time limits when a participant can join a meeting before the meeting"s host. * `0` - Allow the participant to join the meeting at anytime. * `5` - Allow the participant to join 5 minutes before the meeting"s start time. * `10` - Allow the participant to join 10 minutes before the meeting"s start time. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__join__before__host: Optional[bool] = Field(
        default=False,
        description="""Whether participants can join the meeting before its host. This field is only used for scheduled meetings (`2`) or recurring meetings (`3` and `8`). This value defaults to `false`. If the [**Waiting Room** feature](https://support.zoom.us/hc/en-us/articles/115000332726-Waiting-Room) is enabled, this setting is **disabled**. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__language__interpretation__enable: Optional[bool] = Field(
        default=None,
        description="""Whether to enable [language interpretation](https://support.zoom.us/hc/en-us/articles/360034919791-Language-interpretation-in-meetings-and-webinars) for the meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__language__interpretation__interpreters: Optional[list[Any]] = Field(
        default=None,
        description="""Information about the meeting"s language interpreters.""",
    )  # noqa: E501

    settings__meeting__authentication: Optional[bool] = Field(
        default=None,
        description="""If true, only [authenticated](https://support.zoom.us/hc/en-us/articles/360037117472-Authentication-Profiles-for-Meetings-and-Webinars) users can join the meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__meeting__invitees: Optional[list[Any]] = Field(
        default=None, description="""A list of the meeting"s invitees."""
    )  # noqa: E501

    settings__mute__upon__entry: Optional[bool] = Field(
        default=False,
        description="""Whether to mute participants upon entry. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__participant__focused__meeting: Optional[bool] = Field(
        default=False,
        description="""Whether to set the meeting as a participant focused meeting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__participant__video: Optional[bool] = Field(
        default=None,
        description="""Whether to start meetings with the participant video on. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__private__meeting: Optional[bool] = Field(
        default=None,
        description="""Whether to set the meeting as private. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__push__change__to__calendar: Optional[bool] = Field(
        default=False,
        description="""Whether to push meeting changes to the calendar.   To enable this feature, configure the **Configure Calendar and Contacts Service** in the user"s profile page of the Zoom web portal and enable the **Automatically sync Zoom calendar events information bi-directionally between Zoom and integrated calendars.** setting in the **Settings** page of the Zoom web portal. * `true` - Push meeting changes to the calendar. * `false` - Do not push meeting changes to the calendar. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__registrants__confirmation__email: Optional[bool] = Field(
        default=None,
        description="""Whether to send registrants an email confirmation.  * `true` - Send a confirmation email.  * `false` - Do not send a confirmation email. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__registrants__email__notification: Optional[bool] = Field(
        default=None,
        description="""Whether to send registrants email notifications about their registration approval, cancellation, or rejection. * `true` - Send an email notification. * `false` - Do not send an email notification.  Set this value to `true` to also use the `registrants_confirmation_email` parameter. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__registration__type: Optional[int] = Field(
        default=1,
        description="""The meeting"s registration type.  * `1` - Attendees register once and can attend any meeting occurrence.  * `2` - Attendees must register for each meeting occurrence.  * `3` - Attendees register once and can select one or more meeting occurrences to attend. This field is only for recurring meetings with fixed times (`8`). This value defaults to `1`. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__resources: Optional[list[Any]] = Field(
        default=None, description="""The meeting"s resources."""
    )  # noqa: E501

    settings__show__share__button: Optional[bool] = Field(
        default=None,
        description="""Whether to include social media sharing buttons on the meeting"s registration page. This setting is only applied to meetings with registration enabled. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__sign__language__interpretation__enable: Optional[bool] = Field(
        default=None,
        description="""Whether to enable [sign language interpretation](https://support.zoom.us/hc/en-us/articles/9644962487309-Using-sign-language-interpretation-in-a-meeting-or-webinar) for the meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__sign__language__interpretation__interpreters: Optional[list[Any]] = Field(
        default=None,
        description="""Information about the meeting"s sign language interpreters.""",
    )  # noqa: E501

    settings__use__pmi: Optional[bool] = Field(
        default=False,
        description="""Whether to use a [Personal Meeting ID (PMI)](https://developers.zoom.us/docs/api/rest/using-zoom-apis/#understanding-personal-meeting-id-pmi) instead of a generated meeting ID. This field is only used for scheduled meetings (`2`), instant meetings (`1`), or recurring meetings with no fixed time (`3`). This value defaults to `false`. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__waiting__room: Optional[bool] = Field(
        default=None,
        description="""Whether to enable the [**Waiting Room** feature](https://support.zoom.us/hc/en-us/articles/115000332726-Waiting-Room). If this value is `true`, this **disables** the `join_before_host` setting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__watermark: Optional[bool] = Field(
        default=False,
        description="""Whether to add a watermark when viewing a shared screen. Please provide a value of type boolean.""",
    )  # noqa: E501

    start_time: Optional[str] = Field(
        default=None,
        description="""The meeting"s start time. This field is only used for scheduled or recurring meetings with a fixed time. This supports local time and GMT formats.  * To set a meeting"s start time in GMT, use the `yyyy-MM-ddTHH:mm:ssZ` date-time format. For example, `2020-03-31T12:02:00Z`.  * To set a meeting"s start time using a specific timezone, use the `yyyy-MM-ddTHH:mm:ss` date-time format and specify the [timezone ID](https://developers.zoom.us/docs/api/rest/other-references/abbreviation-lists/#timezones) in the `timezone` field. If you do not specify a timezone, the `timezone` value defaults to your Zoom account"s timezone. You can also use `UTC` for the `timezone` value. **Note:** If no `start_time` is set for a scheduled meeting, the `start_time` is set at the current time and the meeting type changes to an instant meeting, which expires after 30 days. . Please provide a value of type string.""",
    )  # noqa: E501

    template_id: Optional[str] = Field(
        default=None,
        description="""The account admin meeting template ID used to schedule a meeting using a [meeting template](https://support.zoom.us/hc/en-us/articles/360036559151-Meeting-templates). For a list of account admin-provided meeting templates, use the [**List meeting templates**](https://developers.zoom.us/docs/api-reference/zoom-api/methods#operation/listMeetingTemplates) API.  * At this time, this field **only** accepts account admin meeting template IDs.  * To enable the account admin meeting templates feature, [contact Zoom support](https://support.zoom.us/hc/en-us). . Please provide a value of type string.""",
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default=None,
        description="""The timezone to assign to the `start_time` value. This field is only used for scheduled or recurring meetings with a fixed time. For a list of supported timezones and their formats, see our [timezone list](https://developers.zoom.us/docs/api/rest/other-references/abbreviation-lists/#timezones). . Please provide a value of type string.""",
    )  # noqa: E501

    topic: Optional[str] = Field(
        default=None,
        description="""The meeting"s topic. Please provide a value of type string.""",
    )  # noqa: E501

    tracking_fields: Optional[list[Any]] = Field(
        default=None, description="""Information about the meeting"s tracking fields."""
    )  # noqa: E501

    type: Optional[int] = Field(
        default=2,
        description="""The type of meeting. * `1` - An instant meeting.  * `2` - A scheduled meeting.  * `3` - A recurring meeting with no fixed time.  * `8` - A recurring meeting with fixed time. . Please provide a value of type integer.""",
    )  # noqa: E501

    userId: str = Field(
        description="""The user"s user ID or email address. For user-level apps, pass the `me` value. . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class GetAMeetingInput(BaseModel):
    """Input model for ZOOM_GET_A_MEETING"""

    meetingId: int = Field(
        description="""The meeting"s ID.   When storing this value in your database, store it as a long format integer and **not** an integer. Meeting IDs can be more than 10 digits. . Please provide a value of type integer. This parameter is required."""
    )  # noqa: E501

    occurrence_id: Optional[str] = Field(
        default=None,
        description="""Meeting occurrence ID. Provide this field to view meeting details of a particular occurrence of the [recurring meeting](https://support.zoom.us/hc/en-us/articles/214973206-Scheduling-Recurring-Meetings). . Please provide a value of type string.""",
    )  # noqa: E501

    show_previous_occurrences: Optional[bool] = Field(
        default=None,
        description="""Set this field"s value to `true` to view meeting details of all previous occurrences of a [recurring meeting](https://support.zoom.us/hc/en-us/articles/214973206-Scheduling-Recurring-Meetings).  . Please provide a value of type boolean.""",
    )  # noqa: E501


class GetAMeetingSummaryInput(BaseModel):
    """Input model for ZOOM_GET_A_MEETING_SUMMARY"""

    meetingId: str = Field(
        description="""The meeting"s universally unique ID (UUID). When you provide a meeting UUID that begins with a `/` character or contains the `//` characters, you **must** double-encode the meeting UUID before making an API request. . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class GetMeetingRecordingsInput(BaseModel):
    """Input model for ZOOM_GET_MEETING_RECORDINGS"""

    include_fields: Optional[str] = Field(
        default=None,
        description="""The `download_access_token` value for downloading the meeting"s recordings. . Please provide a value of type string.""",
    )  # noqa: E501

    meetingId: str = Field(
        description="""To get a meeting"s cloud recordings, provide the meeting ID or UUID. If providing the meeting ID instead of UUID, the response will be for the latest meeting instance.  To get a webinar"s cloud recordings, provide the webinar"s ID or UUID. If providing the webinar ID instead of UUID, the response will be for the latest webinar instance.  If a UUID starts with `/` or contains `//` (example: `/ajXp112QmuoKj4854875==`), **[double encode](https://developers.zoom.us) the UUID** before making an API request.  . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    ttl: Optional[int] = Field(
        default=None,
        description="""The `download_access_token` Time to Live (TTL) value. This parameter is only valid if the `include_fields` query parameter contains the `download_access_token` value. . Please provide a value of type integer.""",
    )  # noqa: E501


class ListAllRecordingsInput(BaseModel):
    """Input model for ZOOM_LIST_ALL_RECORDINGS"""

    from_: Optional[str] = Field(
        default=None,
        alias="from",
        description="""The start date in "yyyy-mm-dd" UTC format for the date range where you would like to retrieve recordings. The maximum range can be a month. If no value is provided for this field, the default will be current date.  For example, if you make the API request on June 30, 2020, without providing the `from` and `to` parameters, by default the value of "from" field will be `2020-06-30` and the value of the "to" field will be `2020-07-01`.  **Note**: The `trash` files cannot be filtered by date range and thus, the `from` and `to` fields should not be used for trash files. . Please provide a value of type string.""",
    )  # noqa: E501

    mc: Optional[str] = Field(
        default="false",
        description="""The query metadata of the recording if using an on-premise meeting connector for the meeting. . Please provide a value of type string.""",
    )  # noqa: E501

    meeting_id: Optional[int] = Field(
        default=None,
        description="""The meeting ID. Please provide a value of type integer.""",
    )  # noqa: E501

    next_page_token: Optional[str] = Field(
        default=None,
        description="""The next page token paginates through a large set of results. A next page token returns whenever the set of available results exceeds the current page size. The expiration period for this token is 15 minutes. . Please provide a value of type string.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=30,
        description="""The number of records returned within a single API call. Please provide a value of type integer.""",
    )  # noqa: E501

    to_: Optional[str] = Field(
        default=None,
        alias="to",
        description="""The end date in "yyyy-mm-dd" "yyyy-mm-dd" UTC format. . Please provide a value of type string.""",
    )  # noqa: E501

    trash: Optional[bool] = Field(
        default=False,
        description="""The query trash. * `true` - List recordings from trash.   * `false` - Do not list recordings from the trash.   The default value is `false`. If you set it to `true`, you can use the `trash_type` property to indicate the type of Cloud recording that you need to retrieve.  . Please provide a value of type boolean.""",
    )  # noqa: E501

    trash_type: Optional[str] = Field(
        default="meeting_recordings",
        description="""The type of cloud recording to retrieve from the trash.     *   `meeting_recordings`: List all meeting recordings from the trash.    *  `recording_file`: List all individual recording files from the trash.  . Please provide a value of type string.""",
    )  # noqa: E501

    userId: str = Field(
        description="""The user"s ID or email address. For user-level apps, pass the `me` value. . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class ListMeetingsInput(BaseModel):
    """Input model for ZOOM_LIST_MEETINGS"""

    from_: Optional[str] = Field(
        default=None,
        alias="from",
        description="""The start date. Please provide a value of type string.""",
    )  # noqa: E501

    next_page_token: Optional[str] = Field(
        default=None,
        description="""Use the next page token to paginate through large result sets. A next page token is returned whenever the set of available results exceeds the current page size. This token"s expiration period is 15 minutes. . Please provide a value of type string.""",
    )  # noqa: E501

    page_number: Optional[int] = Field(
        default=None,
        description="""The page number of the current page in the returned records. Please provide a value of type integer.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=30,
        description="""The number of records returned within a single API call. Please provide a value of type integer.""",
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default=None,
        description="""The timezone to assign to the `from` and `to` value. For a list of supported timezones and their formats, see our [timezone list](https://developers.zoom.us/docs/api/rest/other-references/abbreviation-lists/#timezones). . Please provide a value of type string.""",
    )  # noqa: E501

    to_: Optional[str] = Field(
        default=None,
        alias="to",
        description="""The end date. Please provide a value of type string.""",
    )  # noqa: E501

    type: Optional[
        Literal["scheduled", "live", "upcoming", "upcoming_meetings", "previous_meetings"]
    ] = Field(
        default="scheduled",
        description="""The type of meeting.  * `scheduled` - All valid previous (unexpired) meetings, live meetings, and upcoming scheduled meetings.  * `live` - All the ongoing meetings.  * `upcoming` - All upcoming meetings, including live meetings.  * `upcoming_meetings` - All upcoming meetings, including live meetings.  * `previous_meetings` - All the previous meetings. . Please provide a value of type string.""",
    )  # noqa: E501

    userId: str = Field(
        description="""The user"s user ID or email address. For user-level apps, pass the `me` value. . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class AddAMeetingRegistrantInput(BaseModel):
    """Input model for ZOOM_ADD_A_MEETING_REGISTRANT"""

    address: Optional[str] = Field(
        default=None,
        description="""The registrant"s address. Please provide a value of type string.""",
    )  # noqa: E501

    auto_approve: Optional[bool] = Field(
        default=None,
        description="""If a meeting was scheduled with the `approval_type` field value of `1` (manual approval) but you want to automatically approve meeting registrants, set the value of this field to `true`.  **Note:** You cannot use this field to change approval setting for a meeting originally scheduled with the `approval_type` field value of `0` (automatic approval). . Please provide a value of type boolean.""",
    )  # noqa: E501

    city: Optional[str] = Field(
        default=None,
        description="""The registrant"s city. Please provide a value of type string.""",
    )  # noqa: E501

    comments: Optional[str] = Field(
        default=None,
        description="""The registrant"s questions and comments. Please provide a value of type string.""",
    )  # noqa: E501

    country: Optional[str] = Field(
        default=None,
        description="""The registrant"s two-letter [country code](https://marketplace.zoom.us/docs/api-reference/other-references/abbreviation-lists#countries). . Please provide a value of type string.""",
    )  # noqa: E501

    custom_questions: Optional[list[Any]] = Field(
        default=None, description="""Information about custom questions."""
    )  # noqa: E501

    email: str = Field(
        description="""The registrant"s email address. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    first_name: str = Field(
        description="""The registrant"s first name. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    industry: Optional[str] = Field(
        default=None,
        description="""The registrant"s industry. Please provide a value of type string.""",
    )  # noqa: E501

    job_title: Optional[str] = Field(
        default=None,
        description="""The registrant"s job title. Please provide a value of type string.""",
    )  # noqa: E501

    language: Optional[
        Literal[
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
    ] = Field(
        default=None,
        description="""The registrant"s language preference for confirmation emails:  * `en-US` &mdash; English (US)  * `de-DE` &mdash; German (Germany)  * `es-ES` &mdash; Spanish (Spain)  * `fr-FR` &mdash; French (France)  * `jp-JP` &mdash; Japanese  * `pt-PT` &mdash; Portuguese (Portugal)  * `ru-RU` &mdash; Russian  * `zh-CN` &mdash; Chinese (PRC)  * `zh-TW` &mdash; Chinese (Taiwan)  * `ko-KO` &mdash; Korean  * `it-IT` &mdash; Italian (Italy)  * `vi-VN` &mdash; Vietnamese  * `pl-PL` &mdash; Polish  * `Tr-TR` &mdash; Turkish . Please provide a value of type string.""",
    )  # noqa: E501

    last_name: Optional[str] = Field(
        default=None,
        description="""The registrant"s last name. Please provide a value of type string.""",
    )  # noqa: E501

    meetingId: int = Field(
        description="""The meeting"s ID.   When storing this value in your database, you must store it as a long format integer and **not** an integer. Meeting IDs can exceed 10 digits. . Please provide a value of type integer. This parameter is required."""
    )  # noqa: E501

    no_of_employees: Optional[
        Literal[
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
    ] = Field(
        default=None,
        description="""The registrant"s number of employees:  * `1-20`  * `21-50`  * `51-100`  * `101-500`  * `500-1,000`  * `1,001-5,000`  * `5,001-10,000`  * `More than 10,000` . Please provide a value of type string.""",
    )  # noqa: E501

    occurrence_ids: Optional[str] = Field(
        default=None,
        description="""A comma-separated list of meeting occurrence IDs. You can get this value with the [Get a meeting](https://developers.zoom.us) API. . Please provide a value of type string.""",
    )  # noqa: E501

    org: Optional[str] = Field(
        default=None,
        description="""The registrant"s organization. Please provide a value of type string.""",
    )  # noqa: E501

    phone: Optional[str] = Field(
        default=None,
        description="""The registrant"s phone number. Please provide a value of type string.""",
    )  # noqa: E501

    purchasing_time_frame: Optional[
        Literal[
            "",
            "Within a month",
            "1-3 months",
            "4-6 months",
            "More than 6 months",
            "No timeframe",
        ]
    ] = Field(
        default=None,
        description="""The registrant"s purchasing time frame:  * `Within a month`  * `1-3 months`  * `4-6 months`  * `More than 6 months`  * `No timeframe` . Please provide a value of type string.""",
    )  # noqa: E501

    role_in_purchase_process: Optional[
        Literal[
            "", "Decision Maker", "Evaluator/Recommender", "Influencer", "Not involved"
        ]
    ] = Field(
        default=None,
        description="""The registrant"s role in the purchase process:  * `Decision Maker`  * `Evaluator/Recommender`  * `Influencer`  * `Not involved` . Please provide a value of type string.""",
    )  # noqa: E501

    state: Optional[str] = Field(
        default=None,
        description="""The registrant"s state or province. Please provide a value of type string.""",
    )  # noqa: E501

    zip: Optional[str] = Field(
        default=None,
        description="""The registrant"s ZIP or postal code. Please provide a value of type string.""",
    )  # noqa: E501


class AddAWebinarRegistrantInput(BaseModel):
    """Input model for ZOOM_ADD_A_WEBINAR_REGISTRANT"""

    address: Optional[str] = Field(
        default=None,
        description="""The registrant"s address. Please provide a value of type string.""",
    )  # noqa: E501

    city: Optional[str] = Field(
        default=None,
        description="""The registrant"s city. Please provide a value of type string.""",
    )  # noqa: E501

    comments: Optional[str] = Field(
        default=None,
        description="""The registrant"s questions and comments. Please provide a value of type string.""",
    )  # noqa: E501

    country: Optional[str] = Field(
        default=None,
        description="""The registrant"s two-letter [country code](https://developers.zoom.us/docs/api/rest/other-references/abbreviation-lists/#countries). . Please provide a value of type string.""",
    )  # noqa: E501

    custom_questions: Optional[list[Any]] = Field(
        default=None, description="""Information about custom questions."""
    )  # noqa: E501

    email: str = Field(
        description="""The registrant"s email address. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    first_name: str = Field(
        description="""The registrant"s first name. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    industry: Optional[str] = Field(
        default=None,
        description="""The registrant"s industry. Please provide a value of type string.""",
    )  # noqa: E501

    job_title: Optional[str] = Field(
        default=None,
        description="""The registrant"s job title. Please provide a value of type string.""",
    )  # noqa: E501

    language: Optional[
        Literal[
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
    ] = Field(
        default=None,
        description="""The registrant"s language preference for confirmation emails:  * `en-US` - English (US)  * `de-DE` - German (Germany)  * `es-ES` - Spanish (Spain)  * `fr-FR` - French (France)  * `jp-JP` - Japanese  * `pt-PT` - Portuguese (Portugal)  * `ru-RU` - Russian  * `zh-CN` - Chinese (PRC)  * `zh-TW` - Chinese (Taiwan)  * `ko-KO` - Korean  * `it-IT` - Italian (Italy)  * `vi-VN` - Vietnamese  * `pl-PL` - Polish  * `Tr-TR` - Turkish . Please provide a value of type string.""",
    )  # noqa: E501

    last_name: Optional[str] = Field(
        default=None,
        description="""The registrant"s last name. Please provide a value of type string.""",
    )  # noqa: E501

    no_of_employees: Optional[
        Literal[
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
    ] = Field(
        default=None,
        description="""The registrant"s number of employees:  * `1-20`  * `21-50`  * `51-100`  * `101-500`  * `500-1,000`  * `1,001-5,000`  * `5,001-10,000`  * `More than 10,000` . Please provide a value of type string.""",
    )  # noqa: E501

    occurrence_ids: Optional[str] = Field(
        default=None,
        description="""A comma-separated list of webinar occurrence IDs. Get this value with the [Get a webinar](https://developers.zoom.us) API. Make sure the `registration_type` is 3 if updating multiple occurrences with this API. . Please provide a value of type string.""",
    )  # noqa: E501

    org: Optional[str] = Field(
        default=None,
        description="""The registrant"s organization. Please provide a value of type string.""",
    )  # noqa: E501

    phone: Optional[str] = Field(
        default=None,
        description="""The registrant"s phone number. Please provide a value of type string.""",
    )  # noqa: E501

    purchasing_time_frame: Optional[
        Literal[
            "",
            "Within a month",
            "1-3 months",
            "4-6 months",
            "More than 6 months",
            "No timeframe",
        ]
    ] = Field(
        default=None,
        description="""The registrant"s purchasing time frame:  * `Within a month`  * `1-3 months`  * `4-6 months`  * `More than 6 months`  * `No timeframe` . Please provide a value of type string.""",
    )  # noqa: E501

    role_in_purchase_process: Optional[
        Literal[
            "", "Decision Maker", "Evaluator/Recommender", "Influencer", "Not involved"
        ]
    ] = Field(
        default=None,
        description="""The registrant"s role in the purchase process:  * `Decision Maker`  * `Evaluator/Recommender`  * `Influencer`  * `Not involved` . Please provide a value of type string.""",
    )  # noqa: E501

    source_id: Optional[str] = Field(
        default=None,
        description="""The tracking source"s unique identifier. Please provide a value of type string.""",
    )  # noqa: E501

    state: Optional[str] = Field(
        default=None,
        description="""The registrant"s state or province. Please provide a value of type string.""",
    )  # noqa: E501

    webinarId: int = Field(
        description="""The webinar"s ID. Please provide a value of type integer. This parameter is required."""
    )  # noqa: E501

    zip: Optional[str] = Field(
        default=None,
        description="""The registrant"s ZIP or postal code. Please provide a value of type string.""",
    )  # noqa: E501


class DeleteMeetingRecordingsInput(BaseModel):
    """Input model for ZOOM_DELETE_MEETING_RECORDINGS"""

    action: Optional[Literal["trash", "delete"]] = Field(
        default="trash",
        description="""The recording delete actions:    `trash` - Move recording to trash.    `delete` - Delete recording permanently. . Please provide a value of type string.""",
    )  # noqa: E501

    meetingId: str = Field(
        description="""To get Cloud Recordings of a meeting, provide the meeting ID or meeting UUID. If the meeting ID is provided instead of UUID,the response will be for the latest meeting instance.  To get Cloud Recordings of a webinar, provide the webinar ID or the webinar UUID. If the webinar ID is provided instead of UUID,the response will be for the latest webinar instance.  If a UUID starts with &quot;/&quot; or contains &quot;//&quot; (example: &quot;/ajXp112QmuoKj4854875==&quot;), you must **[double encode](https://marketplace.zoom.us/docs/api-reference/using-zoom-apis/#meeting-id-and-uuid)** the UUID before making an API request.  . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class GetAWebinarInput(BaseModel):
    """Input model for ZOOM_GET_A_WEBINAR"""

    occurrence_id: Optional[str] = Field(
        default=None,
        description="""Unique identifier for an occurrence of a recurring webinar. [Recurring webinars](https://support.zoom.us/hc/en-us/articles/216354763-How-to-Schedule-A-Recurring-Webinar) can have a maximum of 50 occurrences. When you create a recurring Webinar using [**Create a webinar**](https://developers.zoom.us) API, you can retrieve the Occurrence ID from the response of the API call. . Please provide a value of type string.""",
    )  # noqa: E501

    show_previous_occurrences: Optional[bool] = Field(
        default=None,
        description="""Set the value of this field to `true` if you would like to view Webinar details of all previous occurrences of a recurring Webinar. . Please provide a value of type boolean.""",
    )  # noqa: E501

    webinarId: str = Field(
        description="""The webinar"s ID or universally unique ID (UUID). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class GetDailyUsageReportInput(BaseModel):
    """Input model for ZOOM_GET_DAILY_USAGE_REPORT"""

    group_id: Optional[str] = Field(
        default=None,
        description="""The group ID. To get a group ID, use the [**List groups**](https://developers.zoom.us) API.   **Note:** The API response will only contain users who are members of the queried group ID. . Please provide a value of type string.""",
    )  # noqa: E501

    month: Optional[int] = Field(
        default=None,
        description="""Month for this report. Please provide a value of type integer.""",
    )  # noqa: E501

    year: Optional[int] = Field(
        default=None,
        description="""Year for this report. Please provide a value of type integer.""",
    )  # noqa: E501


class GetPastMeetingParticipantsInput(BaseModel):
    """Input model for ZOOM_GET_PAST_MEETING_PARTICIPANTS"""

    meetingId: str = Field(
        description="""The meeting"s ID or universally unique ID (UUID).  * If you provide a meeting ID, the API will return a response for the latest meeting instance.  * If you provide a meeting UUID that begins with a `/` character or contains the `//` characters, you **must** double-encode the meeting UUID before making an API request. . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    next_page_token: Optional[str] = Field(
        default=None,
        description="""Use the next page token to paginate through large result sets. A next page token is returned whenever the set of available results exceeds the current page size. This token"s expiration period is 15 minutes. . Please provide a value of type string.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=30,
        description="""The number of records returned within a single API call. Please provide a value of type integer.""",
    )  # noqa: E501


class ListArchivedFilesInput(BaseModel):
    """Input model for ZOOM_LIST_ARCHIVED_FILES"""

    from_: Optional[str] = Field(
        default=None,
        alias="from",
        description="""The query start date, in `yyyy-MM-dd"T"HH:mm:ssZ` format. This value and the `to` query parameter value cannot exceed seven days. . Please provide a value of type string.""",
    )  # noqa: E501

    group_id: Optional[str] = Field(
        default=None,
        description="""The group ID. To get a group ID, use the [List groups](https://developers.zoom.us/docs/api/rest/reference/scim-api/methods/#operation/groupSCIM2List) API. . Please provide a value of type string.""",
    )  # noqa: E501

    next_page_token: Optional[str] = Field(
        default=None,
        description="""Use the next page token to paginate through large result sets. A next page token is returned whenever the set of available results exceeds the current page size. This token"s expiration period is 15 minutes. . Please provide a value of type string.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=30,
        description="""The number of records returned within a single API call. Please provide a value of type integer.""",
    )  # noqa: E501

    query_date_type: Optional[Literal["meeting_start_time", "archive_complete_time"]] = (
        Field(
            default="meeting_start_time",
            description="""The type of query date. * `meeting_start_time`  * `archive_complete_time`   This value defaults to `meeting_start_time`. . Please provide a value of type string.""",
        )
    )  # noqa: E501

    to_: Optional[str] = Field(
        default=None,
        alias="to",
        description="""The query end date, in `yyyy-MM-dd"T"HH:mm:ssZ` format. This value and the `from` query parameter value cannot exceed seven days. . Please provide a value of type string.""",
    )  # noqa: E501


class ListDevicesInput(BaseModel):
    """Input model for ZOOM_LIST_DEVICES"""

    device_model: Optional[str] = Field(
        default=None,
        description="""Filter devices by model. Please provide a value of type string.""",
    )  # noqa: E501

    device_status: Optional[int] = Field(
        default=-1,
        description="""Filter devices by status.      Device Status:    `0` - offline.    `1` - online.    `-1` - unlink . Please provide a value of type integer.""",
    )  # noqa: E501

    device_type: Optional[int] = Field(
        default=-1,
        description="""Filter devices by device type.     Device Type:    `-1` - All Zoom Room device(0,1,2,3,4,6).    `0` - Zoom Rooms Computer.    `1` - Zoom Rooms Controller.    `2` - Zoom Rooms Scheduling Display.    `3` - Zoom Rooms Control System.    `4` -  Zoom Rooms Whiteboard.    `5` - Zoom Phone Appliance.    `6` - Zoom Rooms Computer (with Controller). . Please provide a value of type integer.""",
    )  # noqa: E501

    device_vendor: Optional[str] = Field(
        default=None,
        description="""Filter devices by vendor. Please provide a value of type string.""",
    )  # noqa: E501

    is_enrolled_in_zdm: Optional[bool] = Field(
        default=True,
        description="""Filter devices by enrollment of ZDM (Zoom Device Management). Please provide a value of type boolean.""",
    )  # noqa: E501

    next_page_token: Optional[str] = Field(
        default=None,
        description="""Use the next page token to paginate through large result sets. A next page token is returned whenever the set of available results exceeds the current page size. This token"s expiration period is 15 minutes. . Please provide a value of type string.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=30,
        description="""The number of records returned within a single API call. Please provide a value of type integer.""",
    )  # noqa: E501

    platform_os: Optional[Literal["win", "mac", "ipad", "iphone", "android", "linux"]] = (
        Field(
            default=None,
            description="""Filter devices by platform operating system. Please provide a value of type string.""",
        )
    )  # noqa: E501

    search_text: Optional[str] = Field(
        default=None,
        description="""Filter devices by name or serial number. Please provide a value of type string.""",
    )  # noqa: E501


class ListWebinarsInput(BaseModel):
    """Input model for ZOOM_LIST_WEBINARS"""

    page_number: Optional[int] = Field(
        default=1,
        description="""**Deprecated** We will no longer support this field in a future release. Instead, use the `next_page_token` for pagination. . Please provide a value of type integer.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=30,
        description="""The number of records returned within a single API call. Please provide a value of type integer.""",
    )  # noqa: E501

    type: Optional[Literal["scheduled", "upcoming"]] = Field(
        default="scheduled",
        description="""The type of webinar.  * `scheduled` - All valid previous (unexpired) webinars, live webinars, and upcoming scheduled webinars.  * `upcoming` - All upcoming webinars, including live webinars. . Please provide a value of type string.""",
    )  # noqa: E501

    userId: str = Field(
        description="""The user"s user ID or email address. For user-level apps, pass the `me` value. . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class ListWebinarParticipantsInput(BaseModel):
    """Input model for ZOOM_LIST_WEBINAR_PARTICIPANTS"""

    next_page_token: Optional[str] = Field(
        default=None,
        description="""Use the next page token to paginate through large result sets. A next page token is returned whenever the set of available results exceeds the current page size. This token"s expiration period is 15 minutes. . Please provide a value of type string.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=30,
        description="""The number of records returned within a single API call. Please provide a value of type integer.""",
    )  # noqa: E501

    webinarId: str = Field(
        description="""The webinar"s ID or universally unique ID (UUID).  * If you provide a webinar ID, the API returns a response for the latest webinar instance.  * If you provide a webinar UUID that begins with a `/` character or contains the `//` characters, you **must** [double encode](https://developers.zoom.us/docs/api/rest/using-zoom-apis/#meeting-id-and-uuid) the webinar UUID before making an API request. . Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class UpdateAMeetingInput(BaseModel):
    """Input model for ZOOM_UPDATE_A_MEETING"""

    agenda: Optional[str] = Field(
        default=None,
        description="""Meeting description. Please provide a value of type string.""",
    )  # noqa: E501

    duration: Optional[int] = Field(
        default=None,
        description="""Meeting duration in minutes. Used for scheduled meetings only. Please provide a value of type integer.""",
    )  # noqa: E501

    meetingId: int = Field(
        description="""The meeting"s ID.   When storing this value in your database, store it as a long format integer and **not** an integer. Meeting IDs can be greater than 10 digits. . Please provide a value of type integer. This parameter is required."""
    )  # noqa: E501

    occurrence_id: Optional[str] = Field(
        default=None,
        description="""Meeting occurrence ID. Support change of agenda, `start_time`, duration, or settings {`host_video`, `participant_video`, `join_before_host`, `mute_upon_entry`, `waiting_room`, `watermark`, `auto_recording`}. . Please provide a value of type string.""",
    )  # noqa: E501

    password: Optional[str] = Field(
        default=None,
        description="""Meeting passcode. Passcodes may only contain these characters [a-z A-Z 0-9 @ - _ *] and can have a maximum of 10 characters. **Note** If the account owner or the admin has configured [minimum passcode requirement settings](https://support.zoom.us/hc/en-us/articles/360033559832-Meeting-and-webinar-passwords#h_a427384b-e383-4f80-864d-794bf0a37604), the passcode value provided here must meet those requirements.         If the requirements are enabled, view those requirements by calling either the [**Get user settings**](https://developers.zoom.us) API or the [**Get account settings**](https://developers.zoom.us) API. . Please provide a value of type string.""",
    )  # noqa: E501

    pre_schedule: Optional[bool] = Field(
        default=False,
        description="""Whether to create a prescheduled meeting through the [GSuite app](https://support.zoom.us/hc/en-us/articles/360020187492-Zoom-for-GSuite-add-on). This **only** supports the meeting `type` value of `2` - scheduled meetings- and `3` - recurring meetings with no fixed time.  * `true` - Create a prescheduled meeting.  * `false` - Create a regular meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    recurrence__end__date__time: Optional[str] = Field(
        default=None,
        description="""Select the final date when the meeting recurs before it is canceled. Should be in UTC time, such as 2017-11-25T12:00:00Z. Cannot be used with `end_times`. . Please provide a value of type string.""",
    )  # noqa: E501

    recurrence__end__times: Optional[int] = Field(
        default=1,
        description="""Select how many times the meeting should recur before it is canceled. If `end_times` is set to 0, it means there is no end time. The maximum number of recurrences is 60. Cannot be used with `end_date_time`. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__monthly__day: Optional[int] = Field(
        default=1,
        description="""Use this field **only if you"re scheduling a recurring meeting of type** `3` to state the day in a month when the meeting should recur. The value range is from 1 to 31. For instance, if the meeting should recur on 23rd of each month, provide `23` as this field"s value and `1` as the `repeat_interval` field"s value. If the meeting should recur every three months on 23rd of the month, change the `repeat_interval` field"s value to `3`. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__monthly__week: Optional[int] = Field(
        default=None,
        description="""Use this field **only if you"re scheduling a recurring meeting of type** `3` to state the week of the month when the meeting should recur. If you use this field, you must also use the `monthly_week_day` field to state the day of the week when the meeting should recur.     `-1` - Last week of the month.    `1` - First week of the month.    `2` - Second week of the month.    `3` - Third week of the month.    `4` - Fourth week of the month. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__monthly__week__day: Optional[int] = Field(
        default=None,
        description="""Use this field only if you"re scheduling a recurring meeting of type `3` to state a specific day in a week when a monthly meeting should recur. To use this field, you must also use the `monthly_week` field.      `1` - Sunday.    `2` - Monday.    `3` - Tuesday.    `4` -  Wednesday.    `5` - Thursday.    `6` - Friday.    `7` - Saturday. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__repeat__interval: Optional[int] = Field(
        default=None,
        description="""Define the interval when the meeting should recur. For instance, to schedule a meeting that recurs every two months, set this field"s value as `2` and the `type` parameter"s value to `3`.  For a daily meeting, the maximum interval is `90` days. For a weekly meeting, the maximum interval is `12` weeks. For a monthly meeting, the maximum value is `3` months.  . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__type: Optional[int] = Field(
        default=None,
        description="""Recurrence meeting types.   `1` - Daily.    `2` - Weekly.    `3` - Monthly. . Please provide a value of type integer.""",
    )  # noqa: E501

    recurrence__weekly__days: Optional[Literal["1", "2", "3", "4", "5", "6", "7"]] = (
        Field(
            default="1",
            description="""This field is required if you"re scheduling a recurring meeting of type `2`, to state which days of the week the meeting should repeat.    Thiw field"s value could be a number between `1` to `7` in string format. For instance, if the meeting should recur on Sunday, provide `1` as this field"s value.         **Note** If you would like the meeting to occur on multiple days of a week, you should provide comma separated values for this field. For instance, if the meeting should recur on Sundays and Tuesdays provide `1,3` as this field"s value.      `1`  - Sunday.     `2` - Monday.    `3` - Tuesday.    `4` -  Wednesday.    `5` -  Thursday.    `6` - Friday.    `7` - Saturday. . Please provide a value of type string.""",
        )
    )  # noqa: E501

    schedule_for: Optional[str] = Field(
        default=None,
        description="""The email address or `userId` of the user to schedule a meeting for. Please provide a value of type string.""",
    )  # noqa: E501

    settings__allow__multiple__devices: Optional[bool] = Field(
        default=None,
        description="""Allow attendees to join the meeting from multiple devices. This setting only works for meetings that require [registration](https://support.zoom.us/hc/en-us/articles/211579443-Setting-up-registration-for-a-meeting). . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__alternative__host__update__polls: Optional[bool] = Field(
        default=None,
        description="""Whether the **Allow alternative hosts to add or edit polls** feature is enabled. This requires Zoom version 5.8.0 or higher. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__alternative__hosts: Optional[str] = Field(
        default=None,
        description="""A semicolon-separated list of the meeting"s alternative hosts" email addresses or IDs. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__alternative__hosts__email__notification: Optional[bool] = Field(
        default=True,
        description="""Flag to determine whether to send email notifications to alternative hosts, default value is true. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__approval__type: Optional[int] = Field(
        default=2,
        description="""Enable registration and set approval for the registration. Note that this feature requires the host to be of **Licensed** user type. **Registration cannot be enabled for a basic user.**          `0` - Automatically approve.    `1` - Manually approve.    `2` - No registration required. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__approved__or__denied__countries__or__regions__approved__list: Optional[
        list[Any]
    ] = Field(
        default=None,
        description="""List of countries or regions from where participants can join this meeting.  """,
    )  # noqa: E501

    settings__approved__or__denied__countries__or__regions__denied__list: Optional[
        list[Any]
    ] = Field(
        default=None,
        description="""List of countries or regions from where participants can not join this meeting.  """,
    )  # noqa: E501

    settings__approved__or__denied__countries__or__regions__enable: Optional[bool] = (
        Field(
            default=None,
            description="""`true` - Setting enabled to either allow users or block users from specific regions to join your meetings.   `false` - Setting disabled. . Please provide a value of type boolean.""",
        )
    )  # noqa: E501

    settings__approved__or__denied__countries__or__regions__method: Optional[
        Literal["approve", "deny"]
    ] = Field(
        default=None,
        description="""Specify whether to allow users from specific regions to join this meeting, or block users from specific regions from joining this meeting.   `approve` - Allow users from specific regions or countries to join this meeting. If this setting is selected, include the approved regions or countries in the `approved_list`.    `deny` - Block users from specific regions or countries from joining this meeting. If this setting is selected, include the approved regions orcountries in the `denied_list` . Please provide a value of type string.""",
    )  # noqa: E501

    settings__audio: Optional[Literal["both", "telephony", "voip", "thirdParty"]] = Field(
        default="both",
        description="""Determine how participants can join the audio portion of the meeting.    `both` - Both Telephony and VoIP.    `telephony` - Telephony only.    `voip` - VoIP only.    `thirdParty` - Third party audio conference. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__audio__conference__info: Optional[str] = Field(
        default=None,
        description="""Third party audio conference info. Please provide a value of type string.""",
    )  # noqa: E501

    settings__authentication__domains: Optional[str] = Field(
        default=None,
        description="""If user has configured [Sign Into Zoom with Specified Domains](https://support.zoom.us/hc/en-us/articles/360037117472-Authentication-Profiles-for-Meetings-and-Webinars#h_5c0df2e1-cfd2-469f-bb4a-c77d7c0cca6f) option, this will list the domains that are authenticated. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__authentication__exception: Optional[list[Any]] = Field(
        default=None,
        description="""The participants added here will receive unique meeting invite links and bypass authentication. """,
    )  # noqa: E501

    settings__authentication__name: Optional[str] = Field(
        default=None,
        description="""Authentication name set in the [authentication profile](https://support.zoom.us/hc/en-us/articles/360037117472-Authentication-Profiles-for-Meetings-and-Webinars#h_5c0df2e1-cfd2-469f-bb4a-c77d7c0cca6f). . Please provide a value of type string.""",
    )  # noqa: E501

    settings__authentication__option: Optional[str] = Field(
        default=None,
        description="""Meeting authentication option ID. Please provide a value of type string.""",
    )  # noqa: E501

    settings__auto__recording: Optional[Literal["local", "cloud", "none"]] = Field(
        default="none",
        description="""Automatic recording.   `local` - Record on local.    `cloud` -  Record on cloud.    `none` - Disabled. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__auto__start__ai__companion__questions: Optional[bool] = Field(
        default=False,
        description="""Whether to automatically start AI Companion questions. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__auto__start__meeting__summary: Optional[bool] = Field(
        default=False,
        description="""Whether to automatically start meeting summary. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__breakout__room__enable: Optional[bool] = Field(
        default=None,
        description="""Set this field"s value to `true` to enable the [breakout room pre-assign](https://support.zoom.us/hc/en-us/articles/360032752671-Pre-assigning-participants-to-breakout-rooms#h_36f71353-4190-48a2-b999-ca129861c1f4) option. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__breakout__room__rooms: Optional[list[Any]] = Field(
        default=None, description="""Create room(s)."""
    )  # noqa: E501

    settings__calendar__type: Optional[int] = Field(
        default=None,
        description="""The type of calendar integration used to schedule the meeting.  * `1` - [Zoom Outlook add-in](https://support.zoom.us/hc/en-us/articles/360031592971-Getting-started-with-Outlook-plugin-and-add-in)  * `2` - [Zoom for Google Workspace add-on](https://support.zoom.us/hc/en-us/articles/360020187492-Using-the-Zoom-for-Google-Workspace-add-on) Works with the `private_meeting` field to determine whether to share details of meetings. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__close__registration: Optional[bool] = Field(
        default=False,
        description="""Close registration after the event date. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__cn__meeting: Optional[bool] = Field(
        default=False,
        description="""Host the meeting in China. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__contact__email: Optional[str] = Field(
        default=None,
        description="""Contact email for registration. Please provide a value of type string.""",
    )  # noqa: E501

    settings__contact__name: Optional[str] = Field(
        default=None,
        description="""Contact name for registration. Please provide a value of type string.""",
    )  # noqa: E501

    settings__continuous__meeting__chat__auto__add__invited__external__users: Optional[
        bool
    ] = Field(
        default=None,
        description="""Whether to enable the **Automatically add invited external users** setting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__continuous__meeting__chat__enable: Optional[bool] = Field(
        default=None,
        description="""Whether to enable the **Enable continuous meeting chat** setting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__custom__keys: Optional[list[Any]] = Field(
        default=None, description="""Custom keys and values assigned to the meeting."""
    )  # noqa: E501

    settings__email__notification: Optional[bool] = Field(
        default=True,
        description="""Whether to send email notifications to [alternative hosts](https://support.zoom.us/hc/en-us/articles/208220166) and [users with scheduling privileges](https://support.zoom.us/hc/en-us/articles/201362803-Scheduling-privilege). This value defaults to `true`. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__encryption__type: Optional[Literal["enhanced_encryption", "e2ee"]] = Field(
        default=None,
        description="""Choose between enhanced encryption and [end-to-end encryption](https://support.zoom.us/hc/en-us/articles/360048660871) when starting or a meeting. When using end-to-end encryption, several features such cloud recording and phone/SIP/H.323 dial-in, will be **automatically disabled**.    `enhanced_encryption` - Enhanced encryption. Encryption is stored in the cloud if you enable this option.      `e2ee` - [End-to-end encryption](https://support.zoom.us/hc/en-us/articles/360048660871). The encryption key is stored in your local device and can not be obtained by anyone else. Enabling this setting also **disables** the features join before host, cloud recording, streaming, live transcription, breakout rooms, polling, 1:1 private chat, and meeting reactions. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__enforce__login: Optional[bool] = Field(
        default=None,
        description="""Only signed in users can join this meeting. **This field is deprecated and will not be supported in the future.**          As an alternative, use the `meeting_authentication`, `authentication_option`, and `authentication_domains` fields to understand the [authentication configurations](https://support.zoom.us/hc/en-us/articles/360037117472-Authentication-Profiles-for-Meetings-and-Webinars) set for the meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__enforce__login__domains: Optional[str] = Field(
        default=None,
        description="""Only signed in users with specified domains can join meetings. **This field is deprecated and will not be supported in the future.**          As an alternative, use the `meeting_authentication`, `authentication_option`. and `authentication_domains` fields to understand the [authentication configurations](https://support.zoom.us/hc/en-us/articles/360037117472-Authentication-Profiles-for-Meetings-and-Webinars) set for the meeting. . Please provide a value of type string.""",
    )  # noqa: E501

    settings__focus__mode: Optional[bool] = Field(
        default=None,
        description="""Whether the [**Focus Mode** feature](https://support.zoom.us/hc/en-us/articles/360061113751-Using-focus-mode) is enabled when the meeting starts. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__global__dial__in__countries: Optional[list[Any]] = Field(
        default=None, description="""List of global dial-in countries"""
    )  # noqa: E501

    settings__global__dial__in__numbers: Optional[list[Any]] = Field(
        default=None, description="""Global dial-in countries or regions"""
    )  # noqa: E501

    settings__host__save__video__order: Optional[bool] = Field(
        default=None,
        description="""Whether the **Allow host to save video order** feature is enabled. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__host__video: Optional[bool] = Field(
        default=None,
        description="""Start video when the host joins the meeting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__in__meeting: Optional[bool] = Field(
        default=False,
        description="""Host meeting in India. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__internal__meeting: Optional[bool] = Field(
        default=False,
        description="""Whether to set the meeting as an internal meeting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__jbh__time: Optional[int] = Field(
        default=None,
        description="""If the value of `join_before_host` field is set to true, use this field to indicate time limits for a participant to join a meeting before a host. *  `0` - Allow participant to join anytime. *  `5` - Allow participant to join 5 minutes before meeting start time.  * `10` - Allow participant to join 10 minutes before meeting start time. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__join__before__host: Optional[bool] = Field(
        default=False,
        description="""Allow participants to join the meeting before the host starts the meeting. Only used for scheduled or recurring meetings. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__language__interpretation__enable: Optional[bool] = Field(
        default=None,
        description="""Whether to enable [language interpretation](https://support.zoom.us/hc/en-us/articles/360034919791-Language-interpretation-in-meetings-and-webinars) for the meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__language__interpretation__interpreters: Optional[list[Any]] = Field(
        default=None,
        description="""Information about the meeting"s language interpreters.""",
    )  # noqa: E501

    settings__meeting__authentication: Optional[bool] = Field(
        default=None,
        description="""`true`- Only authenticated users can join meetings. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__meeting__invitees: Optional[list[Any]] = Field(
        default=None, description="""A list of the meeting"s invitees."""
    )  # noqa: E501

    settings__mute__upon__entry: Optional[bool] = Field(
        default=False,
        description="""Mute participants upon entry. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__participant__focused__meeting: Optional[bool] = Field(
        default=False,
        description="""Whether to set the meeting as a participant focused meeting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__participant__video: Optional[bool] = Field(
        default=None,
        description="""Start video when participants join the meeting. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__private__meeting: Optional[bool] = Field(
        default=None,
        description="""Whether the meeting is set as private. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__registrants__confirmation__email: Optional[bool] = Field(
        default=None,
        description="""Whether to send registrants an email confirmation. * `true` - Send a confirmation email. * `false` - Do not send a confirmation email. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__registrants__email__notification: Optional[bool] = Field(
        default=None,
        description="""Whether to send registrants email notifications about their registration approval, cancellation, or rejection. * `true` - Send an email notification. * `false` - Do not send an email notification.  Set this value to `true` to also use the `registrants_confirmation_email` parameter. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__registration__type: Optional[int] = Field(
        default=1,
        description="""Registration type. Used for recurring meeting with fixed time only.  `1` - Attendees register once and can attend any of the occurrences.    `2` - Attendees need to register for each occurrence to attend.    `3` - Attendees register once and can choose one or more occurrences to attend. . Please provide a value of type integer.""",
    )  # noqa: E501

    settings__resources: Optional[list[Any]] = Field(
        default=None, description="""The meeting"s resources."""
    )  # noqa: E501

    settings__show__share__button: Optional[bool] = Field(
        default=None,
        description="""Show social share buttons on the meeting registration page. This setting only works for meetings that require [registration](https://support.zoom.us/hc/en-us/articles/211579443-Setting-up-registration-for-a-meeting). . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__sign__language__interpretation__enable: Optional[bool] = Field(
        default=None,
        description="""Whether to enable [sign language interpretation](https://support.zoom.us/hc/en-us/articles/9644962487309-Using-sign-language-interpretation-in-a-meeting-or-webinar) for the meeting. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__sign__language__interpretation__interpreters: Optional[list[Any]] = Field(
        default=None,
        description="""Information about the meeting"s sign language interpreters.""",
    )  # noqa: E501

    settings__use__pmi: Optional[bool] = Field(
        default=False,
        description="""Use a [personal meeting ID (PMI)](https://developers.zoom.us/docs/api/rest/using-zoom-apis/#understanding-personal-meeting-id-pmi). Only used for scheduled meetings and recurring meetings with no fixed time. . Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__waiting__room: Optional[bool] = Field(
        default=False,
        description="""Enable waiting room. Please provide a value of type boolean.""",
    )  # noqa: E501

    settings__watermark: Optional[bool] = Field(
        default=False,
        description="""Add a watermark when viewing a shared screen. Please provide a value of type boolean.""",
    )  # noqa: E501

    start_time: Optional[str] = Field(
        default=None,
        description="""Meeting start time. When using a format like `yyyy-MM-dd"T"HH:mm:ss"Z"`, always use GMT time. When using a format like `yyyy-MM-dd"T"HH:mm:ss`, use local time and specify the time zone. Only used for scheduled meetings and recurring meetings with a fixed time. . Please provide a value of type string.""",
    )  # noqa: E501

    template_id: Optional[str] = Field(
        default=None,
        description="""Unique identifier of the meeting template.  [Schedule the meeting from a meeting template](https://support.zoom.us/hc/en-us/articles/360036559151-Meeting-templates#h_86f06cff-0852-4998-81c5-c83663c176fb). Retrieve this field"s value by calling the [List meeting templates](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/listMeetingTemplates) API. . Please provide a value of type string.""",
    )  # noqa: E501

    timezone: Optional[str] = Field(
        default=None,
        description="""The timezone to assign to the `start_time` value. Only use this field ifor scheduled or recurring meetings with a fixed time. For a list of supported timezones and their formats, see our [timezone list](https://developers.zoom.us/docs/api/rest/other-references/abbreviation-lists/#timezones). . Please provide a value of type string.""",
    )  # noqa: E501

    topic: Optional[str] = Field(
        default=None,
        description="""Meeting topic. Please provide a value of type string.""",
    )  # noqa: E501

    tracking_fields: Optional[list[Any]] = Field(
        default=None, description="""Tracking fields."""
    )  # noqa: E501

    type: Optional[int] = Field(
        default=2,
        description="""Meeting types.  `1` - Instant meeting.    `2` - Scheduled meeting.    `3` - Recurring meeting with no fixed time.    `8` - Recurring meeting with a fixed time. . Please provide a value of type integer.""",
    )  # noqa: E501
