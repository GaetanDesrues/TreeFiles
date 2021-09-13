import multiprocessing.pool


"""
curr_proc = multiprocessing.current_process()
print("current process:", curr_proc.name, curr_proc.ident)

Links:
https://stackoverflow.com/questions/6974695/python-process-pool-non-daemonic
https://mail.python.org/pipermail/python-list/2011-March/600152.html
"""


class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess


class NestablePool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs["context"] = NoDaemonContext()
        super().__init__(*args, **kwargs)
