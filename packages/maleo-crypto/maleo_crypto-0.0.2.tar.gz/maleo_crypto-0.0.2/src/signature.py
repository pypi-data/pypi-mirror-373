from base64 import b64decode, b64encode
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from typing import Union, overload
from maleo.types.base.misc import BytesOrString
from maleo.types.base.string import OptionalString
from .hash.enums import Mode
from .hash.sha256 import hash
from .key.rsa.enums import KeyType
from .key.rsa.loader import with_pycryptodome


@overload
def sign(message: bytes, key: RsaKey, password: OptionalString = None) -> bytes: ...
@overload
def sign(message: str, key: RsaKey, password: OptionalString = None) -> str: ...
@overload
def sign(
    message: bytes, key: BytesOrString, password: OptionalString = None
) -> bytes: ...
@overload
def sign(message: str, key: BytesOrString, password: OptionalString = None) -> str: ...
def sign(
    message: BytesOrString,
    key: Union[RsaKey, BytesOrString],
    password: OptionalString = None,
) -> BytesOrString:
    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            KeyType.PRIVATE, extern_key=key, passphrase=password
        )
    sha256_hash = hash(Mode.OBJECT, message=message)
    signature = b64encode(pkcs1_15.new(private_key).sign(sha256_hash))
    if isinstance(message, bytes):
        return signature
    else:
        return signature.decode()


@overload
def verify(
    key: RsaKey,
    message: bytes,
    signature: bytes,
) -> bool: ...
@overload
def verify(
    key: RsaKey,
    message: str,
    signature: str,
) -> bool: ...
@overload
def verify(
    key: BytesOrString,
    message: bytes,
    signature: bytes,
) -> bool: ...
@overload
def verify(
    key: BytesOrString,
    message: str,
    signature: str,
) -> bool: ...
def verify(
    key: Union[RsaKey, BytesOrString],
    message: BytesOrString,
    signature: BytesOrString,
) -> bool:
    if isinstance(key, RsaKey):
        public_key = key
    else:
        public_key = with_pycryptodome(KeyType.PUBLIC, extern_key=key)
    sha256_hash = hash(Mode.OBJECT, message=message)
    if isinstance(signature, str):
        signature_bytes = signature.encode()
    else:
        signature_bytes = signature

    try:
        pkcs1_15.new(public_key).verify(sha256_hash, b64decode(signature_bytes))
        return True
    except ValueError:
        return False
