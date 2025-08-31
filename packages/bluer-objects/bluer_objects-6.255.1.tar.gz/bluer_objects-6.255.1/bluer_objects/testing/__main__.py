import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_objects import NAME
from bluer_objects.testing import create_test_asset
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="create_test_asset",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--depth",
    type=int,
    default=10,
)
args = parser.parse_args()

success = False
if args.task == "create_test_asset":
    success = create_test_asset(
        object_name=args.object_name,
        depth=args.depth,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
