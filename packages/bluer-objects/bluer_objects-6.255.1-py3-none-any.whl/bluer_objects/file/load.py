from typing import Tuple, Any, List, Any
from copy import deepcopy
import json
import numpy as np

from blueness import module
from bluer_options import string
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def load(
    filename,
    ignore_error=False,
    default={},
) -> Tuple[bool, Any]:
    # https://wiki.python.org/moin/UsingPickle
    data = deepcopy(default)

    try:
        import dill

        with open(filename, "rb") as fp:
            data = dill.load(fp)

        return True, data
    except:
        if not ignore_error:
            crash_report(f"{NAME}: load({filename}): failed.")

        return False, data


def load_dataframe(
    filename,
    ignore_error=False,
    log=False,
) -> Tuple[bool, Any]:
    success = False
    df = None

    try:
        import pandas

        df = pandas.read_csv(filename)

        success = True
    except:
        if not ignore_error:
            crash_report(f"{NAME}: load_dataframe({filename}): failed.")

    if success and log:
        logger.info(
            "loaded {} row(s) of {} from {}".format(
                len(df),
                ", ".join(df.columns),
                filename,
            )
        )

    return success, df


def load_image(
    filename,
    ignore_error=False,
    log=False,
) -> Tuple[bool, np.ndarray]:
    import cv2

    success = True
    image = np.empty((0,))

    try:
        image = cv2.imread(filename)

        if len(image.shape) == 3:
            if image.shape[2] == 4:
                image = image[:, :, :3]

            image = np.flip(image, axis=2)

    except:
        if not ignore_error:
            crash_report(f"{NAME}: load_image({filename}): failed.")
        success = False

    if success and log:
        logger.info(
            "loaded {} from {}".format(
                string.pretty_shape_of_matrix(image),
                filename,
            )
        )

    return success, image


def load_json(
    filename,
    ignore_error=False,
    default={},
) -> Tuple[bool, Any]:
    success = False
    data = default

    try:
        with open(filename, "r") as fh:
            data = json.load(fh)

        success = True
    except:
        if not ignore_error:
            crash_report(f"{NAME}: load_json({filename}): failed.")

    return success, data


def load_matrix(
    filename: str,
    ignore_error=False,
    log: bool = False,
) -> Tuple[bool, np.ndarray]:
    success = True
    matrix: np.ndarray = np.empty((0,))

    try:
        matrix = np.load(filename)
    except:
        if not ignore_error:
            crash_report(f"{NAME}: load_matrix({filename}) failed.")
        success = False

    if success and log:
        logger.info(
            "loaded {} from {}".format(
                string.pretty_shape_of_matrix(matrix),
                filename,
            )
        )

    return success, matrix


def load_text(
    filename,
    ignore_error=False,
    log=False,
) -> Tuple[bool, List[str]]:
    success = True
    text = []

    try:
        with open(filename, "r") as fp:
            text = fp.read().splitlines()
    except:
        success = False
        if not ignore_error:
            crash_report(f"{NAME}: load_text({filename}): failed.")

    if success and log:
        logger.info("loaded {} line(s) from {}.".format(len(text), filename))

    return success, text


def load_xml(
    filename,
    ignore_error=False,
    default={},
) -> Tuple[bool, Any]:
    success = False
    data = default

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(filename)
        data = tree.getroot()

        success = True
    except:
        if not ignore_error:
            crash_report(f"{NAME}: load_xml({filename}): failed.")

    return success, data


def load_yaml(
    filename,
    ignore_error=False,
    default={},
) -> Tuple[bool, Any]:
    success = False
    data = default

    try:
        import yaml

        with open(filename, "r") as fh:
            data = yaml.safe_load(fh)

        success = True
    except:
        if not ignore_error:
            crash_report(f"{NAME}: load_yaml({filename}): failed.")

    return success, data
