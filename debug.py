from functools import wraps
from sys import stdout


def printout(*args):
    stdout.write(*args)
    stdout.flush()


class depth_handler:

    def __init__(self):
        self.depth = 0

    def __enter__(self):
        self.depth += 1
        return self.depth

    def __exit__(self, type, value, traceback):
        self.depth -= 1
__debug_depth = depth_handler()


def debug(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        global __debug_depth
        with __debug_depth as depth:
            func_args = [arg for arg in args] + \
                        ["%s=%s" % kv_pair for kv_pair in kwargs.items()]
            printout("debugging %s(%s)\n" % (func.__name__, ", ".join(map(str, func_args))))
            try:
                ret = func(*args, **kwargs)
                printout("\t" * depth + "%s(%s) -> %s\n" %
                         (func.__name__, ", ".join(map(str, func_args)), ret))
                return ret
            except Exception as e:
                printout("\t" * depth + "%s(%s) -> Exception! (%s)\n" %
                         (func.__name__, ", ".join(map(str, func_args)), e))
                raise e

    return wrapper
