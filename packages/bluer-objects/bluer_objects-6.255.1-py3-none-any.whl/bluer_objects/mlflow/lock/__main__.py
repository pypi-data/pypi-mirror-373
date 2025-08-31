import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_objects import NAME
from bluer_objects.mlflow.lock.functions import lock, unlock
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="lock | unlock",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--lock",
    type=str,
    default="lock",
)
parser.add_argument(
    "--timeout",
    type=int,
    default=-1,
    help="in seconds",
)
parser.add_argument(
    "--verbose",
    type=int,
    default=1,
    help="0 | 1",
)
args = parser.parse_args()

success = False
if args.task == "lock":
    success = lock(
        object_name=args.object_name,
        lock_name=args.lock,
        timeout=args.timeout,
        verbose=args.verbose == 1,
    )
elif args.task == "unlock":
    success = unlock(
        object_name=args.object_name,
        lock_name=args.lock,
        verbose=args.verbose == 1,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
