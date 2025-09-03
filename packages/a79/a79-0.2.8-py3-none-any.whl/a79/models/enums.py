import os
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ContentTypeInfo:
    mime_type: str
    extensions: list[str]


class ContentType(Enum):
    DOC = ContentTypeInfo(mime_type="application/msword", extensions=["doc"])
    DOCX = ContentTypeInfo(
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        extensions=["docx"],
    )
    CSV = ContentTypeInfo(mime_type="text/csv", extensions=["csv"])
    PDF = ContentTypeInfo(mime_type="application/pdf", extensions=["pdf"])
    PPTX = ContentTypeInfo(
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        extensions=["pptx"],
    )
    XLSX = ContentTypeInfo(
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        extensions=["xlsx", "xlsm"],
    )
    PPT = ContentTypeInfo(mime_type="application/vnd.ms-powerpoint", extensions=["ppt"])
    HTML = ContentTypeInfo(mime_type="text/html", extensions=["html", "htm"])
    PLAIN_TEXT = ContentTypeInfo(
        mime_type="text/plain", extensions=["md", "markdown", "txt", "text"]
    )
    PNG = ContentTypeInfo(mime_type="image/png", extensions=["png"])
    JPEG = ContentTypeInfo(mime_type="image/jpeg", extensions=["jpg", "jpeg"])
    MP3 = ContentTypeInfo(mime_type="audio/mpeg", extensions=["mp3"])
    MPGA = ContentTypeInfo(mime_type="audio/mpeg", extensions=["mpga"])
    WAV = ContentTypeInfo(mime_type="audio/wav", extensions=["wav"])
    M4A = ContentTypeInfo(mime_type="audio/mp4", extensions=["m4a"])
    OGG = ContentTypeInfo(mime_type="audio/ogg", extensions=["ogg"])
    MPEG = ContentTypeInfo(mime_type="video/mpeg", extensions=["mpeg", "mpg"])
    MP4 = ContentTypeInfo(mime_type="video/mp4", extensions=["mp4"])
    WEBM = ContentTypeInfo(mime_type="video/webm", extensions=["webm"])
    ZIP = ContentTypeInfo(mime_type="application/zip", extensions=["zip"])
    DEFAULT_UPLOAD_TYPE = ContentTypeInfo(
        mime_type="application/octet-stream", extensions=[]
    )
    EML = ContentTypeInfo(mime_type="message/rfc822", extensions=["eml"])
    VTT = ContentTypeInfo(mime_type="text/vtt", extensions=["vtt"])

    @classmethod
    def get_all_supported_extensions(cls) -> set[str]:
        """Returns a set of all supported file extensions."""
        extensions = set()
        for content_type in cls:
            extensions.update(content_type.value.extensions)
        return extensions

    @classmethod
    def get_all_mime_types(cls) -> set[str]:
        """Returns a set of all supported file extensions."""
        extensions = set()
        for content_type in cls:
            extensions.add(content_type.value.mime_type)
        return extensions

    @classmethod
    def from_filepath(cls, filepath: str) -> "ContentType":
        _, extension = os.path.splitext(filepath)
        return cls.from_extension(extension)

    @classmethod
    def from_extension(cls, extension: str) -> "ContentType":
        """
        Get ContentType from file extension.
        Raises ValueError if extension is not supported.
        """
        extension = extension.lower().lstrip(".")
        for content_type in cls:
            if extension in content_type.value.extensions:
                return content_type
        raise ValueError(f"Unsupported file extension: {extension}")

    @classmethod
    def from_mime_type(cls, mime_type: str) -> "ContentType":
        """
        Get ContentType from MIME type.
        Raises ValueError if MIME type is not supported.
        """
        for content_type in cls:
            if content_type.value.mime_type == mime_type:
                return content_type
        raise ValueError(f"Unsupported MIME type: {mime_type}")


class RunStatus(str, Enum):
    # NOTE: When new statuses are added, alembic does not pick up the new enum
    # values. So, we need to create an alembic migration to include the
    # new statuses.
    UNDEFINED = "undefined"
    NOT_STARTED = "not_started"
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"
    PARTIAL_SUCCESS = "partial_success"
    SKIPPED = "skipped"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class CustomDataType(str, Enum):
    TEXT = "text"
    BOOL = "bool"
    EMAIL = "email"
    DATETIME = "datetime"
    TIME = "time"
    DATE = "date"
    NUMBER = "number"
    DOCUMENT = "document"
    FOLDER = "folder"
    INPUT_TEMPLATE = "input_template"
    URL = "url"
    EXCEL = "excel"
    ENUM = "enum"


class ModelName(str, Enum):
    """
    Enum class for standardized model names used across the codebase.
    """

    GEMINI_FLASH = "gemini/gemini-2.5-flash"
    GEMINI_PRO = "gemini/gemini-2.5-pro"
    GPT_4O = "gpt-4o"
    GPT_4_1 = "openai/gpt-4.1"
    CLAUDE_SONNET = "claude-3-5-sonnet-20240620"
    GPT_4O_MINI = "gpt-4o-mini"
    O4_MINI = "o4-mini"
    O3 = "o3"
    CLAUDE_SONNET_4 = "anthropic/claude-sonnet-4"
    MOONSHOT_KIMI_K2 = "moonshotai/kimi-k2"
    OPENAI_OSS = "openai/gpt-oss-120b"
