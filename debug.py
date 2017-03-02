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
        def truncate(s, n):
            return "%s%s" % (str(s)[:min(len(s), n)], " ... " if len(s) > n else "")

        global __debug_depth
        with __debug_depth as depth:
            func_args = [arg for arg in args] + \
                        ["%s=%s" % kv_pair for kv_pair in kwargs.items()]
            try:
                ret = func(*args, **kwargs)
                str_args = (("    " * depth, 64),
                            (func.__name__, 32),
                            (", ".join(map(str, func_args)), 64),
                            (ret, 32))
                s = "%s%s(%s) -> %s" % map(lambda x: truncate(*x), str_args)
                return ret
            except Exception as e:
                s = "    " * depth + "%s(%s) -> Exception! (%s)\n" % \
                    (func.__name__, ", ".join(map(str, func_args)), e)
                print "%s%s" % (s[:min(len(s), 96)], " ... " if len(s) > 96 else "")
                raise e

    return wrapper
