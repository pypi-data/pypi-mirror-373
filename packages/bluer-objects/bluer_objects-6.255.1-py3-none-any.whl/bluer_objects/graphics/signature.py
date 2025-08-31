from typing import List, Union
import numpy as np
from functools import reduce
import textwrap

from blueness import module

from bluer_objects import NAME
from bluer_objects import file
from bluer_objects.graphics.text import render_text
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def justify_text(
    text: Union[List[str], str],
    line_width: int = 80,
    return_str: bool = False,
) -> Union[List[str], str]:
    output = reduce(
        lambda x, y: x + y,
        [
            textwrap.wrap(line, width=line_width)
            for line in (text if isinstance(text, list) else [text])
        ],
        [],
    )

    return "\n".join(output) if return_str else output


def add_signature(
    image: np.ndarray,
    header: List[str],
    footer: List[str] = [],
    word_wrap: bool = True,
    line_width: int = 80,
) -> np.ndarray:
    if image is None or not image.shape:
        return image

    if word_wrap:
        header = justify_text(header, line_width=line_width)
        footer = justify_text(footer, line_width=line_width)

    justify_line = lambda line: (
        line if len(line) >= line_width else line + (line_width - len(line)) * " "
    )

    color_depth = image.shape[2] if len(image.shape) >= 3 else 1

    return np.concatenate(
        [
            render_text(
                text=justify_line(line),
                image_width=image.shape[1],
                color_depth=color_depth,
            )
            for line in header
        ]
        + [image]
        + [
            render_text(
                text=justify_line(line),
                image_width=image.shape[1],
                color_depth=color_depth,
            )
            for line in footer
        ],
        axis=0,
    )


def sign_filename(
    filename: str,
    header: List[str],
    footer: List[str],
    line_width: int = 80,
) -> bool:
    success, image = file.load_image(filename)
    if not success:
        return success

    if not file.save_image(
        filename,
        add_signature(
            image,
            header=[" | ".join(header)],
            footer=[" | ".join(footer)],
            line_width=line_width,
        ),
    ):
        return False

    logger.info("-> {}".format(filename))

    return True
