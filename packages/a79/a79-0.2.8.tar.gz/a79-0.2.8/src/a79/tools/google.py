# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.google_models import SearchInput, SearchOutput

__all__ = ["SearchInput", "SearchOutput", "search"]


def search(
    *,
    query: str,
    num_results: int = DEFAULT,
    num_pages: int = DEFAULT,
    num_extracts: int = DEFAULT,
    extraction_method: str = DEFAULT,
) -> SearchOutput:
    """
    Perform a Google search and extract snippets, webpages, and summaries.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="google", name="search", input=input_model.model_dump()
    )
    return SearchOutput.model_validate(output_model)
