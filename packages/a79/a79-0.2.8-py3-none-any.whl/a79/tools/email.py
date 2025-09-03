# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.email_models import SendEmailInput, SendEmailOutput

__all__ = ["SendEmailInput", "SendEmailOutput", "send_email"]


def send_email(*, recipient: str, subject: str, body: str) -> SendEmailOutput:
    """Send an email"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SendEmailInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="email", name="send_email", input=input_model.model_dump()
    )
    return SendEmailOutput.model_validate(output_model)
