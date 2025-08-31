import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_objects import NAME, file
from bluer_options.host import signature as host_signature
from bluer_objects.graphics import add_signature
from bluer_objects.objects import signature as object_signature
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="add_signature",
)
parser.add_argument(
    "--application",
    type=str,
    default="",
)
parser.add_argument(
    "--header",
    type=str,
    default="",
    help="this|that",
)
parser.add_argument(
    "--filename",
    type=str,
    default="",
)
parser.add_argument(
    "--footer",
    type=str,
    default="",
    help="this|that",
)
parser.add_argument(
    "--item_name",
    default="tag",
    type=str,
)
parser.add_argument(
    "--log",
    default=1,
    type=int,
    help="0|1",
)
parser.add_argument(
    "--word_wrap",
    default=0,
    type=int,
    help="0|1",
)
args = parser.parse_args()

success = False
if args.task == "add_signature":
    success, image = file.load_image(args.filename)
    if success:
        success = file.save_image(
            args.filename,
            add_signature(
                image,
                [args.header] + [" | ".join(object_signature())],
                [args.footer] + [" | ".join([args.application] + host_signature())],
                word_wrap=args.word_wrap,
            ),
        )

    if success:
        logger.info(
            f"{NAME}.add_signature({args.filename},{args.header},{args.footer})"
        )
else:
    success = None


sys_exit(logger, NAME, args.task, success, log=args.log)
