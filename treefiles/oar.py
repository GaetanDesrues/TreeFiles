import logging
import subprocess
from datetime import time
from typing import List

import treefiles as tf


def start_oar(
    runme_str,
    oardir: [tf.Tree, str] = None,
    array_fname: str = None,
    walltime: [time, str] = time(minute=10),
    host: int = 1,
    core: int = 4,
    job_name: str = None,
    queue: str = "default",
    cmd_fname: str = None,
    runme_args: List[str] = None,
    do_run: bool = False,
) -> str:
    """
    Builds an oar command.

    Usage example:

    .. code::

            cdir = tf.Tree.new(__file__)
            sdir = cdir.dir("OarOut").dump(clean=True)

            res = start_oar(
                runme_str=cdir.path("runme.sh"),
                oardir=sdir,
                walltime=time(minute=10),
                queue="besteffort",
                core=2,
                cmd_fname=sdir.path("cmd.sh"),
                do_run=True,
            )

    :param runme_str: path to the runme script or command line
    :param oardir: directory for std out/err
    :param array_fname: path to the arguments file (array file)
    :param walltime: wall time of the job
    :param host: numbre of nodes
    :param core: number of cores
    :param job_name: job name
    :param queue: job queue ['default', 'besteffort']
    :param cmd_fname: path to a file to save the oar command
    :param runme_args: list of command line arguments given to the runme script
    :param do_run: whether to execute the command or not
    :return: The output of the oar command if `do_run` is True else the oar command
    """
    walltime = str(walltime)

    cmd = ["oarsub"]

    if job_name is not None:
        cmd.extend(["--name", f"{job_name}"])

    cmd.extend(
        [
            "--resource",
            f"/host={host}/core={core},walltime={walltime}",
            "-J",
            "--queue",
            f"{queue}",
            # "--directory",
            # sdir.abs(),
        ]
    )

    if oardir is not None:
        if isinstance(oardir, str):
            oardir = tf.Tree(oardir)
        jn = "OAR" if job_name is None else job_name
        cmd.extend(
            [
                "--stdout",
                oardir.path(f"{jn}.%jobid%.stdout"),
                "--stderr",
                oardir.path(f"{jn}.%jobid%.stderr"),
            ]
        )

    oarcmd = [runme_str]
    if runme_args is not None:
        oarcmd.extend(map(str, runme_args))

    cmd.append(f'{" ".join(oarcmd)}')

    if array_fname is not None:
        cmd.insert(1, "--array-param-file")
        cmd.insert(2, array_fname)

    if cmd_fname is not None:
        tf.dump_txt(cmd_fname, [cmd])
        log.debug(f"Find command in file://{cmd_fname}")

    if do_run:
        shell_output = subprocess.check_output(cmd)
        return shell_output.decode("utf-8")
    else:
        return " ".join(cmd)


log = logging.getLogger(__name__)
