import os
from typing import Any, Union, List
import pathlib
import shutil

from blueness import module
from bluer_options import string
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.logger import logger
from bluer_objects.env import abcli_object_path


NAME = module.name(__file__, NAME)


def absolute(
    path: str,
    reference: Union[None, str] = None,
):
    if reference is None:
        reference = current()
    assert isinstance(reference, str)

    path = path.replace("/", os.sep)
    reference = reference.replace("/", os.sep)

    return (
        reference
        if not path
        else (
            path
            if path[0] != "."
            else str(pathlib.Path(os.path.join(reference, path)).resolve())
        )
    )


def auxiliary(
    nickname: str,
    add_timestamp: bool = True,
):
    path = os.path.join(
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
        ),
    )

    assert create(path)

    return path


def copy(
    source: str,
    destination: str,
) -> bool:
    if not create(parent(destination)):
        return False

    try:
        shutil.copytree(source, destination)
        return True
    except:
        crash_report(f"{NAME}: copy({source},{destination}): failed.")
        return False


def create(
    path: str,
    log: bool = False,
) -> bool:
    if not path or exists(path):
        return True

    try:
        os.makedirs(path)
    except:
        crash_report(f"{NAME}: create({path}): failed.")
        return False

    if log:
        logger.info(f"{NAME}.create({path})")

    return True


def current() -> str:
    return os.getcwd()


def delete(
    path: str,
) -> bool:
    try:
        # https://docs.python.org/3/library/shutil.html#shutil.rmtree
        shutil.rmtree(path)
        return True
    except:
        crash_report(f"{NAME}: delete({path}): failed.")
        return False


def exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)


def list_of(
    path: str,
    recursive: bool = False,
) -> List[str]:
    if not exists(path):
        return []

    # http://stackabuse.com/python-list-files-in-a-directory/
    output = []
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                continue

            path_name = os.path.join(path, entry.name)

            output.append(path_name)

            if recursive:
                output += list_of(path_name, recursive=recursive)
    except:
        crash_report(f"-{NAME}: list_of({path}): failed.")

    return output


def move(
    source: str,
    destination: str,
) -> bool:
    if not create(parent(destination)):
        return False

    try:
        shutil.move(source, destination)
        return True
    except:
        crash_report(f"{NAME}: move({source},{destination}): failed.")
        return False


def name(path: str) -> str:
    if not path:
        return path

    if path[-1] == os.sep:
        path = path[:-1]

    path_components = path.split(os.sep)
    return "" if not path_components else path_components[-1]


def parent(
    path: str,
    depth: int = 1,
) -> str:
    # Add os.sep at the end of path, if it already does not exist.
    if path:
        if path[-1] != os.sep:
            path = path + os.sep

    return os.sep.join(path.split(os.sep)[: -depth - 1]) + os.sep


def relative(
    path: str,
    reference: Union[Any, str] = None,
):
    # https://stackoverflow.com/a/918174
    return os.path.relpath(
        path,
        current() if reference is None else reference,
    )
