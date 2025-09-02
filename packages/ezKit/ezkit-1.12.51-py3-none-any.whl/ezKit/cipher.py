"""Cipher Library"""

# https://docs.python.org/3.10/library/hashlib.html
# https://www.pycrypto.org/
# https://stackoverflow.com/a/21928790
# pip install pycryptodome
import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES
from loguru import logger


class AESCipher:
    """AESCipher"""

    def __init__(self, key: str = "vB7DoRm9C2Kd", algorithm: str = "sha256"):

        self.bs = AES.block_size

        # dir(hashlib)
        match True:
            case True if algorithm == "md5":
                self.key = hashlib.md5(key.encode()).digest()
            case True if algorithm == "sha1":
                self.key = hashlib.sha1(key.encode()).digest()
            case True if algorithm == "sha224":
                self.key = hashlib.sha224(key.encode()).digest()
            case True if algorithm == "sha256":
                self.key = hashlib.sha256(key.encode()).digest()
            case True if algorithm == "sha384":
                self.key = hashlib.sha384(key.encode()).digest()
            case True if algorithm == "sha512":
                self.key = hashlib.sha512(key.encode()).digest()
            case True if algorithm == "sha3_224":
                self.key = hashlib.sha3_224(key.encode()).digest()
            case True if algorithm == "sha3_256":
                self.key = hashlib.sha3_256(key.encode()).digest()
            case True if algorithm == "sha3_384":
                self.key = hashlib.sha3_384(key.encode()).digest()
            case True if algorithm == "sha3_512":
                self.key = hashlib.sha3_512(key.encode()).digest()
            # case True if algorithm == 'shake_128':
            #     self.key = hashlib.shake_128(key.encode()).digest()
            # case True if algorithm == 'shake_256':
            #     self.key = hashlib.shake_256(key.encode()).digest()
            case _:
                self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw: str) -> str | None:
        try:
            raw = self._pad(raw)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return base64.b64encode(iv + cipher.encrypt(raw.encode())).decode("utf-8")
        except Exception as e:
            logger.exception(e)
            return None

    def decrypt(self, enc: str) -> str | None:
        try:
            enc_bytes = base64.b64decode(enc)
            iv = enc_bytes[: AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return self._unpad(cipher.decrypt(enc_bytes[AES.block_size :])).decode(
                "utf-8"
            )
        except Exception as e:
            logger.exception(e)
            return None

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s: bytes) -> bytes:
        return s[: -ord(s[len(s) - 1 :])]
