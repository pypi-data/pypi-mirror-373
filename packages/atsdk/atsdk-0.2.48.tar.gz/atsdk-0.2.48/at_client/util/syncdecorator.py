from functools import wraps
from multiprocessing import Lock

def synchronized(member):
    """
    @synchronized decorator.

    Lock a method for synchronized access only. The lock is stored to
    the function or class instance, depending on what is available.
    """

    @wraps(member)
    def wrapper(*args, **kwargs):
        lock = vars(member).get("_synchronized_lock", None)
        result = ""
        try:
            if lock is None:
                lock = vars(member).setdefault("_synchronized_lock", Lock())
            lock.acquire()
            result = member(*args, **kwargs)
            lock.release()
        except Exception as e:
            lock.release()
            raise e
        return result

    return wrapper