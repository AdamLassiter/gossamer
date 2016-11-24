from functools import wraps
from traceback import print_exc


class depth_handler:

    def __init__(self):
        self.depth = 0

    def __enter__(self):
        self.depth += 1
        return self.depth

    def __exit__(self, type, value, traceback):
        self.depth -= 1
__test_depth = depth_handler()


def test(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        global __test_depth
        with __test_depth as depth:
            func_args = [arg for arg in args] + \
                        ["%s=%s" % kv_pair for kv_pair in kwargs.items()]
            try:
                ret = func(*args, **kwargs)
                print "%s%s passed" % ("    " * depth, func.__name__)
                return ret
            except Exception as e:
                print "%s%s failed" % ("    " * depth, func.__name__)
                print_exc()

    return wrapper
