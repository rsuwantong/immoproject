import argparse
import os
import sys
import logging
from pathlib import Path

from helper.utils import parse_params


def run_routine_from_cli(routines, default: str):
    """
    Run routines from CLI

    Parameters
    ----------
    routines: dict
        Mapping of routines names and classes
    default: str
        Default routine to run

    Returns
    -------

    """

    assert (
        default in routines
    ), f"Unknown default routine {default}. Should be one of {routines}"

    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Workflow CLI parser")

    # Workspace settings
    parser.add_argument(
        "--cwd", type=str, required=False, default=None, help="A path working directory"
    )

    parser.add_argument(
        "--routine",
        "-r",
        type=str,
        required=False,
        default=default,
        choices=list(routines.keys()),
        help=f"The routines to run. One of {list(routines.keys())}",
    )

    parser.add_argument(
        "--logging_level",
        type=str,
        required=False,
        default="INFO",
        help="The logging level",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
    )

    parser.add_argument(
        "--timestamp",
        "-t",
        type=str,
        required=False,
        default=None,
        help="Custom timestamp to use",
    )
    # Model settings
    parser.add_argument(
        "--params",
        "-p",
        type=str,
        nargs="+",
        required=False,
        help="Parameters to be passed to the model",
    )

    # Data specific args

    parser.add_argument(
        "--local_cache_root",
        type=str,
        required=False,
        default=None,
        help="Path to read/write local cached data relative to $HOME folder",
    )

    parser.add_argument(
        "--cache_to_prod",
        action="store_true",
        required=False,
        default=False,
        help="Cache on remote server or not (prod run only)",
    )

    parser.add_argument(
        "--cache_from_prod",
        action="store_true",
        required=False,
        default=False,
        help="Exclusively read cache from remote server",
    )

    parser.add_argument(
        "--server",
        action="store_true",
        required=False,
        default=False,
        help="Server (true) or local (false) run (default: false)",
    )

    args = parser.parse_args(sys.argv[1:])

    params = {}
    for s in args.params or []:
        k, v = s.split(":")
        params[k] = v

    # Default CWD set to home/tmp
    if args.cwd is None:
        cwd = os.path.join(Path.home(), "tmp")
        log.info(
            f"Working directory not set in Command Line Arguments, using default path {cwd}"
        )
    else:
        cwd = args.cwd

    job_config = parse_params(params)

    job_config["logging"]["level"] = args.logging_level
    job_config["general"]["mode"] = "server" if args.server else "local"

    if args.local_cache_root:
        job_config["cache"]["root_local_relative_to_home"] = args.local_cache_root
    job_config["cache"]["cache_to_prod"] = args.cache_to_prod
    job_config["cache"]["cache_from_prod"] = args.cache_from_prod

    if args.routine in routines:
        routine = routines[args.routine](cwd, job_config, args.timestamp)
    else:
        raise AttributeError(
            f"Unknown routine to run: '{args.routine}'. Must be one of {list(routines.keys())}"
        )

    routine.run_routine()
