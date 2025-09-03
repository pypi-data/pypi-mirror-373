import base64
import typing as t

from pydantic import PlainSerializer, PlainValidator, WithJsonSchema


def serialize_base64bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def validate_base64bytes(value: t.Any) -> bytes:
    match value:
        case bytes():
            return value
        case str():
            return base64.b64decode(value)
        case _:
            raise ValueError(f"Invalid input type: {type(value)}")


Base64Bytes = t.Annotated[
    bytes,
    PlainValidator(validate_base64bytes),
    PlainSerializer(serialize_base64bytes),
    WithJsonSchema({"type": "string", "format": "base64"}),
]
