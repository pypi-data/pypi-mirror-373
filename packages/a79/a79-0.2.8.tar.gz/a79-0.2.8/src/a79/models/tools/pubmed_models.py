import datetime

from pydantic import BaseModel

from . import ToolOutput


class ArticleRecord(BaseModel):
    pubmed_id: str
    pubmed_url: str
    dc_identifier: str | None = None
    article_url: str | None = None
    title: str
    abstract: str
    background: str | None = None
    objective: str | None = None
    methods: str | None = None
    results: str | None = None
    conclusions: str | None = None
    authors: list[str]
    published_at: datetime.date


class GetArticlesInput(BaseModel):
    feed_url: str
    limit: int = 15


class GetArticlesOutput(ToolOutput):
    articles: list[ArticleRecord]
