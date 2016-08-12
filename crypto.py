from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

from declarative import accepts, returns

# TODO: Test module
# TODO: Extract necessary pyCrypto modules to local folder?
# TODO: SHA2 / SHA3 choice
# TODO: RSA / NTRUEncrypt choice
# IDEA: Symmetric algo. choice?


@accepts(int)
@returns(str)
def NewKey(length):
    # Uses Random
    return Random.new().read(length)


class Hash:
    # Uses SHA512

    def __init__(self):
        pass

    @accepts(str, n=int)
    @returns(str)
    def digest(self, text, n=1024):
        hash_obj = SHA512.new(text)
        for i in xrange(n - 1):
            hash_obj = SHA512.new(hash_obj.digest())
        return hash_obj.digest()


class SymmetricEncryption:
    # Uses AES in CFB block mode

    @accepts(strength=int, key=str)
    def __init__(self, strength=128, key=""):
        self.key = key if key else NewKey(strength >> 3)  # bits -> bytes

    def __str__(self):
        return self.key

    @accepts(str)
    @returns(str)
    def encrypt(self, text):
        iv = NewKey(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return iv + cipher.encrypt(text)

    @accepts(str)
    @returns(str)
    def decrypt(self, text):
        iv, text = text[:AES.block_size], text[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return cipher.decrypt(text)


class AsymmetricEncryption:
    # Uses RSA

    @accepts(strength=int, key=str)
    def __init__(self, strength=2048, key=""):
        self.key = RSA.importKey(key) if key else RSA.generate(strength)

    def __repr__(self):
        return self.key.privatekey().exportKey()

    def __str__(self):
        return self.key.publickey().exportKey()

    @accepts(str)
    @returns(str)
    def encrypt(self, text):
        return self.key.encrypt(text, "")[0]

    @accepts(str)
    @returns(str)
    def decrypt(self, text):
        return self.key.decrypt(text)


class SaltedPadding:
    # Uses NewKey

    @accepts(padding_width=int, control_char=int)
    def __init__(self, padding_width=32, control_char=255):
        self.padding_width = padding_width
        self.control_char = chr(control_char)
        self.control_ord = control_char

    @accepts(str)
    @returns(str)
    def pad(self, text):
        assert self.padding_width - len(text) > 0
        text += self.control_char
        salt = NewKey(self.padding_width - len(text))
        salt = salt.replace(self.control_char, chr(
            (self.control_ord + 1) % 256))
        return text + salt

    @accepts(str)
    @returns(str)
    def unpad(self, text):
        assert len(text) == self.padding_width
        control_char_pos = -(1 + reversed(text).index(self.control_char))
        return text[:control_char_pos]


class Signature:
    # Uses AsymmetricEncryption

    @accepts(strength=int, key=str)
    def __init__(self, strength=2048, key=""):
        self.key = AsymmetricEncryption(strength=strength, key=key)

    def __repr__(self):
        return self.key.privatekey().exportKey()

    def __str__(self):
        return self.key.publickey().exportKey()

    def __eq__(self, other):
        return str(self) == str(other)

    @accepts(str)
    @returns(str)
    def sign(self, text):
        return self.key.encrypt(Hash().digest(text))

    @accepts(str, str)
    @returns(bool)
    def verify(self, signature, text):
        return self.key.decrypt(signature) == Hash().digest(text)


class HashChain:
    # Uses Hash

    def __init__(self):
        self.my_new_raw = NewKey(64)
        self.my_new_hash = Hash().digest(self.my_new_raw)
        self.my_old_raw = None
        self.your_hash = None

    @returns(str)
    def chain(self):
        self.my_old_raw = self.my_new_raw
        self.my_new_raw = NewKey(64)
        self.my_new_hash = Hash().digest(self.my_new_raw)
        return self.my_old_raw + self.my_new_hash

    @accepts(str)
    @returns(bool)
    def verify(self, hashes):
        if self.your_hash:
            your_raw = hashes[:64]
            your_hash = hashes[64:]
            ret = Hash().digest(your_raw) == self.your_hash
        else:
            ret = False
        self.your_hash = your_hash
        return ret

if __name__ == '__main__':
    import tests
    tests.test_crypto()
