from functools import wraps
from sys import stderr

NONE = 0
WEAK = 1
STRONG = 2
DEFAULT = STRONG


def info(func, action, actual, expected):
    return "%s%s %s %s, but expected %s" % \
        (func.im_class + "." if hasattr(func, "im_class") else "", func.__name__,
         action, actual, expected)


def accepts(*types, **kwtypes):

    def arg_checked(func):

        def type(obj):
            return obj.__class__

        def pair_type(pair):
            return (pair[0], type(pair[1])) if pair[1] is not None else None

        @wraps(func)
        def wrapper(*args, **kwargs):
            if strength is not NONE:
                if args and func.__name__ in dir(args[0]):
                    self, args = args[:1], args[1:]
                else:
                    self = None

                arg_types = tuple(map(type, args))
                kwarg_types = set(map(pair_type, kwargs.items()))

                if arg_types != types or not kwarg_types.issubset(set(kwtypes.items() + [None])):
                    called = arg_types + tuple(["%s=%s" % kv for kv in kwarg_types])
                    expected = types + tuple(["%s=%s" % kv for kv in kwtypes.items()])
                    msg = info(func, "called with", called, expected)

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
