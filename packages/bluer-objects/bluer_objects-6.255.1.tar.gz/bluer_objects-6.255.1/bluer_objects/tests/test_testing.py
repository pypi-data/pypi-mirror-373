from bluer_objects import objects
from bluer_objects.testing import create_test_asset


def test_bluer_objects_testing():
    object_name = objects.unique_object("test_bluer_objects_testing")

    assert create_test_asset(object_name)
