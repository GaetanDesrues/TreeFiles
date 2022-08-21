import signal
from contextlib import contextmanager


@contextmanager
def timeout(t):
    """https://www.jujens.eu/posts/en/2018/Jun/02/python-timeout-function/"""
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(t)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError
