import pytest
import numpy as np

from bluer_objects.logger import logger


@pytest.fixture
def test_image():
    matrix = (np.random.rand(512, 512, 3) * 255).astype(np.uint8)

    yield matrix

    logger.info("deleting test_image ...")
