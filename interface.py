import gossamer

# TODO:90 issue:2 Test io class
# TODO:20 issue:1 Finish Program code
# This is hideous


class io:

    from sys import stdout
    try:
        from msvcrt import getch
    except ImportError:
        from curses import getch

    def __init__(self):
        self.input_str = ""
        self.prompt = ">"

    def read(self):
        stdout.write(self.prompt)
        while True:
            input_chr = getch()
            if input_chr == chr(8):  # Backspace
                if self.input_str:
                    stdout.write(input_chr)
                    stdout.write(" ")
                    stdout.write(input_chr)
                elif input_chr == chr(13):  # Enter
                    stdout.write(input_chr)
                    break
                elif 32 <= ord(input_chr):  # Printable character
                    self.input_str += input_chr
                    stdout.write(input_chr)
        string, self.input_str = self.input_str, ""
        return string

    def write(self, string):
        from sys import stdout
        length = len(self.input_str) + len(self.prompt)
        stdout.write(chr(8) * length + chr(32) * length + chr(8) * length)
        stdout.write(string + "\n")
        stdout.write(self.prompt + self.input_str)


class Program:

    pass
