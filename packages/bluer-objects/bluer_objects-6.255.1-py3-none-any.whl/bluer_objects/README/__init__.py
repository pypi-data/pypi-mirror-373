import os

from blueness import module

from bluer_options.help.functions import get_help
from bluer_objects import NAME as MY_NAME
from bluer_objects import file
from bluer_objects.README.functions import build
from bluer_objects.README.items import Items
from bluer_objects.help.functions import help_functions
from bluer_objects.logger import logger

MY_NAME = module.name(__file__, MY_NAME)


def build_me() -> bool:
    from bluer_objects import NAME, VERSION, REPO_NAME, ICON

    return all(
        build(
            path=os.path.join(file.path(__file__), path),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for path in [
            "../..",
            ".",
            # aliases
            "../docs/aliases/clone.md",
            "../docs/aliases/download.md",
            "../docs/aliases/gif.md",
            "../docs/aliases/host.md",
            "../docs/aliases/ls.md",
            "../docs/aliases/metadata.md",
            "../docs/aliases/mlflow.md",
            "../docs/aliases/upload.md",
            # modules
            "../mlflow/lock",
        ]
    )
