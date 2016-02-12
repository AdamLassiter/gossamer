from threading import Thread
import protocol
from socket import create_connection as Socket

# TODO: Finish Node code
# TODO: Finish Seed code
# TODO: Finish Onion code
# TODO: Finish AddressDirectory code



class Node:

    def __init__(self, io, signature):
        self.signature = signature
        self.io = io
        self.addr_dir = AddressDirectory()


    def connect(self, address, port):
        sock = Socket((address, port))
        secure_channel = protocol.SecureChannel(sock, self.signature, False)
        # connect to seed (name and password)
        # get patrons and timestamped username
        # connect to patrons
        # send random start distance, name timestamp and public key
        # patrons send address directory
        pass


    def listen(self, ):
        pass


    def send(self, target):
        pass


    def recv(self):
        pass



class Onion:

    def __init__(self, message, route):
        pass



class User:

    # Signature - str?
    # Distance - int
    # Direction - Node
    def __init__(self, signature, distance, direction):
        self.signature = signature
        self.distance = distance
        self.direction = direction


    # Signatures should be unique and constant
    def __eq__(self, other):
        return self.signature == other.signature


    # Update with new distances and directions
    def upadte(self, distance, direction):
        self.distance = self.distance if self.distance < distance else distance
        self.direction = self.direction if self.distance < distance else direction



class AddressDirectoy:

    # Initialise to empty directory
    def __init__(self):
        #self.directory = {name:user}
        self.directory = {None:None}


    # Add a user with a specific signature to the directory
    # Presume they have just joined
    def add(self, user, name=None):
        # Generate a random, pronouncable, temporary name
        while name in self.directory.keys():
            name = ''.join([choice('aeiou' if i%2 else 'bcdfghklmnprstvw') for i in range(8)])
        self.directory[name] = user


    # Remove a user with specific signature from the directory
    # Presume they have quit
    def remove(self, name):
        if name in self.directory.keys():
            signature = self.directory[name]
            del self.directory[name]


    def export(self):
        return [ (name, user.signature) for name, signature in self.directory.items() ]
