from Crypto.Hash import HMAC, SHA256
from typing import Literal, Union, overload
from maleo.types.base.misc import BytesOrString
from .enums import Mode


@overload
def hash(
    mode: Literal[Mode.OBJECT],
    *,
    key: BytesOrString,
    message: BytesOrString,
) -> HMAC.HMAC: ...
@overload
def hash(
    mode: Literal[Mode.DIGEST],
    *,
    key: bytes,
    message: bytes,
) -> bytes: ...
@overload
def hash(
    mode: Literal[Mode.DIGEST],
    *,
    key: str,
    message: str,
) -> str: ...
def hash(
    mode: Mode = Mode.DIGEST,
    *,
    key: BytesOrString,
    message: BytesOrString,
) -> Union[HMAC.HMAC, BytesOrString]:
    if isinstance(key, str):
        key_bytes = key.encode()
    else:
        key_bytes = key

    if isinstance(message, str):
        message_bytes = message.encode()
    else:
        message_bytes = message

    hash = HMAC.new(key=key_bytes, msg=message_bytes, digestmod=SHA256)

    if mode is Mode.OBJECT:
        return hash

    if isinstance(message, str):
        return hash.hexdigest()
    else:
        return hash.digest()


@overload
def verify(
    key: bytes,
    message: bytes,
    message_hash: HMAC.HMAC,
) -> bool: ...
@overload
def verify(
    key: bytes,
    message: bytes,
    message_hash: bytes,
) -> bool: ...
@overload
def verify(
    key: str,
    message: str,
    message_hash: str,
) -> bool: ...
def verify(
    key: BytesOrString,
    message: BytesOrString,
    message_hash: Union[HMAC.HMAC, BytesOrString],
) -> bool:
    if not isinstance(message_hash, (bytes, str, HMAC.HMAC)):
        raise TypeError(f"Invalid 'message_hash' type: {type(message_hash)}")

    computed_hash = hash(Mode.OBJECT, key=key, message=message)

    if isinstance(message_hash, str):
        return computed_hash.hexdigest() == message_hash
    elif isinstance(message_hash, bytes):
        return computed_hash.digest() == message_hash
    elif isinstance(message_hash, HMAC.HMAC):
        return computed_hash.digest() == message_hash.digest()
