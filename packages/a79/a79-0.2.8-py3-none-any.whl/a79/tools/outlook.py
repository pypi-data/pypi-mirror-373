# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.outlook_models import EmailItem, OutlookInput, OutlookOutput

__all__ = ["EmailItem", "OutlookInput", "OutlookOutput", "fetch_outlook_emails"]


def fetch_outlook_emails(
    *,
    access_token: str,
    folder_name: str = DEFAULT,
    start_date: str | None = DEFAULT,
    end_date: str | None = DEFAULT,
) -> OutlookOutput:
    """
    Fetch emails from a specified Outlook folder, filtered by date and keywords.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = OutlookInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="outlook", name="fetch_outlook_emails", input=input_model.model_dump()
    )
    return OutlookOutput.model_validate(output_model)
