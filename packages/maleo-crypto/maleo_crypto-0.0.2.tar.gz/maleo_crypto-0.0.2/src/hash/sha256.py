from Crypto.Hash import SHA256
from typing import Literal, Union, overload
from maleo.types.base.misc import BytesOrString
from .enums import Mode


@overload
def hash(
    mode: Literal[Mode.OBJECT],
    *,
    message: BytesOrString,
) -> SHA256.SHA256Hash: ...
@overload
def hash(
    mode: Literal[Mode.DIGEST],
    *,
    message: bytes,
) -> bytes: ...
@overload
def hash(
    mode: Literal[Mode.DIGEST],
    *,
    message: str,
) -> str: ...
def hash(
    mode: Mode,
    *,
    message: BytesOrString,
) -> Union[SHA256.SHA256Hash, BytesOrString]:
    if isinstance(message, str):
        message_bytes = message.encode()
    else:
        message_bytes = message

    hash = SHA256.new(message_bytes)

    if mode is Mode.OBJECT:
        return hash

    if isinstance(message, str):
        return hash.hexdigest()
    else:
        return hash.digest()


@overload
def verify(
    message: BytesOrString,
    message_hash: SHA256.SHA256Hash,
) -> bool: ...
@overload
def verify(
    message: bytes,
    message_hash: bytes,
) -> bool: ...
@overload
def verify(
    message: str,
    message_hash: str,
) -> bool: ...
def verify(
    message: BytesOrString,
    message_hash: Union[SHA256.SHA256Hash, BytesOrString],
) -> bool:
    if not isinstance(message_hash, (bytes, str, SHA256.SHA256Hash)):
        raise TypeError(f"Invalid 'message_hash' type: {type(message_hash)}")

    computed_hash = hash(Mode.OBJECT, message=message)

    if isinstance(message_hash, str):
        return computed_hash.hexdigest() == message_hash
    elif isinstance(message_hash, bytes):
        return computed_hash.digest() == message_hash
    elif isinstance(message_hash, SHA256.SHA256Hash):
        return computed_hash.digest() == message_hash.digest()
