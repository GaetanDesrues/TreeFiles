import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class CustomFormatter(logging.Formatter):
    reset = "\x1b[0m"
    # fmt = "[ {}%(levelname)s{} ]\t[\x1b[;3m%(name)s (%(funcName)s)\x1b[0m] %(message)s"  # \t(%(funcName)s:%(filename)s:l.%(lineno)d)"
    fmt = "{}[%(levelname)s]{}\t[{origin}] %(message)s"
    pfmt = "\t --> From: file://%(pathname)s:%(lineno)s"
    origin = "\x1b[;3m%(name)s (%(funcName)s)\x1b[0m"

    FORMATS = {
        logging.DEBUG: "\x1b[;1m",
        logging.INFO: "\x1b[32m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m",
        logging.CRITICAL: "\x1b[31;1m",
    }

    def format(self, record):
        ori = self.origin
        fmt = self.fmt
        # if "__main__" in record.name:
        #     ori = "\x1b[;3mCore\x1b[0m"
        # else:
        fmt += self.pfmt
        # record.name = record.name.replace("gaetools.", "")
        log_fmt = fmt.format(self.FORMATS.get(record.levelno), self.reset, origin=ori)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


FORMATTER = CustomFormatter()
FORMATTER_FILE = logging.Formatter(
    "%(asctime)s [ %(levelname)s ]\t[%(name)s] %(message)s \t(%(funcName)s:%(filename)s:l.%(lineno)d)"
)


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


# def get_file_handler():
#     file_handler = RotatingFileHandler(LOG_FILE, backupCount=1, maxBytes=1e5)
#     file_handler.setFormatter(FORMATTER_FILE)
#     return file_handler


def getLog(
    logger_name, level=logging.DEBUG, file=False, console=True, name_is_file=False
):
    if name_is_file:
        logger_name = os.path.basename(logger_name)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    if console:
        logger.addHandler(get_console_handler())
    if file:
        raise NotImplementedError
        # logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger


def main():
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")


log = getLog(__name__)


if __name__ == "__main__":
    main()
