import argparse
from functools import reduce
import os

from blueness.argparse.generic import sys_exit
from blueness import module

from bluer_objects import NAME
from bluer_objects.mlflow.logging import (
    log_artifacts,
    log_run,
)
from bluer_objects.mlflow.models import (
    list_registered_models,
    transition,
)
from bluer_objects.mlflow.objects import (
    get_id,
    rm,
)
from bluer_objects.mlflow.runs import (
    end_run,
    get_run_id,
    start_run,
)
from bluer_objects.mlflow.tags import (
    create_filter_string,
    get_tags,
    search,
    set_tags,
)
from bluer_objects.mlflow.testing import (
    test,
)
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    default="",
    help="clone_tags|create_filter_string|get_id|get_run_id|get_tags|list_registered_models|log_artifacts|log_run|rm|search|set_tags|start_end_run|test|transition",
)
parser.add_argument(
    "--count",
    type=int,
    default=-1,
)
parser.add_argument(
    "--offset",
    type=int,
    default=0,
)
parser.add_argument(
    "--default",
    type=str,
    default="",
)
parser.add_argument(
    "--delim",
    type=str,
    default=",",
)
parser.add_argument(
    "--description",
    type=str,
    default="",
)
parser.add_argument(
    "--destination_object",
    type=str,
    default="",
)
parser.add_argument(
    "--object_name",
    type=str,
    default=os.getenv("abcli_object_name"),
)
parser.add_argument(
    "--filter_string",
    type=str,
    help="tags.`keyword` = `value` - https://www.mlflow.org/docs/latest/search-runs.html",
)
parser.add_argument(
    "--input",
    type=str,
    default="name",
    help="id|name",
)
parser.add_argument(
    "--item_name_plural",
    type=str,
    default="object(s)",
)
parser.add_argument(
    "--model_name",
    type=str,
    default="",
)
parser.add_argument(
    "--output",
    type=str,
    default="name",
    help="id|name",
)
parser.add_argument(
    "--regex",
    type=str,
    default="",
)
parser.add_argument(
    "--log",
    type=int,
    default=1,
    help="0|1",
)
parser.add_argument(
    "--explicit_query",
    type=int,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--start_end",
    type=str,
    default="",
    help="start|end",
)
parser.add_argument(
    "--stage_name",
    type=str,
    default="",
    help="",
)
parser.add_argument(
    "--tag",
    type=str,
    default="",
)
parser.add_argument(
    "--source_objects",
    type=str,
    default="",
)
parser.add_argument(
    "--tags",
    type=str,
    default="",
    help="+this,that=which,what=12",
)
parser.add_argument(
    "--value",
    type=str,
    default="",
)
parser.add_argument(
    "--version",
    type=str,
    default="",
    help="",
)
args = parser.parse_args()

delim = " " if args.delim == "space" else args.delim

success = False
if args.task == "clone_tags":
    success, tags = get_tags(args.source_objects)
    if success:
        success = set_tags(args.destination_object, tags)
elif args.task == "create_filter_string":
    success = True
    print(create_filter_string(args.tags))
elif args.task == "rm":
    success = reduce(
        lambda x, y: x and y,
        [
            rm(
                object_name,
                is_id=args.input == "id",
            )
            for object_name in args.object_name.split(",")
            if object_name
        ],
        True,
    )
elif args.task == "get_tags":
    success, tags = get_tags(args.object_name)
    print(tags if not args.tag else tags.get(args.tag, args.default))
elif args.task == "get_id":
    success, id = get_id(args.object_name)
    print(id)
elif args.task == "get_run_id":
    success, list_of_id = get_run_id(
        args.object_name,
        args.count,
        args.offset,
    )

    print(delim.join(list_of_id))
elif args.task == "list_registered_models":
    success, list_of_models = list_registered_models()
    if args.log:
        logger.info(
            "{:,} model(s): {}".format(len(list_of_models), delim.join(list_of_models))
        )
    else:
        print(delim.join(list_of_models))
elif args.task == "log_artifacts":
    success = log_artifacts(
        args.object_name,
        args.model_name,
    )
elif args.task == "log_run":
    success = log_run(args.object_name)
elif args.task == "search":
    success = True

    filter_string = (
        create_filter_string(args.tags)
        if args.explicit_query == 0
        else "" if args.filter_string == "-" else args.filter_string
    )

    list_of_objects = search(filter_string)

    list_of_objects = list_of_objects[args.offset :]

    if args.count != -1:
        list_of_objects = list_of_objects[: args.count]

    if args.log:
        logger.info(
            "{:,} {}.".format(
                len(list_of_objects),
                args.item_name_plural,
            ),
        )
        for index, object_name in enumerate(list_of_objects):
            logger.info(f"#{index+1: 4d} - {object_name}")
    else:
        print(delim.join(list_of_objects))
elif args.task == "set_tags":
    success = set_tags(
        args.object_name,
        args.tags,
    )
elif args.task == "transition":
    success = transition(
        args.model_name,
        args.version,
        args.stage_name,
        description=args.description,
    )
elif args.task == "start_end_run":
    if args.start_end == "start":
        success = start_run(args.object_name)
    elif args.task == "end":
        success = end_run(args.object_name)
    else:
        success = False
        logger.info(f"expected start|end,received {args.start_end}.")
elif args.task == "test":
    success = test()
else:
    success = None

sys_exit(logger, NAME, args.task, success)
