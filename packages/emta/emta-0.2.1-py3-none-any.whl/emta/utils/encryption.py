"""Encryption utilities for Eastmoney API."""

import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

# RSA Public Key for Eastmoney API encryption
RSA_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDHdsyxT66pDG4p73yope7jxA92
c0AT4qIJ/xtbBcHkFPK77upnsfDTJiVEuQDH+MiMeb+XhCLNKZGp0yaUU6GlxZdp
+nLW8b7Kmijr3iepaDhcbVTsYBWchaWUXauj9Lrhz58/6AE/NF0aMolxIGpsi+ST
2hSHPu3GSXMdhPCkWQIDAQAB
-----END PUBLIC KEY-----
"""


def encrypt_password(password: str) -> str:
    """Encrypt password using Eastmoney's RSA public key.

    Args:
        password: Plain text password

    Returns:
        Base64 encoded encrypted password
    """
    public_key = serialization.load_pem_public_key(RSA_PUBLIC_KEY.encode("utf-8"))
    # Type cast to RSAPublicKey since we know it is one
    rsa_public_key: RSAPublicKey = public_key  # type: ignore[assignment]
    encrypted = rsa_public_key.encrypt(password.encode(), PKCS1v15())
    return base64.b64encode(encrypted).decode("utf-8")
