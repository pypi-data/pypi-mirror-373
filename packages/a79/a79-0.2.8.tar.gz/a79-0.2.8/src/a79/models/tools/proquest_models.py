import datetime

from pydantic import BaseModel

from . import ToolOutput


class ArticleRecord(BaseModel):
    proquest_id: str
    title: str | None = None
    abstract: str | None = None
    keywords: list[str]
    url: str | None = None
    doi: str | None = None
    doi_url: str | None = None
    authors: list[str]
    published_at: datetime.date | None = None


class GetArticlesInput(BaseModel):
    feed_url: str
    limit: int = 15


class GetArticlesOutput(ToolOutput):
    articles: list[ArticleRecord]
