from functools import wraps
from sys import stderr

NONE = 0
WEAK = 1
STRONG = 2
DEFAULT = WEAK


def info(func, action, actual, expected):
    return "%s %s %s, but expected %s" % \
        (func.__name__, action, actual, expected)


def accepts(*types, **kwtypes):

    def arg_checked(func):

        def type(obj):
            return obj.__class__

        @wraps(func)
        def wrapper(*args, **kwargs):
            if strength is not NONE:
                if func.__name__ in dir(args[0]):
                    self, args = args[:1], args[1:]
                else:
                    self = None
                arg_types = tuple(map(type, args))
                kwarg_types = set(map(lambda kv: (kv[0], type(kv[1])), kwargs.items()))
                if arg_types != types or not kwarg_types.issubset(set(kwtypes.items())):
                    called_types = arg_types + \
                        tuple(["%s=%s" % kv for kv in kwarg_types])
                    expected_types = types + \
                        tuple(["%s=%s" % kv for kv in kwtypes.items()])
                    msg = info(func, "called with", called_types, types)
                    if strength is WEAK:
                        print >> stderr, "Warning: ", msg
                    elif strength is STRONG:
                        raise TypeError(msg)
            return func(*(self + args if self else args), **kwargs)

        return wrapper

    if "_strength" not in kwtypes:
        strength = DEFAULT
    else:
        strength = kwtypes["_strength"]
        del kwtypes["_strength"]
    return arg_checked


def returns(*types, **kwtypes):

    def ret_checked(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            if strength is not NONE:
                ret_types = tuple(map(type, (ret,)))
                if ret_types != types:
                    msg = info(func, "returned", (ret,), types)
                    if strength is WEAK:
                        print >> stderr, "Warning: ", msg
                    elif strength is STRONG:
                        raise TypeError(msg)
            return ret

        return wrapper

    if "_strength" not in kwtypes:
        strength = DEFAULT
    else:
        strength = kwtypes["_strength"]
        del kwtypes["_strength"]
    return ret_checked
