from blueness.argparse.generic import main

from bluer_objects import NAME, VERSION, DESCRIPTION, ICON, README
from bluer_objects.logger import logger

main(
    ICON=ICON,
    NAME=NAME,
    DESCRIPTION=DESCRIPTION,
    VERSION=VERSION,
    main_filename=__file__,
    tasks={
        "build_README": lambda _: README.build_me(),
    },
    logger=logger,
)
