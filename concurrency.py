#! /usr/bin/env python3

from collections.abc import Callable
from functools import wraps


def threaded(func: Callable) -> Callable:
    from threading import Thread

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def parallelized(func: Callable) -> Callable:
    from multiprocessing import Process

    @wraps(func)
    def wrapper(*args, **kwargs):
        process = Process(target=func, args=args, kwargs=kwargs)
        process.start()
        return process

    return wrapper


def synchronized(lock: object) -> Callable:

    def locked(func: Callable) -> Callable:
        # from threading import Lock

        @wraps(func)
        def wrapper(*args, **kwargs):
            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()

        return wrapper

    return locked


def clustered(func: Callable):
    pass
