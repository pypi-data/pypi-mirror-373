import pytest
from typing import Union, List
import numpy as np

from bluer_options import string

from bluer_objects.env import DUMMY_TEXT
from bluer_objects.graphics.signature import add_signature, justify_text
from bluer_objects.tests.test_graphics import test_image


@pytest.mark.parametrize(
    ["line_width"],
    [
        [10],
        [80],
    ],
)
@pytest.mark.parametrize(
    ["word_wrap"],
    [
        [True],
        [False],
    ],
)
def test_graphics_signature_add_signature(
    line_width: int,
    word_wrap: bool,
    test_image,
):
    assert isinstance(
        add_signature(
            test_image,
            header=[DUMMY_TEXT],
            footer=[DUMMY_TEXT, DUMMY_TEXT],
            word_wrap=word_wrap,
            line_width=line_width,
        ),
        np.ndarray,
    )


@pytest.mark.parametrize(
    ["text"],
    [
        [string.random(length=800)],
        [[string.random(length=120) for _ in range(3)]],
    ],
)
@pytest.mark.parametrize(
    ["line_width"],
    [
        [80],
    ],
)
@pytest.mark.parametrize(
    ["return_str"],
    [
        [True],
        [False],
    ],
)
def test_justify_text(
    text: Union[str, List[str]],
    line_width: int,
    return_str: bool,
):
    justified_text = justify_text(
        text,
        line_width=line_width,
        return_str=return_str,
    )

    if return_str:
        assert isinstance(justified_text, str)
    else:
        assert isinstance(justified_text, list)

        for line in justified_text:
            assert len(line) <= line_width, f'len("{line}") > {line_width}'
