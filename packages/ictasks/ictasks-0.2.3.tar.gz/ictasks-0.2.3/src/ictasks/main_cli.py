"""
Main entry point for ictasks
"""

import os
from pathlib import Path
import argparse
import logging

from iccore import logging_utils

import ictasks

logger = logging.getLogger(__name__)


def taskfarm_cli(args):

    logging_utils.setup_default_logger()
    config = args.config.resolve() if args.config else None
    tasklist = args.tasklist.resolve() if args.tasklist else None
    ictasks.taskfarm(
        config_path=config, tasklist=tasklist, work_dir=args.work_dir.resolve()
    )


def main_cli():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        type=int,
        default=0,
        help="Dry run script - 0 can modify, 1 can read, 2 no modify - no read",
    )
    subparsers = parser.add_subparsers(required=True)

    taskfarm_parser = subparsers.add_parser("taskfarm")

    taskfarm_parser.add_argument(
        "--work_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Directory to run the session in",
    )
    taskfarm_parser.add_argument("--config", type=Path, help="Path to a config file")
    taskfarm_parser.add_argument("--tasklist", type=Path, help="Path to tasklist file")

    taskfarm_parser.set_defaults(func=taskfarm_cli)
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main_cli()
