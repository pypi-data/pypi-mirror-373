import numpy as np

from bluer_objects.graphics.frame import add_frame
from bluer_objects.tests.test_graphics import test_image


def test_graphics_frame_add_frame(test_image):
    assert isinstance(
        add_frame(test_image, width=12),
        np.ndarray,
    )
