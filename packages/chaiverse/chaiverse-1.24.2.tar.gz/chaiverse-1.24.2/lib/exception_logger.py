from contextlib import contextmanager
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@contextmanager
def unsafe_swallow_exception(logging_label):
    try:
        yield logger
    except Exception as ex:
        logger.exception(f'CHAI_EXCEPTION:{logging_label} throws exception {repr(ex)}')
