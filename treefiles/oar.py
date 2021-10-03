import datetime
import logging
import subprocess
from typing import List, Union, Tuple

import treefiles as tf


def walltime(hours: int = 0, minutes: int = 0):
    s = datetime.timedelta(hours=hours, minutes=minutes)
    h, m = s.seconds // 3600, s.seconds // 60 % 60
    h += 24 * s.days
    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:00"


class Queue:
    DEFAULT = "default"
    BESTEFFORT = "besteffort"


class Program:
    OARSUB = ("oarsub",)
    OARCTL = ("oarctl", "sub")


class NotifyOar:
    RUNNING = "RUNNING"
    END = "END"
    ERROR = "ERROR"
    INFO = "INFO"
    SUSPENDED = "SUSPENDED"
    RESUMING = "RESUMING"
    # WAITING = "WAITING"
    # LAUNCHED = "LAUNCHED"
    # FINISHING = "FINISHING"
    # TERMINATED = "TERMINATED"
    end = [END, ERROR]

    def __init__(self, dest: str, tags: [str, List] = None):
        self.dest = dest
        if tags is None:
            tags = NotifyOar.end
        elif isinstance(tags, str):
            tags = [] if tags == "all" else [tags]
        self.tags = tags

    @property
    def exec(self):
        # self.dest = tf.Tree(self.dest).abs()
        return self.build_cmd("exec")

    @property
    def mail(self):
        return self.build_cmd("mail")

    def build_cmd(self, dtype: str):
        assert dtype in ["mail", "exec"]
        tags = ",".join(self.tags)
        if tags != "":
            tags = f"[{tags}]"
        return ["--notify", f'"{tags}{dtype}:{self.dest}"']


def start_oar(
    runme_str,
    logs_dir: Union[tf.Tree, str] = None,
    array_fname: str = None,
    wall_time: str = walltime(minutes=1),
    host: int = 1,
    core: int = 1,
    job_name: str = None,
    queue: str = Queue.DEFAULT,
    cmd_fname: str = None,
    runme_args: List[str] = None,
    do_run: bool = True,
    with_json: bool = False,
    notify: List = None,
    prgm: Tuple[str] = Program.OARSUB,
    stdout: str = None,
    stderr: str = None,
) -> Union[str, List[str]]:
    """
    Builds an oar command.

    Usage example:

    .. code::

            cdir = tf.Tree.new(__file__)
            sdir = cdir.dir("OarOut").dump(clean=True)

            res = start_oar(
                runme_str=cdir.path("runme.sh"),
                logs_dir=sdir,
                walltime=time(minute=10),
                queue="besteffort",
                core=2,
                cmd_fname=sdir.path("cmd.sh"),
                do_run=True,
            )

    :param runme_str: path to the runme script or command line
    :param logs_dir: directory for std out/err
    :param array_fname: path to the arguments file (array file)
    :param wall_time: wall time of the job
    :param host: numbre of nodes
    :param core: number of cores
    :param job_name: job name
    :param queue: job queue ['default', 'besteffort']
    :param cmd_fname: path to a file to save the oar command
    :param runme_args: list of command line arguments given to the runme script
    :param do_run: whether to execute the command or not
    :param with_json: add the -J option in oarsub command
    :param notify: notify options [List], you may use the class NotifyOar to build this option
    :param prgm: `oarsub` or `oarctl sub`
    :param stdout: path for stdout
    :param stderr: path for stderr, defaults to stdout if None
    :return: The output of the oar command if `do_run` is True else the oar command
    """
    cmd = list(prgm)

    if job_name is not None:
        cmd.extend(["--name", f"{job_name}"])

    cmd.extend(
        [
            "--resource",
            f"/host={host}/core={core},walltime={wall_time}",
            "--queue",
            f"{queue}",
        ]
    )

    if with_json:
        cmd.append("-J")

    if logs_dir is not None:
        if isinstance(logs_dir, str):
            logs_dir = tf.Tree(logs_dir)
        jn = "OAR" if job_name is None else job_name
        cmd.extend(
            [
                "--stdout",
                logs_dir.path(f"{jn}.%jobid%.stdout"),
                "--stderr",
                logs_dir.path(f"{jn}.%jobid%.stderr"),
            ]
        )

    if notify is not None:
        cmd.extend(notify)

    oarcmd = [runme_str]
    if runme_args is not None:
        oarcmd.extend(map(str, runme_args))

    cmd.append(f'{" ".join(oarcmd)}')
    print('gg', cmd)
    # cmd.extend(oarcmd)

    if array_fname is not None:
        cmd.insert(1, "--array-param-file")
        cmd.insert(2, array_fname)

    if stdout is not None:
        cmd.extend([">", stdout])
        if stderr is None:
            cmd.append("2>&1")
        else:
            cmd.extend(["2>", stderr])

    if cmd_fname is not None:
        tf.dump_txt(cmd_fname, [cmd])
        log.debug(f"Find command in file://{cmd_fname}")

    if do_run:
        shell_output = subprocess.check_output(cmd)
        return shell_output.decode("utf-8")
    else:
        return cmd


log = logging.getLogger(__name__)
