from blueness import module
import numpy as np

from bluer_options import string

from bluer_objects import NAME
from bluer_objects import file, objects
from bluer_objects.logger import logger


NAME = module.name(__file__, NAME)


def create_test_asset(
    object_name: str,
    depth: int = 10,
) -> bool:
    logger.info(f"{NAME}.create_test_asset: {object_name}")

    for suffix in range(depth):
        if not file.save_image(
            objects.path_of(
                object_name=object_name,
                filename=f"test-{suffix:02d}.png",
            ),
            (np.random.rand(512, 512, 3) * 255).astype(np.uint8),
            log=True,
        ):
            return False

    data = {
        string.random(length=depth): string.random(length=depth) for _ in range(depth)
    }

    for filename in [
        "this.yaml",
        "that.yaml",
        "subfolder/this.yaml",
        "subfolder/that.yaml",
        "test.yaml",
    ]:
        if not file.save_yaml(
            objects.path_of(
                object_name=object_name,
                filename=filename,
            ),
            data,
        ):
            return False

    if not file.save_json(
        objects.path_of(
            object_name=object_name,
            filename="test.json",
        ),
        data,
    ):
        return False

    return True
