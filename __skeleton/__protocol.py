from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from struct import pack, unpack


RSA_STRENGTH = 1 << 11
AES_STRENGTH = 1 << 7
HASHCHAIN_LENGTH = 1 << 16


# Protocol-specific error
class ProtocolError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return self.value


# Compromised security warning
class SecurityError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return self.value


# pyCrypto is stupid...
def rsa_encrypt(keypair, data):
    return keypair.encrypt(data, "")[0]
def rsa_decrypt(keypair, data):
    return keypair.decrypt(data)


def buffered(string, size):
    for n in range(len(string) // size + 1):
        yield buffer(string, size*n, size)
    yield ""


class Message:

    def __init__(self, data, aes_key, rsa_key, from_raw=False, next_hash=None, new_chain=False):
        self.aes_key = aes_key
        self.rsa_key = rsa_key
        if not from_raw:
            assert next_hash
            self.text = data
            self.iv = ""
            self.encrypted = 0
            self.signature = ""
            self.salt = ""
            self.signed = 0
            self.chain_link = next_hash
            self.chained = 0
            self.new_chain = 0
        else:
            self.deserialize(data)


    def protect(self, previous_hash, new_chain=None):
        # Use all security features
        self.chain_hash(previous_hash)
        self.sign()
        self.encrypt(new_chain)
        return self.serialize()


    def unprotect(self, previous_hash):
        # Assumes using all security features
        if self.encrypted: new_chain = self.decrypt()
        else: new_chain = None
        if self.signed:    self.verify()
        if self.chained:   self.check_hash(previous_hash)
        return self.text, new_chain


    def encrypt(self, new_chain=None):
        # Ecnrypt the chain-link and the message text
        if self.encrypted:
            raise ProtocolError("encryption failed - message is already encrypted")
        self.iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.aes_key, AES.MODE_CFB, self.iv)
        self.text = cipher.encrypt("%s%s%s" % (self.chain_link if self.chained else "", \
                                               new_chain if self.new_chain else "", \
                                               self.text))
        self.encrypted = 1


    def decrypt(self):
        # Decrypt and split into chain-link and message text
        if not self.encrypted:
            raise ProtocolError("decryption failed - message is already decrypted")
        cipher = AES.new(self.aes_key, AES.MODE_CFB, self.iv)
        plaintext = cipher.decrypt(self.text)
        if self.chained:
            self.chain_link, self.text = plaintext[:64], plaintext[64:]
            if self.new_chain:
                new_chain, self.text = plaintext[:64], plaintext[64:]
        else:
            self.text = plaintext
        self.encrypted = 0
        if self.chained and self.new_chain:
            return new_chain
        else:
            return None


    def sign(self):
        # Sign using a hash of the concatenated salt and text, encrypted with RSA
        if self.encrypted:
            raise ProtocolError("signing failed - cannot sign encrypted message")
        self.salt = Random.new().read(32)
        hash_obj = SHA512.new(self.salt + self.text)
        self.signature = rsa_decrypt(self.rsa_key, hash_obj.digest())
        self.signed = 1


    def verify(self):
        # Decrypt signature and check that hash matches decrypted message
        if self.encrypted:
            raise ProtocolError("verification failed - cannot verify encrypted message")
        if not self.signed:
            raise ProtocolError("verification failed - message is not signed")
        salted_hash = rsa_encrypt(self.rsa_key, self.signature)
        hash_obj = SHA512.new(self.salt + self.text)
        if salted_hash != hash_obj.digest():
            raise SecurityError("security compromised - hashes do not match")


    def chain_hash(self, previous_hash):
        # Add the next hash to the enod of the message
        hash_obj = SHA512.new(self.chain_link)
        if hash_obj.digest() != previous_hash:
            raise ProtocolError("security compromised - chained hash is invalid - %s != %s" % \
                                (previous_hash[:8], hash_obj.digest()[:8]))
        if self.encrypted:
            raise ProtocolError("hash-chaining failed - cannot chain to encrypted message")
        self.chained = 1


    def check_hash(self, previous_hash):
        # Assert that the current hash becomes the previous hash
        if not self.chained:
            raise ProtocolError("verification failed - message is unchained")
        if self.encrypted:
            raise ProtocolError("hash-chaining failed - cannot verify encrypted message")
        hash_obj = SHA512.new(self.chain_link)
        if hash_obj.digest() != previous_hash:
            raise SecurityError("security compromised - hash chain is broken")


    def serialize(self):
        try:
            serial = ""
            # Encrypted? and Chained? flags
            flags = "%s"*8 % (0, 0, 0, 0, \
                              self.signed, self.new_chain, self.chained, self.encrypted)
            flags = chr(int(flags, 2))
            serial += flags
            # Length of message text
            int_len = len(self.text)
            serial += pack("i", int_len)
            # Encrypted or unencrypted message text
            serial += self.text
            if self.encrypted:
                # AES initialisation vector
                serial += self.iv
            if self.signed:
                # Length of signature
                int_len = len(self.signature)
                serial += pack("i", int_len)
                # Signature
                serial += self.signature
                # Signature hash salt
                serial += self.salt
            return serial
        except Exception as e:
            raise ProtocolError("serialization failed - %s" % e)


    def deserialize(self, serial):
        def split(chars):
            try:
                return serial[:chars], serial[chars:]
            except:
                raise Exception("message wrong length")
        try:
            # Flags for what is encrypted etc...
            flags, serial = split(1)
            flags = [ord(flags) & 1 << n for n in range(8)]
            self.encrypted, self.chained, self.new_chain, self.signed = flags[0:4]
            # Length of message text
            str_len, serial = split(4)
            int_len = unpack("i", str_len)[0]
            # Encrypted or unencrypted message text
            self.text, serial = split(int_len)
            if self.encrypted:
                # AES initialisation vector
                self.iv, serial = split(AES.block_size)
            if self.signed:
                # Length of signature
                str_len, serial = split(4)
                int_len = unpack("i", str_len)[0]
                # Signature
                self.signature, serial = split(int_len)
                if len(serial) != 32: raise Exception("message wrong length")
                # Signature hash salt
                self.salt = serial
        except Exception as e:
            raise SecurityError("security compromised - deserialization failed - %s" % e)



