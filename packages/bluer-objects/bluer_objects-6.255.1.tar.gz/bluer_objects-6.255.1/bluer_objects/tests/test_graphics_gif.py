import pytest
import glob

from bluer_objects import objects
from bluer_objects import storage
from bluer_objects.tests.test_objects import test_object
from bluer_objects.graphics.gif import generate_animated_gif


@pytest.mark.parametrize(
    ["scale"],
    [
        [1],
        [2],
    ],
)
def test_graphics_gif_generate_animated_gif(
    test_object,
    scale: int,
):
    list_of_images = list(glob.glob(objects.path_of("*.png", test_object)))

    assert generate_animated_gif(
        list_of_images,
        objects.path_of("test.gif", test_object),
        scale=scale,
    )
