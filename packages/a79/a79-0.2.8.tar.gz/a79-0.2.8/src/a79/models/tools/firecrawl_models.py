import typing as t

from pydantic import BaseModel, Field

from .. import enums
from . import ToolOutput


class PageOptions(BaseModel):
    """Options for configuring page scraping behavior."""

    headers: dict | None = None
    # processed HTML without ads, scripts, and non-essential elements
    include_html: bool = False
    # unmodified HTML source code exactly as received from the server,
    # including all scripts, ads, and metadata.
    include_raw_html: bool = False
    only_main_content: bool = True
    exclude_tags: list[str] | None = None
    wait_for: int = 0


class ExtractorOptions(BaseModel):
    """Options for configuring content extraction behavior."""

    extraction_prompt: str | None = None  # Maps to jsonOptions.prompt
    extraction_schema: dict | None = None  # Maps to jsonOptions.schema


class ScrapeURLInput(BaseModel):
    url: str = Field(
        default="",
        json_schema_extra={
            "mandatory": True,
            "field_type": enums.CustomDataType.URL.value,
        },
    )
    page_options: PageOptions = Field(
        default_factory=PageOptions, description="The options for scraping the page"
    )
    extractor_options: ExtractorOptions = Field(
        default_factory=ExtractorOptions,
        description="The options for extracting content via service LLM",
    )
    timeout: int = 60000


class ScrapeURLOutput(ToolOutput):
    content: dict[str, t.Any]


class CrawlURLInput(BaseModel):
    url: str = Field(
        default="",
        json_schema_extra={
            "mandatory": True,
            "field_type": enums.CustomDataType.URL.value,
        },
    )
    limit: int = Field(default=10, description="Maximum number of pages to crawl")
    max_depth: int = Field(default=2, description="Maximum depth for the crawl")
    ignore_sitemap: bool = Field(
        default=True, description="Whether to ignore the sitemap when crawling"
    )
    page_options: PageOptions = Field(
        default_factory=PageOptions, description="The options for scraping each page"
    )
    extractor_options: ExtractorOptions = Field(
        default_factory=ExtractorOptions,
        description="The options for extracting content via service LLM",
    )
    timeout: int = 600


class CrawlURLOutput(ToolOutput):
    data: list[dict[str, t.Any]] = Field(
        default_factory=list, description="List of scraped page data from the crawl"
    )
    status: str = Field(default="", description="Status of the crawl operation")
    job_id: str | None = Field(
        default=None, description="Job ID if crawl was processed asynchronously"
    )
    credits_used: int | None = Field(
        default=None, description="Number of credits used for the crawl"
    )


class MapURLInput(BaseModel):
    """Input parameters for the Firecrawl Map endpoint."""

    url: str = Field(
        default="",
        json_schema_extra={
            "mandatory": True,
            "field_type": enums.CustomDataType.URL.value,
        },
    )
    search: str | None = None
    ignore_sitemap: bool = True
    sitemap_only: bool = False
    include_subdomains: bool = False
    limit: int = 5000
    timeout: int = 120000


class MapURLOutput(ToolOutput):
    """Output from the Firecrawl Map endpoint."""

    success: bool = False
    links: list[str] = Field(default_factory=list)
