# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.composio_models import ComposioResult
from ..models.tools.gmail_models import (
    AddLabelToEmailInput,
    CreateEmailDraftInput,
    CreateLabelInput,
    DeleteDraftInput,
    DeleteMessageInput,
    FetchEmailsInput,
    FetchMessageByMessageIdInput,
    FetchMessageByThreadIdInput,
    GetAttachmentInput,
    GetContactsInput,
    GetPeopleInput,
    GetProfileInput,
    ListDraftsInput,
    ListLabelsInput,
    MoveToTrashInput,
    PatchLabelInput,
    ReplyToThreadInput,
    SearchPeopleInput,
    SendDraftInput,
    SendEmailInput,
)

__all__ = [
    "AddLabelToEmailInput",
    "CreateEmailDraftInput",
    "CreateLabelInput",
    "DeleteDraftInput",
    "DeleteMessageInput",
    "FetchEmailsInput",
    "FetchMessageByMessageIdInput",
    "FetchMessageByThreadIdInput",
    "GetAttachmentInput",
    "GetContactsInput",
    "GetPeopleInput",
    "GetProfileInput",
    "ListDraftsInput",
    "ListLabelsInput",
    "MoveToTrashInput",
    "PatchLabelInput",
    "ReplyToThreadInput",
    "SearchPeopleInput",
    "SendDraftInput",
    "SendEmailInput",
    "create_email_draft",
    "delete_draft",
    "delete_message",
    "fetch_emails",
    "fetch_message_by_message_id",
    "get_attachment",
    "list_drafts",
    "move_to_trash",
    "patch_label",
    "reply_to_thread",
    "search_people",
    "send_draft",
    "send_email",
    "add_label_to_email",
    "create_label",
    "fetch_message_by_thread_id",
    "get_contacts",
    "get_people",
    "get_profile",
    "list_labels",
]


def create_email_draft(
    *,
    attachment: str | None = DEFAULT,
    bcc: list[Any] | None = DEFAULT,
    body: str,
    cc: list[Any] | None = DEFAULT,
    extra_recipients: list[Any] | None = DEFAULT,
    is_html: bool | None = DEFAULT,
    recipient_email: str,
    subject: str,
    thread_id: str | None = DEFAULT,
    user_id: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Create Email Draft"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateEmailDraftInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="create_email_draft", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_draft(*, draft_id: str, user_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Gmail: Delete Draft"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteDraftInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="delete_draft", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_message(*, message_id: str, user_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Gmail: Delete Message"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteMessageInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="delete_message", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def fetch_emails(
    *,
    ids_only: bool | None = DEFAULT,
    include_payload: bool | None = DEFAULT,
    include_spam_trash: bool | None = DEFAULT,
    label_ids: list[Any] | None = DEFAULT,
    max_results: int | None = DEFAULT,
    page_token: str | None = DEFAULT,
    query: str | None = DEFAULT,
    user_id: str | None = DEFAULT,
    verbose: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Fetch Emails"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FetchEmailsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="fetch_emails", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def fetch_message_by_message_id(
    *, format: str | None = DEFAULT, message_id: str, user_id: str | None = DEFAULT
) -> ComposioResult:
    """Execute Gmail: Fetch Message By Message Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FetchMessageByMessageIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail",
        name="fetch_message_by_message_id",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def get_attachment(
    *, attachment_id: str, file_name: str, message_id: str, user_id: str | None = DEFAULT
) -> ComposioResult:
    """Execute Gmail: Get Attachment"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetAttachmentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="get_attachment", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def list_drafts(
    *,
    max_results: int | None = DEFAULT,
    page_token: str | None = DEFAULT,
    user_id: str | None = DEFAULT,
    verbose: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: List Drafts"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListDraftsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="list_drafts", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def move_to_trash(*, message_id: str, user_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Gmail: Move To Trash"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = MoveToTrashInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="move_to_trash", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def patch_label(
    *,
    color: dict[str, Any] | None = DEFAULT,
    id: str,
    labelListVisibility: str | None = DEFAULT,
    messageListVisibility: str | None = DEFAULT,
    name: str | None = DEFAULT,
    userId: str,
) -> ComposioResult:
    """Execute Gmail: Patch Label"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = PatchLabelInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="patch_label", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def reply_to_thread(
    *,
    attachment: str | None = DEFAULT,
    bcc: list[Any] | None = DEFAULT,
    cc: list[Any] | None = DEFAULT,
    extra_recipients: list[Any] | None = DEFAULT,
    is_html: bool | None = DEFAULT,
    message_body: str,
    recipient_email: str,
    thread_id: str,
    user_id: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Reply To Thread"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ReplyToThreadInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="reply_to_thread", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def search_people(
    *,
    other_contacts: bool | None = DEFAULT,
    pageSize: int | None = DEFAULT,
    person_fields: str | None = DEFAULT,
    query: str,
) -> ComposioResult:
    """Execute Gmail: Search People"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchPeopleInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="search_people", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def send_draft(*, draft_id: str, user_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Gmail: Send Draft"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SendDraftInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="send_draft", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def send_email(
    *,
    attachment: str | None = DEFAULT,
    bcc: list[Any] | None = DEFAULT,
    body: str,
    cc: list[Any] | None = DEFAULT,
    extra_recipients: list[Any] | None = DEFAULT,
    is_html: bool | None = DEFAULT,
    recipient_email: str,
    subject: str | None = DEFAULT,
    user_id: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Send Email"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SendEmailInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="send_email", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def add_label_to_email(
    *,
    add_label_ids: list[Any] | None = DEFAULT,
    message_id: str,
    remove_label_ids: list[Any] | None = DEFAULT,
    user_id: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Add Label To Email"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = AddLabelToEmailInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="add_label_to_email", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_label(
    *,
    label_list_visibility: str | None = DEFAULT,
    label_name: str,
    message_list_visibility: str | None = DEFAULT,
    user_id: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Create Label"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateLabelInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="create_label", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def fetch_message_by_thread_id(
    *, page_token: str | None = DEFAULT, thread_id: str, user_id: str | None = DEFAULT
) -> ComposioResult:
    """Execute Gmail: Fetch Message By Thread Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FetchMessageByThreadIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="fetch_message_by_thread_id", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_contacts(
    *,
    include_other_contacts: bool | None = DEFAULT,
    page_token: str | None = DEFAULT,
    person_fields: str | None = DEFAULT,
    resource_name: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Get Contacts"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetContactsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="get_contacts", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_people(
    *,
    other_contacts: bool | None = DEFAULT,
    page_size: int | None = DEFAULT,
    page_token: str | None = DEFAULT,
    person_fields: str | None = DEFAULT,
    resource_name: str | None = DEFAULT,
    sync_token: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Gmail: Get People"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetPeopleInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="get_people", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def get_profile(*, user_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Gmail: Get Profile"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetProfileInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="get_profile", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def list_labels(*, user_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Gmail: List Labels"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListLabelsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="gmail", name="list_labels", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)
