import numpy as np

from bluer_objects.graphics.text import render_text
from bluer_objects.env import DUMMY_TEXT


def test_graphics_text_render_text():
    assert isinstance(
        render_text(
            text=[DUMMY_TEXT for _ in range(10)],
            image_width=1024,
        ),
        np.ndarray,
    )
