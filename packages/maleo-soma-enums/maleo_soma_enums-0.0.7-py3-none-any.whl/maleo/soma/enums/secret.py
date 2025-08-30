from enum import Enum, StrEnum


class SecretFormat(StrEnum):
    BYTES = "bytes"
    STRING = "string"


class SecretFormatType(Enum):
    BYTES = bytes
    STRING = str
