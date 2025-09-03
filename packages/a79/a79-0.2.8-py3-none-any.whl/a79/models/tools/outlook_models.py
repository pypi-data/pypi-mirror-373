import typing as t

from pydantic import BaseModel

from . import ToolOutput


class OutlookInput(BaseModel):
    access_token: str
    folder_name: str = "News Flow"
    start_date: t.Optional[str] = None
    end_date: t.Optional[str] = None


class EmailItem(BaseModel):
    subject: str
    body: str
    date: str
    sender: t.Optional[str] = None
    to: t.Optional[list[str]] = None


class OutlookOutput(ToolOutput):
    content: list[EmailItem]
