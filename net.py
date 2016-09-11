from struct import pack, unpack
from socket import socket, create_connection as csocket, AF_INET, SOCK_STREAM
import crypto

from declarative import accepts, returns

# TODO:0 Add create_sock to module?


AES_STRENGTH = 1 << 7
RSA_STRENGTH = 1 << 11
PADDING_WIDTH = 1 << 5


class DumbChannel:
    # Managed socket for sending / receiving plain data
    # Will automatically detect length (maximum unsigned long long = 18k TB)
    # Should be buffered, currently isn't

    @accepts(socket)
    def __init__(self, sock):
        self.sock = sock

    @accepts(str)
    def send(self, text):
        int_len = len(text)
        str_len = pack("Q", int_len)
        self.sock.send(str_len)
        self.sock.send(text)

    @returns(str)
    def recv(self):
        str_len = self.sock.recv(8)
        while len(str_len) != 8:  # hack
            str_len = self.sock.recv(8)
        int_len = unpack("Q", str_len)[0]
        return self.sock.recv(int_len)


class SecureChannel:
    # Used for sending message objects, manages client-server connection etc...

    @accepts(tuple, signature=dict, is_server=bool)
    def __init__(self, address, signature=None, is_server=False):
        self.address = address
        self.signature = signature
        self.is_server = is_server
        self.channel = None

    def __enter__(self):
        if self.channel is None:
            sock = self.new_socket(self.address, is_server=self.is_server)
            if self.is_server:
                self.channel = DumbChannel(sock.accept()[0])
            else:
                self.channel = DumbChannel(sock)
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.channel.sock.close()

    @staticmethod
    @accepts(tuple, is_server=bool)
    def new_socket(address, is_server=False):
        if is_server:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.bind(address)
            sock.listen(1)
        else:
            sock = csocket(address)
        return sock

    @accepts(str)
    def send(self, message):
        data = self.msg_generator.construct(message)
        self.__send(data)

    def __send(self, message):
        self.channel.send(message)

    @returns(str)
    def recv(self):
        if self.msg_generator:
            data = self.__recv()
            return self.msg_generator.deconstruct(data)
        else:
            raise Exception()

    def __recv(self):
        return self.channel.recv()

    def connect(self):
        # Initialise crypto objects
        symmetric = crypto.SymmetricEncryption(strength=AES_STRENGTH)
        public, private = crypto.AsymmetricEncryption(), crypto.AsymmetricEncryption()
        signature, other_sig = crypto.Signature(keypair=self.signature), crypto.Signature(keypair=self.signature)
        hashchain = crypto.HashChain()

        # Either send or recieve first
        if self.is_server:
            self.__send(private.pubkey())
            public.set_key(private.decrypt(self.__recv()))
            self.__send(public.encrypt(private.encrypt(symmetric.pubkey())))
            self.__send(symmetric.encrypt(signature.pubkey()))
            other_sig.set_key(pub=symmetric.decrypt(self.__recv()))

        else:
            public.set_key(pub=self.__recv())
            self.channel.send(public.encrypt(private.pubkey()))
            key = public.decrypt(private.decrypt(self.__recv()))
            symmetric = crypto.SymmetricEncryption(key=key)
            other_sig = crypto.Signature(key=symmetric.decrypt(self.__recv()))
            self.__send(symmetric.encrypt(signature.pubkey()))

        self.msg_generator = MessageGenerator(
            symmetric, signature, other_sig, hashchain)


class MessageGenerator:
    """Creates message objects from encryption keys and text.

    Message format:
    |                 symmetric encrypted data                |
    | message | asymmetric encrypted signature | chained hash |
              |        hash of message         |
    Each block is preceeded by its length
    """

    @accepts(crypto.SymmetricEncryption, crypto.Signature, crypto.Signature, crypto.HashChain)
    def __init__(self, symmetric, self_sig, other_sig, hashchain):
        self.symmetric = symmetric
        self.signature = self_sig
        self.other_sig = other_sig
        self.hashchain = hashchain

    @accepts(str)
    @returns(str)
    def construct(self, text):
        def with_len(data):
            return pack("q", len(data)) + data
        message = "".join(map(with_len, [text,
                                         self.signature.sign(text),
                                         self.hashchain.chain()]))
        encrypted = self.symmetric.encrypt(message)
        return encrypted

    @accepts(str)
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

if __name__ == '__main__':
    import tests
    tests.test_net()
