from threading import Thread
from protocol import SecureChannel
from socket import create_connection as Socket,
    socket as ServerSocket

# TODO: Write Onion code


class Node:

    def __init__(self, signature):
        self.signature = signature
        self.addr_dir = AddressDirectory()

    def connect(self, sock):
        assert isinstance(sock, Socket)
        secure_channel = SecureChannel(sock, self.signature, True)
        secure_channel.connect()
        return secure_channel

    def listen(sock):
        assert isinstance(sock, ServerSocket)
        sock.listen(1)
        while True:
            secure_channel = SecureChannel(
                sock.accept(), self.signature, False)
            secure_channel.connect()
            yield secure_channel

    def create_client(address, port):
        sock = Socket((address, port))
        return sock

    def create_server(address, port):
        from socket import AF_INET, SOCK_STREAM
        sock = ServerSocket(AF_INET, SOCK_STREAM)
        sock.bind(address, port)
        return sock

    def send(self, target, message):
        assert self.addr_dir.contains(target)
        channel = self.addr_dir.get(target)
        channel.send(message)

    def recv(self, source):
        assert isinstance(source, SecureChannel)
        while True:
            yield source.recv()


class Onion:

    def __init__(self, message, route):
        pass


class User:

    # TODO: Test class

    # Signature - str of Signature object
    # Distance -  int
    # Direction - SecureChannel
    def __init__(self, signature, distance, direction):
        self.signature = signature
        self.distance = distance
        self.direction = direction

    # Signatures should be unique and constant
    def __eq__(self, other):
        return self.signature == other.signature

    # Update with new distances and directions
    def update(self, distance, direction):
        self.distance = self.distance if self.distance < distance else distance
        self.direction = self.direction if self.distance < distance else direction


class AddressDirectoy:

    # TODO: Test class

    # Initialise to empty directory
    def __init__(self):
        #self.directory = {name:user}
        self.directory = {None: None}

    # Add a user with a specific signature to the directory
    # Presume they have just joined
    def add(self, user, name=None):
        assert isinstance(user, User)
        # Generate a random, pronouncable, temporary name
        # ~10k names holds p < 0.05 of collisions
        while name in self.directory.keys():
            name = ''.join(
                [choice('aeiou' if i % 2 else 'bcdfghklmnprstvw') for i in range(8)])
        self.directory[name] = user

    # Remove a user with specific signature from the directory
    # Presume they have quit
    def remove(self, name):
        if name in self.directory.keys():
            signature = self.directory[name]
            del self.directory[name]

    def get(self, name):
        return self.directory[name]

    def contains(self, name):
        return self.directory.contains(name)

    def get_route_to(self, name):
        assert self.contains(name)

    def export(self):
        return [(name, user.signature) for name, user in self.directory.items()]
