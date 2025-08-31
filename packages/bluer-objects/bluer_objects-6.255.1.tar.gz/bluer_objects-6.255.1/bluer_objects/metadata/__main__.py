import argparse

from blueness import module
from blueness.argparse.generic import sys_exit


from bluer_objects import NAME
from bluer_objects.metadata.get import get
from bluer_objects.metadata.post import post
from bluer_objects.metadata.enums import MetadataSourceType
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    default="",
    help="get|post",
)
parser.add_argument(
    "--default",
    type=str,
    default="",
)
parser.add_argument(
    "--delim",
    type=str,
    default="",
)
parser.add_argument(
    "--dict_keys",
    type=int,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--dict_values",
    type=int,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--filename",
    type=str,
    default="metadata.yaml",
)
parser.add_argument(
    "--is_base64_encoded",
    type=int,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--key",
    type=str,
)
parser.add_argument(
    "--source",
    type=str,
)
parser.add_argument(
    "--source_type",
    type=str,
    default=MetadataSourceType.FILENAME.name.lower(),
    help="|".join([source_type.name.lower() for source_type in MetadataSourceType]),
)
parser.add_argument(
    "--value",
    type=str,
)
parser.add_argument(
    "--verbose",
    type=int,
    default="0",
    help="0|1",
)
args = parser.parse_args()

delim = " " if args.delim == "space" else args.delim

success = False
if args.task == "get":
    success = True
    output = get(
        key=args.key,
        default=args.default,
        source=args.source,
        source_type=MetadataSourceType[args.source_type.upper()],
        dict_keys=args.dict_keys,
        dict_values=args.dict_values,
        filename=args.filename,
    )
    print(delim.join(output) if isinstance(output, list) else output)
elif args.task == "post":
    success = post(
        key=args.key,
        value=args.value,
        filename=args.filename,
        source=args.source,
        source_type=MetadataSourceType[args.source_type.upper()],
        is_base64_encoded=args.is_base64_encoded,
        verbose=args.verbose == 1,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
