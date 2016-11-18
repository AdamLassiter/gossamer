from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.Cipher import AES
from ntruencrypt import NTRUCipher
from declarative import accepts, returns
from debug import debug

# TODO Extract necessary pyCrypto modules to local folder?
# TODO SHA2 / SHA3 choice
# TODO RSA / NTRUEncrypt choice
# IDEA Symmetric algo. choice?
# TODO Implement DHKE or use NTRU... Fuck pyCrypto


@accepts(int)
@returns(str)
def NewKey(length):
    # Uses Random
    return Random.new().read(length)


class Hash:

    def __init__(self):
        pass

    @accepts(str, n=int)
    @returns(str)
    def digest(self, text, n=1):
        hash_obj = SHA512.new(text)
        for i in xrange(n - 1):
            hash_obj = SHA512.new(hash_obj.digest())
        return hash_obj.digest()


class SymmetricEncryption:

    @accepts(strength=int, key=str)
    def __init__(self, strength=128, key=""):
        self.key = key if key else NewKey(strength >> 3)  # bits -> bytes

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


class AsymmetricEncryption(NTRUCipher):

    @accepts(keypair=dict)
    def __init__(self, keypair=None):
        params = {"N": 787, "d": 22, "Hw": 462, "p": 3, "q": 2048}
        super(AsymmetricEncryption, self).__init__(params, keypair=keypair)


class Signature(AsymmetricEncryption):

    @accepts(str)
    @returns(str)
    def sign(self, text):
        return self.encrypt(Hash().digest(text))

    @accepts(str, str)
    @returns(bool)
    def verify(self, signature, text):
        return self.decrypt(signature) == Hash().digest(text)


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
