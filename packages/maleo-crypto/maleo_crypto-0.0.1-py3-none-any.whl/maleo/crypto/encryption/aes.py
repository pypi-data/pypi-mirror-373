import os
from base64 import b64decode, b64encode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from typing import Tuple, Union, overload
from maleo.types.base.misc import BytesOrString


@overload
def encrypt(plaintext: bytes) -> Tuple[bytes, bytes, bytes]: ...
@overload
def encrypt(plaintext: str) -> Tuple[str, str, str]: ...
def encrypt(
    plaintext: BytesOrString,
) -> Union[Tuple[bytes, bytes, bytes], Tuple[str, str, str]]:
    if not isinstance(plaintext, (bytes, str)):
        raise TypeError(f"Invalid type for 'plaintext': {type(plaintext)}")

    key_bytes = os.urandom(32)
    initialization_vector_bytes = os.urandom(16)

    cipher = Cipher(
        algorithm=algorithms.AES256(key_bytes),
        mode=modes.CFB(initialization_vector_bytes),
        backend=default_backend(),
    )
    encryptor = cipher.encryptor()

    if isinstance(plaintext, str):
        plaintext_bytes = plaintext.encode()
    else:
        plaintext_bytes = plaintext

    ciphertext_bytes = b64encode(
        encryptor.update(plaintext_bytes) + encryptor.finalize()
    )

    key_bytes = b64encode(key_bytes)
    initialization_vector_bytes = b64encode(initialization_vector_bytes)

    if isinstance(plaintext, str):
        return (
            key_bytes.decode(),
            initialization_vector_bytes.decode(),
            ciphertext_bytes.decode(),
        )

    if isinstance(plaintext, bytes):
        return (key_bytes, initialization_vector_bytes, ciphertext_bytes)


@overload
def decrypt(key: bytes, initialization_vector: bytes, ciphertext: bytes) -> bytes: ...
@overload
def decrypt(key: str, initialization_vector: str, ciphertext: str) -> str: ...
def decrypt(
    key: BytesOrString, initialization_vector: BytesOrString, ciphertext: BytesOrString
) -> BytesOrString:
    if not isinstance(key, (bytes, str)):
        raise TypeError(f"Invalid type for 'key': {type(key)}")

    if isinstance(key, str):
        key_bytes = key.encode()
    else:
        key_bytes = key

    key_bytes = b64decode(key_bytes)

    if not isinstance(initialization_vector, (bytes, str)):
        raise TypeError(
            f"Invalid type for 'initialization_vector': {type(initialization_vector)}"
        )

    if isinstance(initialization_vector, str):
        initialization_vector_bytes = initialization_vector.encode()
    else:
        initialization_vector_bytes = initialization_vector

    initialization_vector_bytes = b64decode(initialization_vector_bytes)

    if not isinstance(ciphertext, (bytes, str)):
        raise TypeError(f"Invalid type for 'ciphertext': {type(ciphertext)}")

    if isinstance(ciphertext, str):
        ciphertext_bytes = ciphertext.encode()
    else:
        ciphertext_bytes = ciphertext

    ciphertext_bytes = b64decode(ciphertext_bytes)

    cipher = Cipher(
        algorithm=algorithms.AES256(key_bytes),
        mode=modes.CFB(initialization_vector_bytes),
        backend=default_backend(),
    )
    decryptor = cipher.decryptor()

    plaintext_bytes = decryptor.update(ciphertext_bytes) + decryptor.finalize()

    if isinstance(ciphertext, str):
        return plaintext_bytes.decode()

    if isinstance(ciphertext, bytes):
        return plaintext_bytes