class SecureChannel:

    def __init__(self, sock, server=False, rsa_key=None, output=None):
        self.output = output # Info message output
        self.sock = sock
        self.server = server
        self.aes_key = None
        if not server: self.gen_aes_key()
        if not rsa_key:
            self.gen_rsa_key()
        else:
            self.private_key = rsa_key
        self.gen_hashchain()


    def __dumb_send(self, data):
        int_len = len(data)
        str_len = pack("q", int_len)
        self.sock.send(str_len)
        self.sock.send(data)


    def __dumb_recv(self):
        str_len = self.sock.recv(8)
        while len(str_len) != 8: # hack
            str_len = self.sock.recv(8)
        int_len = unpack("q", str_len)[0]
        return self.sock.recv(int_len)


    def connect(self):
        # Exchange keys
        if self.server:
            if self.output: self.output("connecting to client\n")
            self.your_prev_hash = self.__dumb_recv()
            self.__dumb_send(self.my_prev_hash)
            if self.output: self.output("received client's final hash\n")
            key_data = self.__dumb_recv()
            self.public_key = RSA.importKey(key_data)
            if self.output: self.output("received client's public key\n")
            key_data = self.private_key.publickey().exportKey()
            self.__dumb_send(key_data)
            encrypted_key = self.__dumb_recv()
            self.aes_key = rsa_decrypt(self.private_key, encrypted_key)
            if self.output: self.output("received client's aes key\n")
        else: # client
            if self.output: self.output("connecting to server\n")
            self.__dumb_send(self.my_prev_hash)
            self.your_prev_hash = self.__dumb_recv()
            if self.output: self.output("received server's final hash\n")
            key_data = self.private_key.publickey().exportKey()
            self.__dumb_send(key_data)
            key_data = self.__dumb_recv()
            self.public_key = RSA.importKey(key_data)
            if self.output: self.output("received server's public key\n")
            iv = Random.new().read(AES.block_size)
            encrypted_key = rsa_encrypt(self.public_key, self.aes_key)
            self.__dumb_send(encrypted_key)
        if self.output: self.output("secure channel established\n")


    def send(self, text, echo=False):
        new_chain = len(self.hashchain) == 1
        message = Message(text, self.aes_key, self.private_key,
                          next_hash=self.hashchain[-1], new_chain=new_chain)
        if new_chain:
            self.gen_hashchain()
        msg_data = message.protect(self.my_prev_hash, self.hashchain[-1])
        self.__dumb_send(msg_data)
        self.my_prev_hash = self.hashchain[-1]
        del self.hashchain[-1]
        if not echo:
            echo_text = self.recv(echo=True)
            if not echo_text == text:
                raise SecurityError("security compromised - echo invalid")


    def recv(self, echo=False):
        msg_data = self.__dumb_recv()
        message = Message(msg_data, self.aes_key, self.public_key, from_raw=True)
        text, new_chain = message.unprotect(self.your_prev_hash)
        if message.new_chain:
            self.your_prev_hash = new_chain
        else:
            self.your_prev_hash = message.chain_link
        if not echo:
            self.send(text, True)
        return text


    def gen_rsa_key(self):
        if self.output: self.output("generating %s-bit rsa key\n" % RSA_STRENGTH)
        self.private_key = RSA.generate(RSA_STRENGTH)


    def gen_aes_key(self):
        if self.output: self.output("generating %s-bit aes key\n" % AES_STRENGTH)
        self.aes_key = Random.new().read(AES_STRENGTH >> 3)


    def gen_hashchain(self):
        # Uses 4MB of memory
        if self.output: self.output("generating 512-bit sha-2 hashchain\n")
        hash_obj = SHA512.new(Random.new().read(64))
        self.hashchain = []
        for n in xrange(HASHCHAIN_LENGTH):
            self.hashchain.append(hash_obj.digest())
            hash_obj = SHA512.new(self.hashchain[-1])
        self.my_prev_hash = hash_obj.digest()


    def close(self):
        # Umm...
        self.sock.close()
