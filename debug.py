#! /usr/bin/python3

from functools import wraps


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
                        ["%s=%s" % kwarg for kwarg in kwargs.items()]
            try:
                ret = func(*args, **kwargs)
                str_args = ("    " * depth,
                            func.__name__,
                            ", ".join(map(str, func_args)),
                            ret)
                s = "%s%s(%s) -> %s" % str_args
                return ret
            except Exception as e:
                print(e)
                raise e

    return wrapper
