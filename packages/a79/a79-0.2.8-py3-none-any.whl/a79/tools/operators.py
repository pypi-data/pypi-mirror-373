# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.operators_models import MergeContentInput, MergeContentOutput

__all__ = ["MergeContentInput", "MergeContentOutput", "merge_content"]


def merge_content(
    *,
    separator: str = DEFAULT,
    content_headers: list[str] = DEFAULT,
    content_texts: list[str] = DEFAULT,
    indent_level: int = DEFAULT,
    title: str | None = DEFAULT,
) -> MergeContentOutput:
    """
    Merge content from multiple nodes into a single text with numbered section
    headers.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = MergeContentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="operators", name="merge_content", input=input_model.model_dump()
    )
    return MergeContentOutput.model_validate(output_model)
