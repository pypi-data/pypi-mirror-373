from enum import StrEnum


class KeyType(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"


class Loader(StrEnum):
    CRYPTOGRAPHY = "cryptography"
    PYCRYPTODOME = "pycryptodome"
