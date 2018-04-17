#! /usr/bin/env python3

from binascii import a2b_base64 as encode, b2a_base64 as decode
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

    def __init__(self, key: str = None, iv: str = None, mode: int = MODE_CBC) -> None:
        self._key = key if key else self.keygen()
        self.iv = iv if iv else bytes(''.join([chr(randint(0, 255)) for _ in range(16)]), 'utf8')
        if mode not in self.__modes:
            raise Exception("Error: mode %s not found" % mode)
        self.mode = mode

    @staticmethod
    def keygen() -> str:
        return decode(bytes((randint(0, 255) for _ in range(8))))

    def key(self) -> str:
        return self._key

    def encrypt(self, text: str) -> str:
        def pad(_bytes: bytes, len_multiple: int):
            return _bytes + bytes([self.__pad_delimiter] +
                                  [self.__pad_byte for _ in range((len(_bytes) + 1) % len_multiple)])
        _bytes = self.cLib.encrypt_(bytes(text, 'utf8'), self.key, self.iv, self.mode)
        return decode(_bytes)

    def decrypt(self, text: str) -> str:
        def unpad(_bytes):
            return _bytes.rstrip(self.__pad_byte)[:-1]
        _bytes = self.cLib.decrypt_(bytes(encode(text)), self.key, self.iv, self.mode)
        return decode(_bytes)
