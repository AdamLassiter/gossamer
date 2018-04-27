#! /usr/bin/env python3

from __future__ import annotations
from base64 import b64encode as encode, b64decode as decode
from random import randint

from abcs import SymmetricCipher


class FeistelCipher(SymmetricCipher):
    import c_feistel.feistel as cLib

    MODE_ECB = 0
    MODE_CBC = 1
    MODE_PCBC = 2
    MODE_CFB = 3
    MODE_OFB = 4
    __modes = [MODE_ECB, MODE_CBC, MODE_PCBC, MODE_CFB, MODE_OFB]

    __pad_delimiter = 0xFF
    __pad_byte = 0x00
    KEY_LEN = 16
    IV_LEN = 16

    def __init__(self, key: str = None, iv: str = None, mode: int = MODE_CBC) -> None:
        self.key = key if key else self.keygen()
        self.iv = iv if iv else ''.join([chr(randint(0, 255)) for _ in range(self.IV_LEN)])
        if mode not in self.__modes:
            raise Exception("Error: mode %s not found" % mode)
        self.mode = mode

    @property
    def key(self) -> str:
        return self._key
    @key.setter
    def key(self, value: str) -> None:
        self._key = value

    @classmethod
    def keygen(cls) -> str:
        return ''.join([chr(randint(0, 255)) for _ in range(cls.KEY_LEN)])

    def __encrypt_bytes(self, b: bytes) -> bytes:
        return self.cLib.encrypt_(b, self.key, self.iv, self.mode)

    def encrypt(self, text: str) -> str:
        def pad(_bytes: bytes, len_multiple: int):
            return _bytes + bytes([self.__pad_delimiter] +
                                  [self.__pad_byte for _ in range((len(_bytes) + 1) % len_multiple)])
        return str(encode(self.__encrypt_bytes(bytes(text, 'utf8'))))

    def __decrypt_bytes(self, b: bytes) -> bytes:
        return self.cLib.decrypt_(b, self.key, self.iv, self.mode)

    def decrypt(self, text: str) -> str:
        def unpad(_bytes):
            return _bytes.rstrip(self.__pad_byte)[:-1]
        return str(self.__decrypt_bytes(decode(text)))
