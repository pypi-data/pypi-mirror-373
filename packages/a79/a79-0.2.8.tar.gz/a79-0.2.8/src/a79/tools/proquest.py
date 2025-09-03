# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.proquest_models import (
    ArticleRecord,
    GetArticlesInput,
    GetArticlesOutput,
)

__all__ = ["ArticleRecord", "GetArticlesInput", "GetArticlesOutput", "get_articles"]


def get_articles(*, feed_url: str, limit: int = DEFAULT) -> GetArticlesOutput:
    """Fetch articles from ProQuest."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GetArticlesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="proquest", name="get_articles", input=input_model.model_dump()
    )
    return GetArticlesOutput.model_validate(output_model)
