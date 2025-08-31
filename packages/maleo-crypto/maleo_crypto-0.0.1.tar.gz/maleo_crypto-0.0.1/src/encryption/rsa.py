from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey.RSA import RsaKey
from typing import Union, overload
from maleo.types.base.misc import BytesOrString
from maleo.types.base.string import OptionalString
from ..key.rsa.enums import KeyType
from ..key.rsa.loader import with_pycryptodome


@overload
def encrypt(key: RsaKey, plaintext: bytes) -> bytes: ...
@overload
def encrypt(key: RsaKey, plaintext: str) -> str: ...
@overload
def encrypt(key: BytesOrString, plaintext: bytes) -> bytes: ...
@overload
def encrypt(key: BytesOrString, plaintext: str) -> str: ...
def encrypt(
    key: Union[RsaKey, BytesOrString], plaintext: BytesOrString
) -> BytesOrString:
    if isinstance(key, RsaKey):
        public_key = key
    else:
        public_key = with_pycryptodome(KeyType.PUBLIC, extern_key=key)
    cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)

    if isinstance(plaintext, str):
        plaintext_bytes = plaintext.encode()
    else:
        plaintext_bytes = plaintext

    ciphertext_bytes = b64encode(cipher.encrypt(plaintext_bytes))

    if isinstance(plaintext, str):
        return ciphertext_bytes.decode()
    else:
        return ciphertext_bytes


@overload
def decrypt(
    ciphertext: bytes, key: RsaKey, password: OptionalString = None
) -> bytes: ...
@overload
def decrypt(ciphertext: str, key: RsaKey, password: OptionalString = None) -> str: ...
@overload
def decrypt(
    ciphertext: bytes, key: BytesOrString, password: OptionalString = None
) -> bytes: ...
@overload
def decrypt(
    ciphertext: str, key: BytesOrString, password: OptionalString = None
) -> str: ...
def decrypt(
    ciphertext: BytesOrString,
    key: Union[RsaKey, BytesOrString],
    password: OptionalString = None,
) -> BytesOrString:
    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            KeyType.PRIVATE, extern_key=key, passphrase=password
        )
    cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)

    if isinstance(ciphertext, str):
        ciphertext_bytes = ciphertext.encode()
    else:
        ciphertext_bytes = ciphertext

    plaintext_bytes = cipher.decrypt(b64decode(ciphertext_bytes))

    if isinstance(ciphertext, str):
        return plaintext_bytes.decode()
    else:
        return plaintext_bytes
