import logging
import tempfile
import os.path as op

from tornado import log


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def setup_logger():
    log.enable_pretty_logging()

    logger = get_logger()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(op.join(tempfile.gettempdir(), 'monitord.log'))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('{asctime}|{levelname:_<8}|{message}', style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger():
    return logging.getLogger('monitord')
