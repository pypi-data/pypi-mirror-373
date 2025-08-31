import matplotlib.pyplot as plt
from typing import Dict, Any, Union, List
import pandas as pd
import random
import os

from bluer_options import string

from bluer_objects import file, objects, path
from bluer_objects.graphics.signature import sign_filename

LOG_IMAGE_GRID_COLS = 5
LOG_IMAGE_GRID_ROWS = 3


def log_image_grid(
    items: Union[
        List[Dict[str, Any]],
        pd.DataFrame,
    ],
    filename: str,
    rows: int = LOG_IMAGE_GRID_ROWS,
    cols: int = LOG_IMAGE_GRID_COLS,
    log: bool = True,
    verbose: bool = False,
    scale: int = 2,
    shuffle: bool = False,
    header: List[str] = [],
    footer: List[str] = [],
    relative_path: bool = False,
) -> bool:
    if isinstance(items, pd.DataFrame):
        items = items.to_dict("records")

    while len(items) < rows * cols:
        items += [{"pass": True}]
    if shuffle:
        random.shuffle(items)

    items = items[: rows * cols]

    if relative_path:
        root_path = file.path(filename)
        for item in items:
            if item.get("filename", ""):
                item["filename"] = os.path.join(
                    root_path,
                    item["filename"],
                )

    _, axes = plt.subplots(
        rows,
        cols,
        figsize=(
            scale * cols,
            scale * rows,
        ),
    )
    axes = axes.flatten()

    image_shape = ""
    for i, item in enumerate(items):
        if item.get("pass", False):
            axes[i].axis("off")
            continue

        if item.get("filename", ""):
            success, item["image"] = file.load_image(
                item.get("filename", ""),
                log=verbose,
            )
            if not success:
                return False

        ax = axes[i]
        image = item["image"]
        image_shape = string.pretty_shape_of_matrix(image)
        ax.imshow(
            image,
            cmap="gray" if image.ndim == 2 else None,
        )
        ax.set_title(
            item.get("title", f"#{i}"),
            color=item.get("color", "black"),
            fontsize=10,
        )
        ax.axis("off")

    plt.tight_layout()

    if not file.save_fig(
        filename,
        log=verbose,
    ):
        return False

    return sign_filename(
        filename,
        [
            " | ".join(
                objects.signature(
                    info=file.name_and_extension(filename),
                    object_name=path.name(file.path(filename)),
                )
                + [image_shape]
                + header
            )
        ],
        [" | ".join(footer)],
    )
