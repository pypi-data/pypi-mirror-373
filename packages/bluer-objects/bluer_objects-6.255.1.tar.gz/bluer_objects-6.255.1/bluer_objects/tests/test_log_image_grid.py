from bluer_objects import objects
from bluer_objects.testing import create_test_asset
from bluer_objects.logger.image import log_image_grid


def test_log_image_grid():
    object_name = objects.unique_object("test_log_image_grid")

    depth = 10

    assert create_test_asset(
        object_name=object_name,
        depth=depth,
    )

    assert log_image_grid(
        [
            {
                "filename": objects.path_of(
                    object_name=object_name,
                    filename=f"test-{suffix:02d}.png",
                )
                for suffix in range(depth)
            }
        ],
        objects.path_of(object_name=object_name, filename="image_grid.png"),
        rows=2,
        cols=5,
    )
