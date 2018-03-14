from functools import wraps
import time


def timer(func):
    """Timer decorator. Prints out elapsed time running the process.
    """
    @wraps(func)
    def func_timer(*args, **kwargs):
        s = time.time()
        result = func(*args, **kwargs)
        e = time.time()
        print("Time running [%s]: %.3f seconds" % (func.__name__, (e - s)))
        return result
    return func_timer
