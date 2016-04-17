import socket
from socket import error as SocketError
import threading
from os.path import exists as file_exists
from os.path import split as split_fname
try:
    from msvcrt import getch
except ImportError:
    from curses import getch
from sys import stdout
from time import sleep
from __protocol import SecureChannel, SecurityError, ProtocolError, buffered


# TcpClient-specific error
class ClientError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return self.value


class TcpClient:

    commands = [":free:", ":used:", ":nick:",
                ":mesg:", ":file:",
                ":offr:", ":acpt:", ":rjct:",
                ":quit:", ":svqt:"]

    def __init__(self, address="localhost", port=5000, paranoia=1):
        def paranoid(x):
            try: self.channel.send(":quit:%s" % x)
            except: pass
            raise ClientError(x)
        def cautious(x):
            if str(x).split(" - ")[0] in ["client/server exchange invalid", "security compromised"]:
                paranoid(x)
            else:
                normal(x)
        def normal(x):
            self.output(x)
        assert type(port) == int
        assert 0 <= port < 65536
        self.accepting_file = False
        self.HOST, self.PORT = address, port
        self.input_str = ""
        self.error = [normal, cautious, paranoid][paranoia]

    def input(self, prompt):
        self.input_str = ""
        self.prompt = prompt
        stdout.write("%s " % self.prompt)
        while True:
            char = getch()
            if char == chr(8): # Backspace
                if self.input_str:
                    stdout.write(char)
                    stdout.write(" ")
                    stdout.write(char)
                    self.input_str = self.input_str[:-1]
            elif char == chr(13): # Enter
                stdout.write("\n")
                break
            elif 32 <= ord(char) <= 127: # Everything else
                self.input_str += char
                stdout.write(char)
        inp_str, self.input_str = self.input_str, ""
        return inp_str

    def output(self, string):
        stdout.write(chr(8) * (len(self.input_str) + len(self.prompt) + 1))
        stdout.write(string + "\n")
        stdout.write("%s %s" % (self.prompt, self.input_str))

    def serve_forever(self):
        self.connect()
        self.receiveThread = threading.Thread(target=self.receive_forever)
        self.sendThread = threading.Thread(target=self.send_forever)
        self.receiveThread.start()
        self.sendThread.start()

    def connect(self):
        try:
            self.sock = socket.create_connection((self.HOST, self.PORT))
            self.channel = SecureChannel(self.sock, output=stdout.write)
            self.channel.connect()
            reply = ":used:"
            while reply[0:6] != ":free:":
                self.nickname = self.input("nickname?")
                if " " in self.nickname:
                    stdout.write("ncikname cannot contain spaces\n")
                    continue
                self.channel.send(":nick:%s" % self.nickname)
                reply = self.channel.recv()
                if reply[0:6] == ":used:":
                    stdout.write("nickname in use\n")
                elif reply[0:6] != ":free:":
                    stdout.write("invalid header - %s" % reply[:6])
            if reply[6:] != self.nickname:
                self.error("client/server exchange invalid - nickname is not %s" \
                           % reply[6:])
        except SocketError:
            stdout.write("connection refused by server\n")
            stdout.write("retry in 5 seconds%s" % (chr(8) * 9))
            for n in range(5):
                sleep(1)
                stdout.write("%s%s" % (str(4-n), chr(8)))
            stdout.write("\n")
            self.connect()
        except SecurityError as e:
            self.error("security compromised - %" % e)

    def receive_forever(self):
        while True:
            file = None
            data = self.channel.recv()
            header, message = data[:6], data[6:]
            if header == ":svqt:":
                self.output("server quit - %s" % message)
                self.close()
            elif header == ":offr:":
                self.accepting_file = True
                nickname, filename = message.split(" ", 1)
                self.output("%s sent: %s\naccept? y(es) / n(o)" % (nickname, filename))
            elif header == ":file:":
                if not file:
                    file = open(filename, "w+b")
                file.write(message)
                if not message:
                    file.close()
                    file = None
            elif header == ":mesg:":
                self.output(message)
            else:
                self.error("invalid header - %s" % header)

    def send_forever(self):
        while True:
            try:
                user_input = self.input(">>>")

                while user_input[:6] in TcpClient.commands or not user_input:
                    user_input = self.input(">>>")

                if user_input[0] == "@":
                    try:
                        target, user_input = user_input.split(" ", 1)
                    except:
                        continue
                else:
                    target = ""

                if user_input == "quit":
                    self.channel.send(":quit:%s left" % (self.nickname))
                    self.output("successfully quit server")
                    self.close()

                elif self.accepting_file:
                    while user_input.lower() not in ["y", "yes", "yum", "n", "no", "nom"]:
                        self.output("please enter y(es) / n(o)")
                        user_input = self.input(">>>")
                    if user_input.lower() in ["y", "yes", "yum"]:
                        self.channel.send(":acpt:")
                    elif user_input.lower() in ["n", "no", "nom"]:
                        self.channel.send(":rjct:")
                    self.accepting_file = False

                elif file_exists(user_input):
                    file_data = open(user_input, "rb").read()
                    self.channel.send(":file:%s %s" % ( target, split_fname(user_input)[1]) )
                    self.output("uploading file to server")
                    for block in buffered(file_data, 1<<8):
                        self.channel.send(str(block))
                    self.output("successfully uploaded file")

                else:
                    self.channel.send(":mesg:%s%s" % (target + " " if target else "", user_input))

            except SecurityError as e:
                self.error(e)
            except ProtocolError as e:
                self.error(e)
            except Exception as e:
                self.error("error - %s" % e)

    def close(self):
        sleep(1)
        exit()


if __name__ == "__main__":
    client = TcpClient()
    client.serve_forever()
