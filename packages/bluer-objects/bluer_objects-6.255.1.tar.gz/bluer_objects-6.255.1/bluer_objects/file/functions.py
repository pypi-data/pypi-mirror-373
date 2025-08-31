import urllib3
from functools import reduce
import fnmatch
from typing import Any, List, Union
import os
import shutil

from blueness import module
from bluer_options import string
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.env import abcli_object_path
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def absolute(
    filename: str,
    reference_path: Any = None,
) -> str:
    from bluer_objects.path import absolute as path_absolute

    return os.path.join(
        path_absolute(
            path(filename),
            os.getcwd() if reference_path is None else reference_path,
        ),
        name_and_extension(filename),
    )


def add_extension(
    filename: str,
    extension_: Any,
    force: bool = True,
):
    if not isinstance(extension_, str):
        extension_ = extension(extension_)

    filename, extension_as_is = os.path.splitext(filename)
    if extension_as_is != "":
        extension_as_is = extension_as_is[1:]

    if not force and extension_as_is == "":
        extension_ = extension_as_is

    return f"{filename}.{extension_}"


def add_prefix(
    filename: str,
    prefix: str,
) -> str:
    pathname, filename = os.path.split(filename)
    return os.path.join(pathname, f"{prefix}-{filename}")


def add_suffix(
    filename: str,
    suffix: str,
) -> str:
    filename, extension = os.path.splitext(filename)
    return f"{filename}-{suffix}{extension}"


def auxiliary(
    nickname: str,
    extension: str,
    add_timestamp: bool = True,
) -> str:
    filename = os.path.join(
        abcli_object_path,
        "auxiliary",
        "-".join(
            [nickname]
            + (
                [
                    string.pretty_date(
                        as_filename=True,
                        squeeze=True,
                        unique=True,
                    )
                ]
                if add_timestamp
                else []
            )
        )
        + f".{extension}",
    )

    os.makedirs(path(filename), exist_ok=True)

    return filename


def copy(
    source: str,
    destination: str,
    log: bool = True,
    overwrite: bool = True,
) -> bool:
    if not overwrite and exists(destination):
        if log:
            logger.info(f"✅ {destination}")
        return True

    try:
        os.makedirs(path(destination), exist_ok=True)

        # https://stackoverflow.com/a/8858026
        # better choice: copy2
        shutil.copyfile(source, destination)
    except:
        crash_report(f"{NAME}: copy({source},{destination}): failed.")
        return False

    if log:
        logger.info(f"{source} -copy-> {destination}")

    return True


def delete(
    filename: str,
    log: bool = False,
) -> bool:
    if not os.path.isfile(filename):
        return True

    try:
        os.remove(filename)
    except:
        crash_report(f"{NAME}: delete({filename}): failed.")
        return False

    if log:
        logger.info(f"deleted {filename}.")

    return True


def download(
    url: str,
    filename: str,
    log: bool = True,
    overwrite: bool = True,
) -> bool:
    if not overwrite and exists(filename):
        if log:
            logger.info(f"✅ {filename}")

        return True

    try:
        os.makedirs(path(filename), exist_ok=True)

        # https://stackoverflow.com/a/27406501
        with urllib3.PoolManager().request(
            "GET", url, preload_content=False
        ) as response, open(filename, "wb") as fp:
            shutil.copyfileobj(response, fp)

        response.release_conn()  # not 100% sure this is required though

    except:
        crash_report(f"{NAME}: download({url},{filename}): failed.")
        return False

    if log:
        logger.info(f"{NAME}: {url} -> {filename}")

    return True


def exists(
    filename: str,
) -> bool:
    return os.path.isfile(filename)


def extension(
    filename: Any,
) -> str:
    if isinstance(filename, str):
        _, extension = os.path.splitext(filename)
        if extension != "":
            if extension[0] == ".":
                extension = extension[1:]
        return extension

    if isinstance(filename, type):
        return "py" + filename.__name__.lower()

    return "py" + filename.__class__.__name__.lower()


def list_of(
    template: str,
    recursive: bool = False,
) -> List[str]:
    from bluer_objects import path as path_module

    if isinstance(template, list):
        return reduce(
            lambda x, y: x + y,
            [list_of(template_, recursive) for template_ in template],
            [],
        )

    if recursive:
        return reduce(
            lambda x, y: x + y,
            [
                list_of(
                    os.path.join(pathname, name_and_extension(template)),
                    recursive,
                )
                for pathname in path_module.list_of(path(template))
            ],
            list_of(template),
        )

    # https://stackoverflow.com/a/40566802
    template_path = path(template)
    if template_path == "":
        template_path = path_module.current()

    try:
        return [
            os.path.join(template_path, filename)
            for filename in fnmatch.filter(
                os.listdir(template_path),
                name_and_extension(template),
            )
        ]
    except:
        return []


def move(
    source: str,
    destination: str,
    log: bool = True,
) -> bool:
    try:
        os.makedirs(path(destination), exist_ok=True)

        # https://stackoverflow.com/a/8858026
        shutil.move(source, destination)
    except:
        crash_report(f"{NAME}: move({source},{destination}): failed.")
        return False

    if log:
        logger.info(f"{source} -move-> {destination}")

    return True


def name(
    filename: str,
) -> str:
    _, filename = os.path.split(filename)

    return filename if "." not in filename else ".".join(filename.split(".")[:-1])


def name_and_extension(
    filename: str,
) -> str:
    return os.path.basename(filename)


def path(
    filename: str,
) -> str:
    return os.path.split(filename)[0]


def relative(
    filename: str,
    reference_path: Union[None, str] = None,
):
    from bluer_objects.path import relative as path_relative

    return path_relative(
        path(filename),
        os.getcwd() if reference_path is None else reference_path,
    ) + name_and_extension(filename)


def size(
    filename: str,
) -> int:
    try:
        return os.path.getsize(filename)
    except:
        return 0
