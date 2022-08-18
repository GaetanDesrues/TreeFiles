import logging
import os
import subprocess
from typing import List

from treefiles import timer
from treefiles.commons import get_iterable


class Viewer:
    BATCH = "batch"
    QGLVIEWER = "qglviewer"


@timer
def run_sofa(
    scene_path: str,
    sofa_path: str = None,
    iterations: int = 100,
    viewer: str = Viewer.BATCH,
    std_to_file: bool = False,
    timer_occur: int = 0,
    build: bool = False,
    run: bool = True,
    build_j: int = 6,
    dry_run: bool = False,
    plugins: List[str] = None,
):
    """
    Utilities for compiling and running a SOFA scene.

    :param scene_path: path to the scene
    :param sofa_path: path to runSofa executable, will into env variable `CARDIAC_SOFA_PATH` if None
    :param iterations: number of iterations for the sofa simulation
    :param viewer: see Viewer class
    :param std_to_file: write out logs or display in terminal
    :param timer_occur: if >0, interval for timer output
    :param build: if compilation is enabled
    :param run: if execution is enabled
    :param build_j: number of cores for compilation
    :param dry_run: will not actually call runSofa
    :param plugins: load given plugins (from https://www.sofa-framework.org/community/doc/using-sofa/runsofa/#launch-runsofa)
    """
    sofa_timer_args = [
        "--computationTimeSampling",  # Frequency of display of the computation time statistics, in number of animation steps.
        str(timer_occur),
        "-b",  # Output computation time statistics of the init
        "true",
    ]

    try:
        if sofa_path is None:
            sofa_path = os.environ["CARDIAC_SOFA_PATH"]

        log.debug(f"Found SOFA executable: {sofa_path!r}")

        ###
        ### Compile
        ###
        if build:
            if not sofa_path.endswith("/bin/runSofa"):
                log.error(f"Cannot compile: executable not valid {sofa_path!r}")
            else:
                log.info("Start compiling SOFA")

                build_path = sofa_path[:-12]
                buid_args = ["make", f"-j{build_j}"]

                if std_to_file:
                    out = os.path.join(os.path.dirname(scene_path), "build.stdout")
                    err = os.path.join(os.path.dirname(scene_path), "build.stderr")
                    with open(out, "w") as stdout:
                        with open(err, "w") as stderr:
                            subprocess.call(
                                buid_args, stdout=stdout, stderr=stderr, cwd=build_path
                            )
                else:
                    subprocess.call(buid_args, cwd=build_path)

        ###
        ### Run
        ###
        if run:
            log.info("Start running SOFA scene")

            args = [sofa_path, scene_path, "-g", viewer, "-n", str(iterations)]

            if timer_occur > 0:
                args.extend(sofa_timer_args)

            if plugins is not None:
                args.extend(["--load", *plugins])

            if std_to_file:
                out = os.path.join(os.path.dirname(scene_path), "Output_Python.stdout")
                err = os.path.join(os.path.dirname(scene_path), "Error_Python.stderr")
                log.debug(f"Calling '{' '.join(args)} > {out} 2> {err}'")
                if not dry_run:
                    with open(out, "w") as stdout:
                        with open(err, "w") as stderr:
                            subprocess.call(
                                args,
                                stdout=stdout,
                                stderr=stderr,
                            )
            else:
                log.debug(f"Calling '{' '.join(args)}'")
                if not dry_run:
                    subprocess.call(args)

            log.info("Finished runSofa")

    except Exception as e:
        log.error(
            f"\nCannot compile SOFA or run the generated scene file://{scene_path}: {e}"
        )


log = logging.getLogger(__name__)
