import logging
import sys
from typing import List


class SimpleFormatter(logging.Formatter):
    reset = "\x1b[0m"
    fmt = "{col}[%(levelname)s]{reset}\t[{origin}] %(message)s"
    origin = "\x1b[;3m%(name)s (%(funcName)s)\x1b[0m"

    FORMATS = {
        logging.DEBUG: "\x1b[;1m",
        logging.INFO: "\x1b[32m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m",
        logging.CRITICAL: "\x1b[31;1m",
    }

    def format(self, record):
        log_fmt = self.fmt.format(
            col=self.FORMATS.get(record.levelno, self.reset),
            reset=self.reset,
            origin=self.origin,
        )
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CSVFormatter(logging.Formatter):
    def __init__(self, formats=None, sep=",", **kw):
        super().__init__(**kw)

        if formats is None:
            formats = ["asctime", "levelname", "funcName", "message"]

        fmt = [f"%({x})s" for x in formats]
        self.fmt = sep.join(fmt)

    def format(self, record):
        formatter = logging.Formatter(self.fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def get_logger(
    remove_handlers=True, default=True, handlers: List[logging.Handler] = None
):
    """
    Format the root logger to remove default handlers and add a default `StreamHandler` with custom formatter `SimpleFormatter`.

    Usage example, place this in your main module

    .. code:: python

        logging.basicConfig(level=logging.INFO)
        log = get_logger()

    """
    logger = logging.getLogger()

    if remove_handlers:
        for hdlr in logger.handlers:
            logger.removeHandler(hdlr)

    if default:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(SimpleFormatter())
        logger.addHandler(console_handler)

    if handlers is not None:
        for x in handlers:
            logger.addHandler(x)

    return logger


def stream_csv_handler():
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(CSVFormatter(sep=", "))
    return h


if __name__ == "__main__":

    def my_func():
        logging.basicConfig(level=logging.INFO)
        log = get_logger(default=False, handlers=[stream_csv_handler()])

        log.debug("This is a debug message")
        log.info("This is an info message")
        log.warning("This is a warning message")
        log.error("This is an error message")
        log.critical("This is a critical message")

    my_func()
