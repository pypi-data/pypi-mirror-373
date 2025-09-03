from pydantic import BaseModel, Field

from . import ToolOutput


class ParseDocumentInput(BaseModel):
    document_input: str = Field(
        default="",
        json_schema_extra={"mandatory": True},
        description=(
            "URL of the document to download and parse, or the document content itself"
        ),
    )
    content_type: str = Field(
        default="text/plain",
        description=(
            "Content type of the document "
            "(auto-detected for URLs, optional for direct content)"
        ),
    )


class ParseDocumentOutput(ToolOutput):
    parsed_text: str = Field(
        default="", description="The parsed text content from the document"
    )
