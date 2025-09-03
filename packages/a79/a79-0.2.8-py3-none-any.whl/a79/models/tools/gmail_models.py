# This is a generated file by scripts/codegen/composio.py, do not edit manually
# ruff: noqa: E501  # Ignore line length issues in generated files
from typing import Any, Optional

from pydantic import BaseModel, Field


class CreateEmailDraftInput(BaseModel):
    """Input model for GMAIL_CREATE_EMAIL_DRAFT"""

    attachment: Optional[str] = Field(
        default=None, description="""File to attach to the email."""
    )  # noqa: E501

    bcc: Optional[list[Any]] = Field(
        default=[], description="""'Bcc' (blind carbon copy) recipient email addresses."""
    )  # noqa: E501

    body: str = Field(
        description="""Email body content (plain text or HTML); `is_html` must be True if HTML. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    cc: Optional[list[Any]] = Field(
        default=[], description="""'Cc' (carbon copy) recipient email addresses."""
    )  # noqa: E501

    extra_recipients: Optional[list[Any]] = Field(
        default=[], description="""Additional 'To' recipient email addresses."""
    )  # noqa: E501

    is_html: Optional[bool] = Field(
        default=False,
        description="""Set to True if `body` is HTML, otherwise the action may fail. Please provide a value of type boolean.""",
    )  # noqa: E501

    recipient_email: str = Field(
        description="""Primary recipient's email address. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    subject: str = Field(
        description="""Email subject line. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    thread_id: Optional[str] = Field(
        default=None,
        description="""ID of an existing Gmail thread to reply to; omit for new thread. Please provide a value of type string.""",
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address or 'me' for the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class DeleteDraftInput(BaseModel):
    """Input model for GMAIL_DELETE_DRAFT"""

    draft_id: str = Field(
        description="""Immutable ID of the draft to delete, typically obtained when the draft was created. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address or 'me' for the authenticated user; 'me' is recommended. Please provide a value of type string.""",
    )  # noqa: E501


class DeleteMessageInput(BaseModel):
    """Input model for GMAIL_DELETE_MESSAGE"""

    message_id: str = Field(
        description="""Identifier of the email message to delete. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address. The special value 'me' refers to the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class FetchEmailsInput(BaseModel):
    """Input model for GMAIL_FETCH_EMAILS"""

    ids_only: Optional[bool] = Field(
        default=False,
        description="""If true, only returns message IDs from the list API without fetching individual message details. Fastest option for getting just message IDs and thread IDs. Please provide a value of type boolean.""",
    )  # noqa: E501

    include_payload: Optional[bool] = Field(
        default=True,
        description="""Set to true to include full message payload (headers, body, attachments); false for metadata only. Please provide a value of type boolean.""",
    )  # noqa: E501

    include_spam_trash: Optional[bool] = Field(
        default=False,
        description="""Set to true to include messages from 'SPAM' and 'TRASH'. Please provide a value of type boolean.""",
    )  # noqa: E501

    label_ids: Optional[list[Any]] = Field(
        default=None,
        description="""Filter by label IDs; only messages with all specified labels are returned. Common IDs: 'INBOX', 'SPAM', 'TRASH', 'UNREAD', 'STARRED', 'IMPORTANT', 'CATEGORY_PRIMARY' (alias 'CATEGORY_PERSONAL'), 'CATEGORY_SOCIAL', 'CATEGORY_PROMOTIONS', 'CATEGORY_UPDATES', 'CATEGORY_FORUMS'. Use 'listLabels' action for custom IDs.""",
    )  # noqa: E501

    max_results: Optional[int] = Field(
        default=1,
        description="""Maximum number of messages to retrieve per page. Please provide a value of type integer.""",
    )  # noqa: E501

    page_token: Optional[str] = Field(
        default=None,
        description="""Token for retrieving a specific page, obtained from a previous response's `nextPageToken`. Omit for the first page. Please provide a value of type string.""",
    )  # noqa: E501

    query: Optional[str] = Field(
        default=None,
        description="""Gmail advanced search query (e.g., 'from:user subject:meeting'). Supports operators like 'from:', 'to:', 'subject:', 'label:', 'has:attachment', 'is:unread', 'after:YYYY/MM/DD', 'before:YYYY/MM/DD', AND/OR/NOT. Use quotes for exact phrases. Omit for no query filter. Please provide a value of type string.""",
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address or 'me' for the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501

    verbose: Optional[bool] = Field(
        default=True,
        description="""If false, uses optimized concurrent metadata fetching for faster performance (~75% improvement). If true, uses standard detailed message fetching. When false, only essential fields (subject, sender, recipient, time, labels) are guaranteed. Please provide a value of type boolean.""",
    )  # noqa: E501


class FetchMessageByMessageIdInput(BaseModel):
    """Input model for GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID"""

    format: Optional[str] = Field(
        default="full",
        description="""Format for message content: 'minimal' (ID/labels), 'full' (complete data), 'raw' (base64url string), 'metadata' (ID/labels/headers). Please provide a value of type string.""",
    )  # noqa: E501

    message_id: str = Field(
        description="""Unique ID of the email message to retrieve, obtainable from actions like 'List Messages'. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address or 'me' for the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class GetAttachmentInput(BaseModel):
    """Input model for GMAIL_GET_ATTACHMENT"""

    attachment_id: str = Field(
        description="""ID of the attachment to retrieve. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    file_name: str = Field(
        description="""Desired filename for the downloaded attachment. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    message_id: str = Field(
        description="""Immutable ID of the message containing the attachment. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address ('me' for authenticated user). Please provide a value of type string.""",
    )  # noqa: E501


class ListDraftsInput(BaseModel):
    """Input model for GMAIL_LIST_DRAFTS"""

    max_results: Optional[int] = Field(
        default=1,
        description="""Maximum number of drafts to return per page. Please provide a value of type integer.""",
    )  # noqa: E501

    page_token: Optional[str] = Field(
        default="",
        description="""Token from a previous response to retrieve a specific page of drafts. Please provide a value of type string.""",
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's mailbox ID; use 'me' for the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501

    verbose: Optional[bool] = Field(
        default=False,
        description="""If true, fetches full draft details including subject, sender, recipient, body, and timestamp. If false, returns only draft IDs (faster). Please provide a value of type boolean.""",
    )  # noqa: E501


class MoveToTrashInput(BaseModel):
    """Input model for GMAIL_MOVE_TO_TRASH"""

    message_id: str = Field(
        description="""Identifier of the email message to move to trash. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address or 'me' for the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class PatchLabelInput(BaseModel):
    """Input model for GMAIL_PATCH_LABEL"""

    color: Optional[dict[str, Any]] = Field(
        default=None,
        description="""The color to assign to the label. Color is only available for labels that have their `type` set to `user`.""",
    )  # noqa: E501

    id: str = Field(
        description="""The ID of the label to update. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    labelListVisibility: Optional[str] = Field(
        default=None,
        description="""The visibility of the label in the label list in the Gmail web interface. Please provide a value of type string.""",
    )  # noqa: E501

    messageListVisibility: Optional[str] = Field(
        default=None,
        description="""The visibility of messages with this label in the message list in the Gmail web interface. Please provide a value of type string.""",
    )  # noqa: E501

    name: Optional[str] = Field(
        default=None,
        description="""The display name of the label. Please provide a value of type string.""",
    )  # noqa: E501

    userId: str = Field(
        description="""The user's email address. The special value `me` can be used to indicate the authenticated user. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class ReplyToThreadInput(BaseModel):
    """Input model for GMAIL_REPLY_TO_THREAD"""

    attachment: Optional[str] = Field(
        default=None,
        description="""File to attach to the reply. Just Provide file path here""",
    )  # noqa: E501

    bcc: Optional[list[Any]] = Field(
        default=[],
        description="""BCC recipients' email addresses (hidden from other recipients).""",
    )  # noqa: E501

    cc: Optional[list[Any]] = Field(
        default=[], description="""CC recipients' email addresses."""
    )  # noqa: E501

    extra_recipients: Optional[list[Any]] = Field(
        default=[], description="""Additional 'To' recipients' email addresses."""
    )  # noqa: E501

    is_html: Optional[bool] = Field(
        default=False,
        description="""Indicates if `message_body` is HTML; if True, body must be valid HTML, if False, body should not contain HTML tags. Please provide a value of type boolean.""",
    )  # noqa: E501

    message_body: str = Field(
        description="""Content of the reply message, either plain text or HTML. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    recipient_email: str = Field(
        description="""Primary recipient's email address. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    thread_id: str = Field(
        description="""Identifier of the Gmail thread for the reply. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""Identifier for the user sending the reply; 'me' refers to the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class SearchPeopleInput(BaseModel):
    """Input model for GMAIL_SEARCH_PEOPLE"""

    other_contacts: Optional[bool] = Field(
        default=True,
        description="""Include 'Other Contacts' (interacted with but not explicitly saved) in search results; if false, searches only primary contacts. Please provide a value of type boolean.""",
    )  # noqa: E501

    pageSize: Optional[int] = Field(
        default=10,
        description="""Maximum results to return; values >30 are capped to 30 by the API. Please provide a value of type integer.""",
    )  # noqa: E501

    person_fields: Optional[str] = Field(
        default="emailAddresses,names,phoneNumbers",
        description="""Comma-separated fields to return (e.g., 'names,emailAddresses'); see PersonFields enum. If 'other_contacts' is true, only 'emailAddresses', 'names', 'phoneNumbers' are allowed. Please provide a value of type string.""",
    )  # noqa: E501

    query: str = Field(
        description="""Matches contact names, nicknames, email addresses, phone numbers, and organization fields. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class SendDraftInput(BaseModel):
    """Input model for GMAIL_SEND_DRAFT"""

    draft_id: str = Field(
        description="""The ID of the draft to send. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""The user's email address. The special value `me` can be used to indicate the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class SendEmailInput(BaseModel):
    """Input model for GMAIL_SEND_EMAIL"""

    attachment: Optional[str] = Field(
        default=None,
        description="""File to attach; ensure `s3key`, `mimetype`, and `name` are set if provided. Omit or set to null for no attachment.""",
    )  # noqa: E501

    bcc: Optional[list[Any]] = Field(
        default=[], description="""Blind Carbon Copy (BCC) recipients' email addresses."""
    )  # noqa: E501

    body: str = Field(
        description="""Email content (plain text or HTML); if HTML, `is_html` must be `True`. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    cc: Optional[list[Any]] = Field(
        default=[], description="""Carbon Copy (CC) recipients' email addresses."""
    )  # noqa: E501

    extra_recipients: Optional[list[Any]] = Field(
        default=[],
        description="""Additional 'To' recipients' email addresses (not Cc or Bcc).""",
    )  # noqa: E501

    is_html: Optional[bool] = Field(
        default=False,
        description="""Set to `True` if the email body contains HTML tags. Please provide a value of type boolean.""",
    )  # noqa: E501

    recipient_email: str = Field(
        description="""Primary recipient's email address. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    subject: Optional[str] = Field(
        default=None,
        description="""Subject line of the email. Please provide a value of type string.""",
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address; the literal 'me' refers to the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class AddLabelToEmailInput(BaseModel):
    """Input model for GMAIL_ADD_LABEL_TO_EMAIL"""

    add_label_ids: Optional[list[Any]] = Field(
        default=[],
        description="""Label IDs to add. For custom labels, obtain IDs via 'listLabels'. System labels (e.g., 'INBOX', 'SPAM') can also be used.""",
    )  # noqa: E501

    message_id: str = Field(
        description="""Immutable ID of the message to modify (e.g., from 'fetchEmails' or 'fetchMessagesByThreadId'). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    remove_label_ids: Optional[list[Any]] = Field(
        default=[],
        description="""Label IDs to remove. For custom labels, obtain IDs via 'listLabels'. System labels can also be used.""",
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""User's email address or 'me' for the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class CreateLabelInput(BaseModel):
    """Input model for GMAIL_CREATE_LABEL"""

    label_list_visibility: Optional[str] = Field(
        default="labelShow",
        description="""Controls how the label is displayed in the label list in the Gmail sidebar. Please provide a value of type string.""",
    )  # noqa: E501

    label_name: str = Field(
        description="""The name for the new label. Must be unique within the account, non-blank, maximum length 225 characters, cannot contain ',' or '/', not only whitespace, and must not be a reserved system label (e.g., INBOX, DRAFTS, SENT). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    message_list_visibility: Optional[str] = Field(
        default="show",
        description="""Controls how messages with this label are displayed in the message list. Please provide a value of type string.""",
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""The email address of the user in whose account the label will be created. Please provide a value of type string.""",
    )  # noqa: E501


class FetchMessageByThreadIdInput(BaseModel):
    """Input model for GMAIL_FETCH_MESSAGE_BY_THREAD_ID"""

    page_token: Optional[str] = Field(
        default="",
        description="""Opaque page token for fetching a specific page of messages if results are paginated. Please provide a value of type string.""",
    )  # noqa: E501

    thread_id: str = Field(
        description="""Unique ID of the thread, obtainable from actions like 'listThreads' or 'fetchEmails'. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    user_id: Optional[str] = Field(
        default="me",
        description="""The email address of the user. Please provide a value of type string.""",
    )  # noqa: E501


class GetContactsInput(BaseModel):
    """Input model for GMAIL_GET_CONTACTS"""

    include_other_contacts: Optional[bool] = Field(
        default=True,
        description="""Include 'Other Contacts' (interacted with but not explicitly saved) in addition to regular contacts; if true, fetches from both endpoints and merges results. Please provide a value of type boolean.""",
    )  # noqa: E501

    page_token: Optional[str] = Field(
        default=None,
        description="""Token to retrieve a specific page of results, obtained from 'nextPageToken' in a previous response. Please provide a value of type string.""",
    )  # noqa: E501

    person_fields: Optional[str] = Field(
        default="emailAddresses,names,birthdays,genders",
        description="""Comma-separated person fields to retrieve for each contact (e.g., 'names,emailAddresses'). Please provide a value of type string.""",
    )  # noqa: E501

    resource_name: Optional[str] = Field(
        default="people/me",
        description="""Identifier for the person resource whose connections are listed; use 'people/me' for the authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class GetPeopleInput(BaseModel):
    """Input model for GMAIL_GET_PEOPLE"""

    other_contacts: Optional[bool] = Field(
        default=False,
        description="""If true, retrieves 'Other Contacts' (people interacted with but not explicitly saved), ignoring `resource_name` and enabling pagination/sync. If false, retrieves information for the single person specified by `resource_name`. Please provide a value of type boolean.""",
    )  # noqa: E501

    page_size: Optional[int] = Field(
        default=10,
        description="""The number of 'Other Contacts' to return per page. Applicable only when `other_contacts` is true. Please provide a value of type integer.""",
    )  # noqa: E501

    page_token: Optional[str] = Field(
        default="",
        description="""An opaque token from a previous response to retrieve the next page of 'Other Contacts' results. Applicable only when `other_contacts` is true and paginating. Please provide a value of type string.""",
    )  # noqa: E501

    person_fields: Optional[str] = Field(
        default="emailAddresses,names,birthdays,genders",
        description="""A comma-separated field mask to restrict which fields on the person (or persons) are returned. Consult the Google People API documentation for a comprehensive list of valid fields. Please provide a value of type string.""",
    )  # noqa: E501

    resource_name: Optional[str] = Field(
        default="people/me",
        description="""Resource name identifying the person for whom to retrieve information (like the authenticated user or a specific contact). Used only when `other_contacts` is false. Please provide a value of type string.""",
    )  # noqa: E501

    sync_token: Optional[str] = Field(
        default="",
        description="""A token from a previous 'Other Contacts' list call to retrieve only changes since the last sync; leave empty for an initial full sync. Applicable only when `other_contacts` is true. Please provide a value of type string.""",
    )  # noqa: E501


class GetProfileInput(BaseModel):
    """Input model for GMAIL_GET_PROFILE"""

    user_id: Optional[str] = Field(
        default="me",
        description="""The email address of the Gmail user whose profile is to be retrieved, or the special value 'me' to indicate the currently authenticated user. Please provide a value of type string.""",
    )  # noqa: E501


class ListLabelsInput(BaseModel):
    """Input model for GMAIL_LIST_LABELS"""

    user_id: Optional[str] = Field(
        default="me",
        description="""Identifies the Gmail account (owner's email or 'me' for authenticated user) for which labels will be listed. Please provide a value of type string.""",
    )  # noqa: E501
