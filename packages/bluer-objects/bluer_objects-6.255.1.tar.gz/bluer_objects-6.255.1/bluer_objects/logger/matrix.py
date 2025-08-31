from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import math
import cv2

from blueness import module
from bluer_options import string
from bluer_ai.host import signature

from bluer_objects import NAME
from bluer_objects import file
from bluer_objects.graphics.signature import add_signature, justify_text
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def log_matrix(
    matrix: np.ndarray,
    header: List[str],
    footer: List[str],
    filename: str,
    dynamic_range: Tuple[float] = (-100, 100),
    line_width: int = 80,
    min_width: int = 1200,
    max_width: int = 2400,
    colorbar_width: int = 20,
    colormap: int = -1,  # example: cv2.COLORMAP_JET
    invert_color_map: bool = True,
    invert_color_map_rgb: bool = True,
    verbose: bool = False,
    log: bool = True,
    log_range: bool = False,
    log_shape_of_matrix: bool = True,
    suffix: List[np.ndarray] = [],
) -> bool:
    if log:
        logger.info(
            "{}.log_matrix({})".format(
                NAME,
                string.pretty_shape_of_matrix(matrix),
            )
        )

    shape_of_matrix = string.pretty_shape_of_matrix(matrix)

    range_signature: List[str] = (
        [f"range: {string.pretty_range_of_matrix(matrix)}"] if log_range else []
    )

    scale = 1
    if min_width != -1 and matrix.shape[1] < min_width and matrix.shape[1] > 0:
        scale = int(math.ceil(min_width / matrix.shape[1]))
    elif max_width != -1 and (
        matrix.shape[0] > max_width or matrix.shape[1] > max_width
    ):
        scale = min([max_width / matrix.shape[index] for index in [0, 1]])

    if scale != 1:
        if verbose:
            logger.info(f"scale: {scale}")

        matrix = cv2.resize(
            matrix,
            (
                int(scale * matrix.shape[1]),
                int(scale * matrix.shape[0]),
            ),
            interpolation=cv2.INTER_NEAREST_EXACT,
        )

    if colormap != -1:
        normalized_matrix = (matrix - dynamic_range[0]) / (
            dynamic_range[1] - dynamic_range[0]
        )
        normalized_matrix[normalized_matrix < 0] = 0
        normalized_matrix[normalized_matrix > 1] = 1

        colored_matrix = cv2.applyColorMap(
            (
                (1 - normalized_matrix if invert_color_map else normalized_matrix) * 255
            ).astype(np.uint8),
            colormap,
        )
        if not invert_color_map_rgb:
            colored_matrix = colored_matrix[:, :, [2, 1, 0]]

        gradient = (
            255
            * np.linspace(0, 1, colored_matrix.shape[0]).reshape(-1, 1)
            * np.ones((1, colorbar_width))
        ).astype(np.uint8)
        colorbar = cv2.applyColorMap(gradient, colormap)
        if not invert_color_map:
            colorbar = np.flipud(colorbar)
        if not invert_color_map_rgb:
            colorbar = colorbar[:, :, [2, 1, 0]]

        colored_matrix = np.hstack(
            (
                colored_matrix,
                np.zeros(
                    (colored_matrix.shape[0], colorbar_width // 2, 3),
                    dtype=np.uint8,
                ),
                colorbar,
            )
        )

        matrix = colored_matrix

    if suffix:
        if scale != 1:
            suffix = [
                cv2.resize(
                    matrix,
                    (
                        int(scale * matrix.shape[1]),
                        int(scale * matrix.shape[0]),
                    ),
                    interpolation=cv2.INTER_NEAREST_EXACT,
                )
                for matrix in suffix
            ]

        matrix = np.concatenate([matrix] + suffix, axis=1)

    matrix = add_signature(
        matrix,
        header=[
            " | ".join(
                header
                + ([shape_of_matrix] if log_shape_of_matrix else [])
                + [
                    f"scale: {scale:.2f}X",
                ]
                + (
                    []
                    if colormap == -1
                    else [
                        "dynamic-range: ( {:.03f} , {:.03f} )".format(
                            dynamic_range[0],
                            dynamic_range[1],
                        ),
                    ]
                )
                + range_signature
            )
        ],
        footer=[" | ".join(footer + signature())],
        word_wrap=True,
        line_width=line_width,
    )

    return file.save_image(filename, matrix, log=verbose)


def log_matrix_hist(
    matrix: np.ndarray,
    dynamic_range: Tuple[float],
    filename: str,
    header: List[str] = [],
    footer: List[str] = [],
    line_width: int = 80,
    bins: int = 64,
    ylabel: str = "frequency",
    log: bool = True,
    verbose: bool = False,
) -> bool:
    if log:
        logger.info(
            "{}.log_matrix_hist({})".format(
                NAME,
                string.pretty_shape_of_matrix(matrix),
            )
        )

    plt.figure(figsize=(10, 6))
    plt.hist(
        matrix.ravel(),
        bins=bins,
        range=dynamic_range,
    )
    plt.title(
        justify_text(
            " | ".join(
                header
                + [
                    string.pretty_shape_of_matrix(matrix),
                    f"dynamic-range: {dynamic_range}",
                    f"bins: {bins}",
                ]
            ),
            line_width=line_width,
            return_str=True,
        )
    )
    plt.xlabel(
        justify_text(
            " | ".join(footer + signature()),
            line_width=line_width,
            return_str=True,
        )
    )
    plt.ylabel(ylabel)
    plt.grid(True)

    return file.save_fig(filename, log=verbose)
