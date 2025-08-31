from typing import List
import math

from blueness import module

from bluer_objects import NAME
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def generate_table(
    items: List[str],
    cols: int = 3,
    log: bool = True,
) -> List[str]:
    if not items:
        return []

    items_dict = {index: item for index, item in enumerate(items)}

    cols = min(cols, len(items))

    row_count = int(math.ceil(len(items) / cols))

    if log:
        logger.info(
            "{}.generate_table(): {} item(s), {} row(s)".format(
                NAME,
                len(items),
                row_count,
            )
        )

    return [
        "| {} |".format(" | ".join(cols * [" "])),
        "| {} |".format(" | ".join(cols * ["---"])),
    ] + [
        "| {} |".format(
            " | ".join(
                [items_dict.get(cols * row_index + index, "") for index in range(cols)]
            )
        )
        for row_index in range(row_count)
    ]
