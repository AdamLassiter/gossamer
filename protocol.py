from struct import pack, unpack
from socket import socket
import crypto

from declarative import accepts, returns

# TODO: Test module


AES_STRENGTH = 1 << 7
RSA_STRENGTH = 1 << 11
PADDING_WIDTH = 1 << 5


# Managed socket for sending / receiving pure data
# Will automatically detect length (unsigned long long = 18k TB)
# Should be buffered, currently isn't
class DumbChannel:

    @accepts(DumbChannel, socket)
    def __init__(self, sock):
        self.sock = sock

    @accepts(DumbChannel, str)
    def send(self, text):
        int_len = len(data)
        str_len = pack("Q", int_len)
        self.sock.send(str_len)
        self.sock.send(data)

    @returns(str)
    def recv(self):
        str_len = self.sock.recv(8)
        while len(str_len) != 8:  # hack
            str_len = self.sock.recv(8)
        int_len = unpack("Q", str_len)[0]
        return self.sock.recv(int_len)


# Used for sending message objects, manages client-server connection etc...
class SecureChannel:

    @accepts(SecureChannel, socket, crypto.Signature, dominant=bool)
    def __init__(self, sock, signature, dominant=False):
        self.channel = DumbChannel(sock)
        self.signature = signature
        self.dominant = dominant
        self.msg_generator = None

    @accepts(str)
    def send(self, message):
        data = self.msg_generator.construct(message)
        self.channel.send(data)

    @returns(str)
    def recv(self):
        if self.msg_generator:
            data = self.channel.recv()
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
            self.channel.send(str(private))
            public = crypto.AsymmetricEncryption(
                key=private.encrypt(self.channel.recv()))
            self.channel.send(public.decrypt(private.encrypt(str(symmetric))))
            self.channel.send(symmetric.encrypt(str(signature)))
            other_sig = crypto.Signature(
                kry=symmetric.decrypt(self.channel.recv()))
        else:
            public = crypto.AsymmetricEncryption(key=self.channel.recv())
            self.channel.send(public.decrypt(str(private)))
            key = public.decrypt(private.encrypt(self.channel.recv()))
            symmetric = crypto.SymmetricEncryption(key=key)
            other_sig = crypto.Signature(
                key=symmetric.decrypt(self.channel.recv()))
            self.channel.send(symmetric.encrypt(str(signature)))
        self.msg_generator = MessageGenerator(
            symmetric, signature, other_sig, padding, hashchain)


# Creates message objects from encryption keys and text
"""
Message format:
|                    symmetric encrypted data                    |
| salt | message | asymmetric encrypted signature | chained hash |
                 |        hash of message         |
Each block is preceeded by its length
"""


class MessageGenerator:

    @accepts(MessageGenerator, crypto.SymmetricEncryption, crypto.Signature,
             crypto.Signature, crypto.SaltedPadding, crypto.HashChain)
    def __init__(self, symmetric, self_signature, other_signature, padding, hashchain):
        self.symmetric = symmetric
        self.signature = self_signature
        self.other_sig = other_signature
        self.padding = padding
        self.hashchain = hashchain

    @accepts(MessageGenerator, str)
    @returns(str)
    def construct(self, text):
        def add_block(text, data):
            text[0] += pack("q", len(data)) + data
        message = [""]                                      # Mutability hack
        add_block(message, self.padding.pad(""))            # Salt
        add_block(message, text)                            # Message text
        add_block(message, self.self_signature.sign(text))  # Signature
        add_block(message, self.hashchain.chain())          # Chained hash
        encrypted = self.symmetric.encrypt(message[0])      # Encrypted message
        return encrypted

    @accepts(MessageGenerator, str)
    @returns(str)
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
