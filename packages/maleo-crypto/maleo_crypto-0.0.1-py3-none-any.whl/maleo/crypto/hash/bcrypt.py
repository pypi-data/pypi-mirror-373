import bcrypt
from typing import overload
from maleo.types.base.misc import BytesOrString


@overload
def hash(
    password: bytes,
) -> bytes: ...
@overload
def hash(
    password: str,
) -> str: ...
def hash(
    password: BytesOrString,
) -> BytesOrString:
    if isinstance(password, str):
        password_bytes = password.encode()
    else:
        password_bytes = password

    hash = bcrypt.hashpw(password=password_bytes, salt=bcrypt.gensalt())

    if isinstance(password, str):
        return hash.decode()

    return hash


@overload
def verify(
    password: bytes,
    hash: bytes,
) -> bool: ...
@overload
def verify(
    password: str,
    hash: str,
) -> bool: ...
def verify(
    password: BytesOrString,
    hash: BytesOrString,
) -> bool:
    if isinstance(password, str):
        password_bytes = password.encode()
    else:
        password_bytes = password

    if isinstance(hash, str):
        hash_bytes = hash.encode()
    else:
        hash_bytes = hash

    return bcrypt.checkpw(password=password_bytes, hashed_password=hash_bytes)
