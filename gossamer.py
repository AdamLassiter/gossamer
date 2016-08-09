from threading import Thread
from protocol import SecureChannel
from socket import create_connection as Socket, socket as ServerSocket

from declarative import accepts, returns

# TODO: Write Onion code
# TODO: Test module


class Node:

    @ecceots(protocol.crypto.Signature)
    def __init__(self, signature):
        self.signature = signature
        self.addr_dir = AddressDirectory()

    @accepts(Socket)
    @returns(SecureChannel)
    def connect(self, sock):
        secure_channel = SecureChannel(sock, self.signature, True)
        secure_channel.connect()
        return secure_channel

    @accepts(ServerSocket)
    @returns(SecureChannel)
    def get_listener(self, sock):
        sock.listen(5)
        while True:
            secure_channel = SecureChannel(
                sock.accept(), self.signature, False)
            secure_channel.connect()
            yield secure_channel

    @accepts(str, int)
    @returns(Socket)
    @staticmethod
    def create_client(address, port):
        sock = Socket((address, port))
        return sock

    @accepts(str, int)
    @returns(ServerSocket)
    @staticmethod
    def create_server(address, port):
        from socket import AF_INET, SOCK_STREAM
        sock = ServerSocket(AF_INET, SOCK_STREAM)
        sock.bind(address, port)
        return sock

    @accetps(str, str)
    def send(self, target, message):
        assert self.addr_dir.contains(target)
        user = self.addr_dir.get(target)
        channel = user.direction
        channel.send(message)

    @accepts(SecureChannel)
    @returns(str, str)
    def recv(self, source):
        return "user", source.recv()


class Onion:

    # TODO: Implement all the onion

    @accepts(Onion, str, )
    def __init__(self, message, route):
        pass


class User:

    # TODO: Test class

    @accepts(protocol.crypto.Signature, int, SecureChannel)
    def __init__(self, signature, distance, direction):
        self.signature = signature
        self.distance = distance
        self.direction = direction

    def __eq__(self, other):
        # Signatures should be unique and constant
        return self.signature == other.signature

    @accepts(int, SecureChannel)
    def update(self, dist, dir):
        # Update with new distances and directions
        self.distance = self.distance if self.distance < dist else dist
        self.direction = self.direction if self.distance < dist else dir


class AddressDirectoy:

    # TODO: Test class

    def __init__(self):
        # Initialise to empty directory
        # self.directory = {name:user}
        self.directory = {None: None}

    @accepts(User, str)
    def add(self, user, name=None):
        # Add a user with a specific signature to the directory
        # Presume they have just joined
        while name in self.directory.keys():
            # Generate a random, pronouncable, temporary name
            # ~10k names holds p < 0.05 of collisions
            name = ''.join([choice('aeiou' if i % 2 else 'bcdfghklmnprstvw')
                            for i in range(8)])
        self.directory[name] = user

    @accepts(str)
    def remove(self, name):
        # Remove a user with specific signature from the directory
        # Presume they have quit
        if name in self.directory.keys():
            signature = self.directory[name]
            del self.directory[name]

    @accepts(str)
    @returns(User)
    def get(self, name):
        return self.directory[name]

    @accepts(str)
    @returns(bool)
    def contains(self, name):
        return self.directory.contains(name)

    @accepts(str)
    def get_route_to(self, name):
        assert self.contains(name)
        pass

    @returns(list)
    def export(self):
        # Returns a list of str:User pairs
        return [(name, user.signature)
                for name, user in self.directory.items()]
