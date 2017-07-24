#! /usr/bin/python3
from copy import deepcopy


class KeccakHash:
    import c_keccak.keccak as cLib

    def __init__(self, rate, capacity):
        self.cLib.new_hash(self, rate, capacity)

    def __squeeze(self):
        return self.cLib.squeeze(self)

    def __absorb(self, bytes):
        self.cLib.absorb(self, bytes)

    def copy(self):
        return deepcopy(self)

    def update(self, s):
        self.__absorb(bytes(s, 'utf8'))

    def digest(self):
        finalised = self.copy()
        digest = finalised.__squeeze()
        return digest.decode('raw_unicode_escape')

    def hexdigest(self):
        finalised = self.copy()
        digest = finalised.__squeeze()
        return digest.hex()

    @staticmethod
    def preset(rate, capacity):
        """
        Returns a factory function for the given bitrate, sponge capacity and output length.
        The function accepts an optional initial input, ala hashlib.
        """
        def create(initial_input=None):
            h = KeccakHash(rate, capacity)
            if initial_input is not None:
                h.update(initial_input)
            return h
        return create


# SHA3 parameter presets
Keccak224 = KeccakHash.preset(1152, 448)
Keccak256 = KeccakHash.preset(1088, 512)
Keccak384 = KeccakHash.preset(832, 768)
Keccak512 = KeccakHash.preset(576, 1024)
