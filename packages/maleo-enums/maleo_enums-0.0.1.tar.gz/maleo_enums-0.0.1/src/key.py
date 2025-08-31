from enum import StrEnum


class RSAKeyType(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"


class KeyFormat(StrEnum):
    BYTES = "bytes"
    STRING = "string"
