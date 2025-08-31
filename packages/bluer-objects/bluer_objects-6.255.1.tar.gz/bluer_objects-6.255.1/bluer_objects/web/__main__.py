import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_objects import NAME
from bluer_objects.web.functions import is_accessible
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="is_accessible",
)
parser.add_argument(
    "--url",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "is_accessible":
    success = True
    print(int(is_accessible(args.url)))
else:
    success = None

sys_exit(logger, NAME, args.task, success)
