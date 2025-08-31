import argparse
import glob

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_objects import NAME, objects
from bluer_objects.graphics.gif import generate_animated_gif
from bluer_objects.graphics import screen
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    default="",
    help="generate_animated_gif|get_screen_size",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--suffix",
    default=".png",
    type=str,
)
parser.add_argument(
    "--output_filename",
    default="",
    type=str,
    help="blank: <object-name>.gif",
)
parser.add_argument(
    "--frame_duration",
    default=150,
    type=int,
    help="ms",
)
parser.add_argument(
    "--scale",
    default=1,
    type=int,
)

args = parser.parse_args()

success = False
if args.task == "generate_animated_gif":
    success = generate_animated_gif(
        list_of_images=sorted(
            list(
                glob.glob(
                    objects.path_of(
                        f"*{args.suffix}",
                        args.object_name,
                    )
                )
            )
        ),
        output_filename=objects.path_of(
            filename=(
                args.output_filename
                if args.output_filename
                else "{}{}.gif".format(
                    args.object_name,
                    f"-{args.scale}X" if args.scale != 1 else "",
                )
            ),
            object_name=args.object_name,
        ),
        frame_duration=args.frame_duration,
        scale=args.scale,
    )
elif args.task == "get_screen_size":
    success = True
    print("x".join([str(value) for value in screen.get_size()]))
else:
    success = None

sys_exit(logger, NAME, args.task, success)
