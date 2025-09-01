"""This module contains helper functions for encrypting and decrypting data."""

import os
from binascii import unhexlify

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from zmp_authentication_provider.setting import auth_default_settings

str_key = auth_default_settings.basic_auth_encryption_key
key = unhexlify(str_key)  # 256-bit key
iv = os.urandom(16)  # 128-bit IV


def encrypt(data: str) -> bytes:
    """Encrypt the data."""
    data_bytes = data.encode("utf-8")

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return iv + encrypted_data


def decrypt(encrypted_data: bytes) -> str:
    """Decrypt the data."""
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data_bytes = unpadder.update(padded_data) + unpadder.finalize()

    return data_bytes.decode("utf-8")
