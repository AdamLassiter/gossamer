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

        def is_subset(subset, superset):
            return all(item in superset.items() for item in subset.items())

        # Does this work?
        # Else, 'reduce(lambda a, b: a & b, map(isinstance, args, arg_types))'
        # Don't know about **kwargs, filter?
        @wraps(func)
        def wrapper(*args, **kwargs):
            if strength is not NONE:
                arg_types = tuple(map(type, args))
                kwarg_types = dict([(k, type(v)) for k, v in kwargs.items()])
                if arg_types != types or not is_subset(kwarg_types, kwtypes):
                    called_types = arg_types + \
                        ["%s=%s" % kv for kv in kwarg_types.items()]
                    msg = info(func, "called with", called_types, types)
                    if strength is WEAK:
                        print >> stderr, "Warning: ", msg
                    elif strength is STRONG:
                        raise TypeError(msg)
            return func(*args)

        return wrapper

    if "_strength" not in kwtypes:
        strength = DEFAULT
    else:
        strength = kwtypes["_strength"]
        del kwtypes["_strength"]
    return arg_checked


def returns(*types):

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
