# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.firecrawl_models import (
    CrawlURLInput,
    CrawlURLOutput,
    ExtractorOptions,
    MapURLInput,
    MapURLOutput,
    PageOptions,
    ScrapeURLInput,
    ScrapeURLOutput,
)

__all__ = [
    "CrawlURLInput",
    "CrawlURLOutput",
    "ExtractorOptions",
    "MapURLInput",
    "MapURLOutput",
    "PageOptions",
    "ScrapeURLInput",
    "ScrapeURLOutput",
    "scrape_url",
    "crawl_url",
    "map_url",
]


def scrape_url(
    *,
    url: str = DEFAULT,
    page_options: PageOptions = DEFAULT,
    extractor_options: ExtractorOptions = DEFAULT,
    timeout: int = DEFAULT,
) -> ScrapeURLOutput:
    """Scrape the content of a web page using the latest Firecrawl SDK"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ScrapeURLInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="firecrawl", name="scrape_url", input=input_model.model_dump()
    )
    return ScrapeURLOutput.model_validate(output_model)


def crawl_url(
    *,
    url: str = DEFAULT,
    limit: int = DEFAULT,
    max_depth: int = DEFAULT,
    ignore_sitemap: bool = DEFAULT,
    page_options: PageOptions = DEFAULT,
    extractor_options: ExtractorOptions = DEFAULT,
    timeout: int = DEFAULT,
) -> CrawlURLOutput:
    """Crawl a website and return content using async Firecrawl SDK."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CrawlURLInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="firecrawl", name="crawl_url", input=input_model.model_dump()
    )
    return CrawlURLOutput.model_validate(output_model)


def map_url(
    *,
    url: str = DEFAULT,
    search: str | None = DEFAULT,
    ignore_sitemap: bool = DEFAULT,
    sitemap_only: bool = DEFAULT,
    include_subdomains: bool = DEFAULT,
    limit: int = DEFAULT,
    timeout: int = DEFAULT,
) -> MapURLOutput:
    """Map a website and return list of links."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = MapURLInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="firecrawl", name="map_url", input=input_model.model_dump()
    )
    return MapURLOutput.model_validate(output_model)
