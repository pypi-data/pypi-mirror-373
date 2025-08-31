import jwt
from collections.abc import Iterable, Sequence
from Crypto.PublicKey.RSA import RsaKey
from datetime import timedelta
from typing import Union, overload
from maleo.types.base.dict import StringToAnyDict
from maleo.types.base.misc import BytesOrString
from maleo.types.base.string import OptionalString
from .key.rsa.enums import KeyType
from .key.rsa.loader import with_pycryptodome


@overload
def encode(
    payload: StringToAnyDict,
    key: RsaKey,
) -> str: ...
@overload
def encode(
    payload: StringToAnyDict,
    key: BytesOrString,
    *,
    password: OptionalString = None,
) -> str: ...
def encode(
    payload: StringToAnyDict,
    key: Union[RsaKey, BytesOrString],
    *,
    password: OptionalString = None,
) -> str:
    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            KeyType.PRIVATE, extern_key=key, passphrase=password
        )

    token = jwt.encode(
        payload=payload,
        key=private_key.export_key(),
        algorithm="RS256",
    )

    return token


def decode(
    token: str,
    key: Union[RsaKey, BytesOrString],
    audience: str | Iterable[str] | None = None,
    subject: str | None = None,
    issuer: str | Sequence[str] | None = None,
    leeway: float | timedelta = 0,
) -> StringToAnyDict:
    if isinstance(key, RsaKey):
        public_key = key
    else:
        public_key = with_pycryptodome(KeyType.PRIVATE, extern_key=key)

    payload = jwt.decode(
        jwt=token,
        key=public_key.export_key(),
        algorithms=["RS256"],
        audience=audience,
        subject=subject,
        issuer=issuer,
        leeway=leeway,
    )

    return payload
