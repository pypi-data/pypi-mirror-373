from contextlib import contextmanager
import functools
import logging
import os
import signal
import sys
import threading
import time
from types import FrameType


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ShutdownHandler:
    def __init__(self, handler):
        self.handler = handler
        self.original_sigint_handler = None
        self.original_sigterm_handler = None

    def __enter__(self):
        if threading.current_thread() is threading.main_thread():
            self._register_shutdown_handler()
        else:
            logger.warning('Shutdown handler not registered because Python interpreter is not running in the main thread')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.original_sigint_handler:
            signal.signal(signal.SIGINT, self.original_sigint_handler)
        if self.original_sigterm_handler:
            signal.signal(signal.SIGTERM, self.original_sigterm_handler)
        logger.info('Shutdown handler de-registered')

    def _register_shutdown_handler(self):
        logger.info('Shutdown handler registered')
        self.original_sigint_handler = signal.getsignal(signal.SIGINT)
        self.original_sigterm_handler = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig: int, frame: FrameType) -> None:
        logger.warning(f'Received signal {sig}, running shutdown handler')
        self.handler(sig, frame)
        sys.exit(1)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper


class ShutdownAfter:
    def __init__(self, delay):
        self.delay = delay
        self.timer_thread = None

    def _send_sigint(self):
        time.sleep(self.delay)
        os.kill(os.getpid(), signal.SIGINT)

    def __enter__(self):
        if self.delay:
            self.timer_thread = threading.Thread(target=self._send_sigint)
            self.timer_thread.daemon = True
            self.timer_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is KeyboardInterrupt:
            print("Received SIGINT, handling interrupt...")

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper
