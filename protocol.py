from struct import pack, unpack
import crypto

# TODO: Test module


AES_STRENGTH = 1 << 7
RSA_STRENGTH = 1 << 11
PADDING_WIDTH = 1 << 5


# Managed socket for sending / receiving pure data
# Will automatically detect length (unsigned long long = 18k TB)
# Should be buffered, currently isn't
class DumbChannel:

    def __init__(self, sock):
        self.sock = sock

    def send(self, text):
        int_len = len(data)
        str_len = pack("Q", int_len)
        self.sock.send(str_len)
        self.sock.send(data)

    def recv(self):
        str_len = self.sock.recv(8)
        while len(str_len) != 8:  # hack
            str_len = self.sock.recv(8)
        int_len = unpack("Q", str_len)[0]
        return self.sock.recv(int_len)


# Used for sending message objects, manages client-server connection etc...
class SecureChannel:

    def __init__(self, sock, signature, dominant=False):
        self.channel = DumbChannel(sock)
        self.signature = signature
        self.dominant = dominant
        self.msg_generator = None

    def _send(self, data):
        self.channel.send(data)

    def send(self, message):
        if self.msg_generator:
            data = self.msg_generator.construct(message)
            self._send(data)
        else:
            raise Exception()

    def _recv():
        return self.channel.recv()

    def recv(self):
        if self.msg_generator:
            data = self._recv()
            return self.msg_generator.deconstruct(data)
        else:
            raise Exception()

    def connect(self):
        symmetric = crypto.SymmetricEncryption(strength=AES_STRENGTH)
        private = crypto.AsymmetricEncryption(strength=RSA_STRENGTH)
        signature = crypto.Signature(key=self.signature)
        padding = crypto.SaltedPadding(padding_width=PADDING_WIDTH)
        hashchain = crypto.HashChain()
        if self.dominant:
            self._send(str(private))
            public = crypto.AsymmetricEncryption(
                key=private.encrypt(self._recv()))
            self._send(public.decrypt(private.encrypt(str(self.symmetric))))
            self._send(symmetric.encrypt(str(signature)))
            other_sig = crypto.Signature(kry=symmetric.decrypt(self._recv()))
        else:
            public = crypto.AsymmetricEncryption(key=self._recv())
            self._send(public.decrypt(str(private)))
            key = public.decrypt(private.encrypt(self._recv()))
            symmetric = crypto.SymmetricEncryption(key=key)
            other_sig = crypto.Signature(kry=symmetric.decrypt(self._recv()))
            self._send(symmetric.encrypt(str(signature)))
        self.msg_generator = MessageGenerator(
            symmetric, signature, other_sig, padding, hashchain)


# Creates message objects from encryption keys and text
"""
Message format:
|                    symmetric encrypted data                    |
| salt | message | asymmetric encrypted signature | chained hash |
                 |        hash of message         |
Each block is preceded by its length
"""


class MessageGenerator:

    def __init__(self, symmetric, self_signature, other_signature, padding, hashchain):
        self.symmetric = symmetric
        self.signature = self_signature
        self.other_sig = other_signature
        self.padding = padding
        self.hashchain = hashchain

    def construct(self, text):
        def add_block(text, data):
            text[0] += pack("q", len(data)) + data
        message = [""]                                    # Mutability hack
        add_block(message, self.padding.pad(""))            # Salt
        add_block(message, text)                            # Message text
        add_block(message, self.self_signature.sign(text))  # Signature
        add_block(message, self.hashchain.chain())          # Chained hash
        encrypted = self.symmetric.encrypt(message[0])      # Encrypted message
        return encrypted

    def deconstruct(self, encrypted):
        def rem_block(text):
            length, text[0] = unpack("q", text[0][:8]), text[0][8:]
            data, text[0] = text[0][:length], text[0][length:]
            return data
        message = [self.symmetric.decrypt(encrypted)]
        salt = rem_block(message)
        text = rem_block(message)
        self.other_sig.verify(rem_block(message), text)
        self.hashchain.verify(rem_block(message))
        return text
