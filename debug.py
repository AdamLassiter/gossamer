from functools import wraps


class depth_handler:

    def __init__(self):
        self.depth = 0

    def __enter__(self):
        self.depth += 1
        return self.depth

    def __exit__(self, type, value, traceback):
        self.depth -= 1
debug_depth = depth_handler()


def debug(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        global debug_depth
        with debug_depth as depth:
            ret = func(*args, **kwargs)
            func_args = [arg for arg in args] + \
                        ["%s=%s" % kv_pair for kv_pair in kwargs.items()]
            print "\t" * depth + "%s(%s) -> %s" % \
                  (func.__name__, ", ".join(map(str, func_args)), ret)
        return ret

    return wrapper
