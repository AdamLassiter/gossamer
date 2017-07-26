#! /usr/bin/python3


class FeistelCipher(object):
    import c_feistel.feistel as cLib

    MODE_ECB = 0
    mode_CBC = 1
    MODE_PCBC = 2
    MODE_CFB = 3
    MODE_OFB = 4
    __modes = [MODE_ECB, mode_CBC, MODE_PCBC, MODE_CFB, MODE_OFB]

    __pad_delimiter = 0xFF
    __pad_byte = 0x00

    def __init__(self, key):
        self.key = key

    def encrypt(self, text, iv, mode):
        def pad(_bytes, len_multiple):
            return _bytes + bytes([self.__pad_delimiter] +
                                  [self.__pad_byte for _ in range((len(_bytes) + 1) % len_multiple)])
        if mode not in self.__modes:
            raise Exception("Error: mode %s not found" % mode)
        _bytes = self.cLib.f_encrypt(bytes(text, 'utf8'), self.key, iv, mode)
        return _bytes.decode('raw_unicode_escape')

    def decrypt(self, text, iv, mode):
        def unpad(_bytes):
            return _bytes.rstrip(self.__pad_byte)[:-1]
        if mode not in self.__modes:
            raise Exception("Error: mode %s not found" % mode)
        _bytes = self.cLib.f_decrypt(
            bytes(text, 'raw_unicode_escape'), self.key, iv, mode)
        return _bytes.decode('utf8')
