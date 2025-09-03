# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.document_models import ParseDocumentInput, ParseDocumentOutput

__all__ = ["ParseDocumentInput", "ParseDocumentOutput", "parse_document"]


def parse_document(
    *, document_input: str = DEFAULT, content_type: str = DEFAULT
) -> ParseDocumentOutput:
    """
    Parse document content, either from a URL or direct input.

    This function supports various document types including:
    - PDF
    - DOCX
    - DOC
    - HTML
    - PPTX
    - CSV
    - Plain text
    - Email (EML)

    The node automatically detects whether the input is a URL or direct content.
    For URLs, the content type is automatically detected if not specified.
    For direct content, the content type can be specified or will default to PDF.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ParseDocumentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="document", name="parse_document", input=input_model.model_dump()
    )
    return ParseDocumentOutput.model_validate(output_model)
