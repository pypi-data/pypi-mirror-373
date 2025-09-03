import threading
from contextlib import contextmanager


class TimeoutLock:
    def __init__(self):
        self._lock = threading.Lock()

    @contextmanager
    def acquire(self, timeout):
        result = False
        try:
            result = self._lock.acquire(timeout=timeout)
            yield result
        finally:
            if result:
                self._lock.release()

    def release(self):
        self._lock.release()
