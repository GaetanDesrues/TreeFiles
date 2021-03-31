import logging
import sys


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


def set_up_logger(logger, remove_handlers=True):
    if remove_handlers:
        for hdlr in logger.handlers:
            logger.removeHandler(hdlr)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(SimpleFormatter())

    logger.addHandler(console_handler)


def get_logger():
    log = logging.getLogger()
    set_up_logger(log)
    return log


def my_func():
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")


logging.basicConfig(level=logging.INFO)
log = get_logger()


if __name__ == "__main__":
    my_func()
