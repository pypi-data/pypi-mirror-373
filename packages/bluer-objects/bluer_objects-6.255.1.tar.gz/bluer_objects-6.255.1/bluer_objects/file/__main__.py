import argparse
from tqdm import tqdm

from blueness import module
from blueness.argparse.generic import sys_exit
from bluer_options import string

from bluer_objects import file, NAME
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="replace | size",
)
parser.add_argument(
    "--filename",
    type=str,
)
parser.add_argument(
    "--this",
    type=str,
    help="<this-1+this-2+this-3>",
)
parser.add_argument(
    "--that",
    type=str,
    help="<that-1+that-2+that-3>",
)
parser.add_argument(
    "--size",
    type=int,
    default=16,
)
args = parser.parse_args()

success = False
if args.task == "replace":
    logger.info(f"{NAME}.{args.task}: {args.this} -> {args.that} in {args.filename}")

    success, content = file.load_text(args.filename)
    if success:
        for this, that in tqdm(zip(args.this.split("+"), args.that.split("+"))):
            content = [line.replace(this, that) for line in content]

        success = file.save_text(args.filename, content)
elif args.task == "size":
    print(string.pretty_bytes(file.size(args.filename)))
    success = True
else:
    success = None

sys_exit(logger, NAME, args.task, success)
