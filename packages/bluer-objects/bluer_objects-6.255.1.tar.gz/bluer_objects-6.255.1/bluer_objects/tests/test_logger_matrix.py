import pytest
import cv2

from bluer_objects import objects
from bluer_objects.logger.matrix import log_matrix, log_matrix_hist
from bluer_objects.tests.test_graphics import test_image
from bluer_objects.env import DUMMY_TEXT


@pytest.mark.parametrize(
    ["verbose"],
    [
        [True],
        [False],
    ],
)
def test_log_matrix(
    test_image,
    verbose: bool,
):
    object_name = objects.unique_object("test_log_matrix")

    assert log_matrix(
        matrix=test_image,
        header=[DUMMY_TEXT for _ in range(4)],
        footer=[DUMMY_TEXT for _ in range(2)],
        filename=objects.path_of(
            filename="log.png",
            object_name=object_name,
        ),
        log_range=True,
        verbose=verbose,
    )

    assert log_matrix(
        matrix=test_image[:, :, 0],
        dynamic_range=(0, 255.0),
        header=[DUMMY_TEXT for _ in range(4)],
        footer=[DUMMY_TEXT for _ in range(2)],
        filename=objects.path_of(
            filename="log.png",
            object_name=object_name,
        ),
        colormap=cv2.COLORMAP_JET,
        log_range=True,
        verbose=verbose,
    )


@pytest.mark.parametrize(
    ["verbose"],
    [
        [True],
        [False],
    ],
)
def test_log_matrix_hist(
    test_image,
    verbose: bool,
):
    object_name = objects.unique_object("test_log_matrix_hist")

    assert log_matrix_hist(
        matrix=test_image,
        dynamic_range=(0, 255.0),
        header=[DUMMY_TEXT for _ in range(4)],
        footer=[DUMMY_TEXT for _ in range(2)],
        filename=objects.path_of(
            filename="log-histogram.png",
            object_name=object_name,
        ),
        verbose=verbose,
    )
