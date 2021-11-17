import logging
import sys
from typing import List


class SimpleFormatter(logging.Formatter):
    colors = {
        "reset": "\x1b[0m",
        logging.DEBUG: "\x1b[;1m",
        logging.INFO: "\x1b[32m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m",
        logging.CRITICAL: "\x1b[31;1m",
    }
    fonts = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARN",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRIT",
    }

    def __init__(self, origin: bool = True):
        fmt = self.set_fmt_(origin)
        super().__init__(fmt, style="{")

    @staticmethod
    def set_fmt_(origin: bool):
        s = "{color}[{levelname}]{reset}{space}"
        if origin:
            s += "[\x1b[;3m{name}{funcName}\x1b[0m] "
        s += "{message}"
        return s

    def get_update(self, record):
        if record.funcName == "<module>":
            record.funcName = ""
        else:
            record.funcName = f" ({record.funcName})"

        record.levelname = self.fonts.get(record.levelno, record.levelname)

        return {
            "color": self.colors.get(record.levelno, self.colors["reset"]),
            "space": " " * max(0, 6 - len(record.levelname)),
            "reset": self.colors["reset"],
        }

    def format(self, record):
        record.__dict__.update(self.get_update(record))
        return super().format(record)


class HtmlFormatter(logging.Formatter):
    reset = "</font>"
    fmt = "{col}[%(levelname)s]{reset} [{origin}] %(message)s<br>"
    origin = "%(name)s (%(funcName)s)"

    FORMATS = {
        logging.DEBUG: '<font color="Grey">',
        logging.INFO: '<b><font color="Green">',
        logging.WARNING: '<font color="Orange">',
        logging.ERROR: '<font color="Red">',
        logging.CRITICAL: '<b><font color="Red">',
    }

    def format(self, record):
        col = self.FORMATS.get(record.levelno, self.reset)
        log_fmt = self.fmt.format(
            col=col,
            reset=f"{self.reset}</b>" if "<b>" in col else self.reset,
            origin=self.origin,
        )
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record).replace("\n", "<br>")


class CSVFormatter(logging.Formatter):
    def __init__(self, formats=None, sep=", ", **kw):
        super().__init__(**kw)

        if formats is None:
            formats = ["asctime", "levelname", "funcName", "message"]

        fmt = [f"%({x})s" for x in formats]
        self.fmt = sep.join(fmt)

    def format(self, record):
        formatter = logging.Formatter(self.fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def get_logger(
    remove_handlers=True,
    default=True,
    handlers: List[logging.Handler] = None,
    origin: bool = True,
):
    """
    Format the root logger to remove default handlers and add a default `StreamHandler` with custom formatter `SimpleFormatter`.

    Usage example, place this in your main module

    .. code:: python

        logging.basicConfig(level=logging.INFO)
        log = get_logger()

    """
    logger = logging.getLogger()
    logging.getLogger("matplotlib").setLevel(logging.ERROR)

    if remove_handlers:
        for hdlr in logger.handlers:
            logger.removeHandler(hdlr)

    if default:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(SimpleFormatter(origin))
        logger.addHandler(console_handler)

    if handlers is not None:
        for x in handlers:
            logger.addHandler(x)

    return logger


def get_csv_logger():
    """
    Calls a treefile logger formatted for files output, no colors but timestamps

    .. code:: python

        logging.basicConfig(level=logging.INFO)
        log = get_csv_logger()

    """
    return get_logger(default=False, handlers=[stream_csv_handler()])


def stream_csv_handler(**kwargs):
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(CSVFormatter(**kwargs))
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
