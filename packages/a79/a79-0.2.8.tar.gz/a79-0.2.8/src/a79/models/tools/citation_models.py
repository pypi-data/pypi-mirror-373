from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CitationType(str, Enum):
    """Supported citation types."""

    TABLE_CELL = "tableCell"
    EXTERNAL_LINK = "externalLink"
    INTERNAL_DOCUMENT = "internalDocument"
    VIDEO_CLIP = "videoClip"
    AUDIO_CLIP = "audioClip"


class TableCellMetadata(BaseModel):
    """Metadata for table cell citations."""

    table_id: str
    row_index: int
    col_index: int


class ExternalLinkMetadata(BaseModel):
    """Metadata for external link citations."""

    url: str
    title: Optional[str] = None


class InternalDocumentMetadata(BaseModel):
    """Metadata for internal document citations."""

    document_id: str
    title: Optional[str] = None


class VideoClipMetadata(BaseModel):
    """Metadata for video clip citations."""

    video_url: str
    start_time: int  # in seconds
    end_time: int  # in seconds


class AudioClipMetadata(BaseModel):
    """Metadata for audio clip citations."""

    audio_url: str | None = None
    start_time: int  # in seconds
    end_time: int  # in seconds


class Citation(BaseModel):
    """
    A citation that can reference different types of content (tables, links, documents,
    video clips, etc).
    """

    id: str = Field(..., description="Unique identifier for the citation")
    number: int = Field(..., description="Citation number for display ordering")
    type: CitationType = Field(..., description="Type of citation")

    # Metadata fields for different citation types
    table_cell_metadata: Optional[TableCellMetadata] = Field(
        default=None, description="Metadata for table cell citations"
    )
    external_link_metadata: Optional[ExternalLinkMetadata] = Field(
        default=None, description="Metadata for external link citations"
    )
    # TODO: Add metadata for internal document, video clip, and audio clip citations

    # internal_document_metadata: Optional[InternalDocumentMetadata] = Field(
    #     default=None, description="Metadata for internal document citations"
    # )
    # video_clip_metadata: Optional[VideoClipMetadata] = Field(
    #     default=None, description="Metadata for video clip citations"
    # )
    # audio_clip_metadata: Optional[AudioClipMetadata] = Field(
    #     default=None, description="Metadata for audio clip citations"
    # )

    class Config:
        exclude_none = True

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_metadata()

    def _validate_metadata(self) -> None:
        """Validate that the appropriate metadata is present for the citation type."""
        metadata_map = {
            CitationType.TABLE_CELL: (self.table_cell_metadata, TableCellMetadata),
            CitationType.EXTERNAL_LINK: (
                self.external_link_metadata,
                ExternalLinkMetadata,
            ),
            # TODO: Add metadata for internal document, video clip, and audio clip
            # CitationType.INTERNAL_DOCUMENT: (
            #     self.internal_document_metadata,
            #     InternalDocumentMetadata,
            # ),
            # CitationType.VIDEO_CLIP: (self.video_clip_metadata, VideoClipMetadata),
            # CitationType.AUDIO_CLIP: (self.audio_clip_metadata, AudioClipMetadata),
        }

        metadata, expected_type = metadata_map[self.type]
        if metadata is None:
            raise ValueError(
                f"Citation of type {self.type} requires {expected_type.__name__}"
            )

    @classmethod
    def create_table_cell_citation(
        cls, id: str, number: int, table_id: str, row_index: int, col_index: int
    ) -> "Citation":
        """Create a table cell citation."""
        return cls(
            id=id,
            number=number,
            type=CitationType.TABLE_CELL,
            table_cell_metadata=TableCellMetadata(
                table_id=table_id, row_index=row_index, col_index=col_index
            ),
        )

    @classmethod
    def create_external_link_citation(
        cls, id: str, number: int, url: str, title: Optional[str] = None
    ) -> "Citation":
        """Create an external link citation."""
        return cls(
            id=id,
            number=number,
            type=CitationType.EXTERNAL_LINK,
            external_link_metadata=ExternalLinkMetadata(url=url, title=title),
        )

    @classmethod
    def create_internal_document_citation(
        cls, id: str, number: int, document_id: str, title: Optional[str] = None
    ) -> "Citation":
        """Create an internal document citation."""
        return cls(
            id=id,
            number=number,
            type=CitationType.INTERNAL_DOCUMENT,
            internal_document_metadata=InternalDocumentMetadata(
                document_id=document_id, title=title
            ),
        )

    @classmethod
    def create_video_clip_citation(
        cls, id: str, number: int, video_url: str, start_time: int, end_time: int
    ) -> "Citation":
        """Create a video clip citation."""
        return cls(
            id=id,
            number=number,
            type=CitationType.VIDEO_CLIP,
            video_clip_metadata=VideoClipMetadata(
                video_url=video_url, start_time=start_time, end_time=end_time
            ),
        )

    @classmethod
    def create_audio_clip_citation(
        cls, id: str, number: int, audio_url: str, start_time: int, end_time: int
    ) -> "Citation":
        """Create an audio clip citation."""
        return cls(
            id=id,
            number=number,
            type=CitationType.AUDIO_CLIP,
            audio_clip_metadata=AudioClipMetadata(
                audio_url=audio_url, start_time=start_time, end_time=end_time
            ),
        )
