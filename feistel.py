#! /usr/bin/env python3

from binascii import a2b_base64 as encode, b2a_base64 as decode

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

    def __init__(self, key: str) -> None:
        self._key = key

    def key(self) -> str:
        return self._key

    def encrypt(self, text: str, iv: str, mode: int) -> str:
        def pad(_bytes: bytes, len_multiple: int):
            return _bytes + bytes([self.__pad_delimiter] +
                                  [self.__pad_byte for _ in range((len(_bytes) + 1) % len_multiple)])
        if mode not in self.__modes:
            raise Exception("Error: mode %s not found" % mode)
        _bytes = self.cLib.f_encrypt(bytes(text, 'utf8'), self._key, iv, mode)
        return decode(_bytes)

    def decrypt(self, text: str, iv: str, mode: int) -> str:
        def unpad(_bytes):
            return _bytes.rstrip(self.__pad_byte)[:-1]
        if mode not in self.__modes:
            raise Exception("Error: mode %s not found" % mode)
        _bytes = self.cLib.f_decrypt(bytes(encode(text)), self._key, iv, mode)
        return decode(_bytes)
