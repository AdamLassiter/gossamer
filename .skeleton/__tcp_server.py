import socket
import threading
from sys import stdout
from time import sleep, time
from __protocol import SecureChannel, SecurityError, ProtocolError, buffered

# TcpServer-specific error
class ServerError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return self.value


"""

Buffered sending to support files and long messages

"""


class TcpServer:

    commands = [":free:", ":used:", ":nick:",
                ":mesg:", ":file:",
                ":offr:", ":acpt:", ":rjct:",
                ":quit:", ":svqt:"]

    def __init__(self, address="localhost", port=5000, debug=True, logging=False,
            log_file="log.txt", paranoia=1):
        def paranoid(x):
            try:
                self.broadcast(":svqt:paranoid server quit")
            except: pass
            raise ServerError(x)
        def cautious(x):
            if str(x).split(" - ", 1)[0] == "security compromised":
                paranoid(x)
            else:
                normal(x)
        def normal(x):
            self.output(x)
        self.HOST = address
        self.PORT = port
        self.DEBUG = debug
        self.LOGGING = logging
        self.RUNNING = True
        self.clients = {}
        self.error = [normal, cautious, paranoid][paranoia]
        if self.LOGGING:
            self.log_file = open(log_file, "wb")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.HOST, self.PORT))
        self.sock.listen(1)
        self.output("%s(server) waiting on %s:%s\n" % (" " * 15, address, port))

    def output(self, string):
        if self.DEBUG:
            stdout.write(string)
        if self.LOGGING:
            self.log_file.write(string)
            self.log_file.flush()

    def broadcast(self, message, from_user=None):
        for target in self.clients:
            if target != from_user:
                self.clients[target].send(message)

    def serve_forever(self):
        while self.RUNNING:
            sock, address = self.sock.accept()
            threadName = "client@%s" % (str(address))
            threadObj = threading.Thread(target=self.serve_client,
                                         name=threadName,
                                         args=(sock, address))
            threadObj.start()
        for target in self.clients.values():
            target.send(":svqt:server closed")
        raise SystemExit

    def connect_client(self, sock, address):
        address = "(%s:%s)" % address
        address = " " * (23 - len(address)) + address
        self.output("%s connecting\n" % (address))
        channel = SecureChannel(sock, server=True, output=self.output)
        channel.connect()
        reply = channel.recv()
        header, nickname = reply[:6], reply[6:]
        if header != ":nick:":
            self.error("unrecognised header - %s" % header)
        while nickname in self.clients.keys():
            channel.send(":used:%s" % nickname)
            reply = channel.recv()
            header, nickname = reply[:6], reply[6:]
            if header != ":nick:":
                self.error("unrecognised header - %s" % header)
        channel.send(":free:%s" % nickname)
        self.output("%s %s joined\n" % (address, nickname))
        self.clients[nickname] = channel
        channel.accepting_file = False
        return channel, (nickname, address)

    def serve_client(self, sock, address):
        try:
            client, (nickname, address) = self.connect_client(sock, address)
        except Exception as e:
            self.output("%s\n%s client failed to connect\n" % (e, address))
            return 0
        try:
            self.broadcast(":mesg:%s joined" % (nickname))
            while True:
                data = client.recv()
                header, message = data[:6], data[6:]
                self.output("%s %s said:   %s\n"
                                % (address, nickname, data))
                if message[0] == "@":
                    target, message = message[1:].split(" ", 1)
                else:
                    target = ""
                if target and not target in self.clients.keys():
                    client.send(":mesg:user not found")
                    continue
                if header == ":quit:":
                    client.close()
                    del self.clients[nickname]
                    self.broadcast("%s quit - %s" % (nickname, message))
                    self.output("%s %s quit - %s\n" % (address, nickname, message))
                    break
                elif header == ":file:":
                    file = open("%s-%s%s" % (nickname, str(int(time()))[-6:], message), "w+b")
                    block = " "
                    while block:
                        block = client.recv()
                        file.write(block)
                    file.close()
                    if target:
                        target_list = [self.clients[target]]
                    else:
                        target_list = self.clients.values()
                        target_list.remove(client)
                    for target in target_list:
                        while target.accepting_file:
                            sleep(1)
                        target.send(":offr:%s %s" % (nickname, message))
                        reply = target.recv()
                        if reply == ":acpt:":
                            target.accepting_file = True
                            file_data = open(file_name, "rb").read()
                            for block in buffered(file_data, 1<<8):
                                target.send(":file:%s" % block)
                            target.accepting_file = False
                        elif reply == ":rjct:":
                            pass
                elif header == ":mesg:":
                    if target:
                        target_list = [self.clients[target]]
                        whisper = "# "
                    else:
                        target_list = self.clients.values()
                        target_list.remove(client)
                        whisper = "> "
                    for target in target_list:
                        target.send(":mesg:%s%s said: %s" % (whisper, nickname, message))
                else:
                    self.error("invalid header - %s" % header)
        except SecurityError as e:
            self.error(e)
        except ProtocolError as e:
            self.error(e)
        except Exception as e:
            self.output("%s\n%s %s kicked in caution\n" % (e, address, nickname))
            del self.clients[nickname]
            self.broadcast(":mesg:%s quit - kicked in caution" % (nickname))


if __name__ == "__main__":
    server = TcpServer()
    server.serve_forever()
