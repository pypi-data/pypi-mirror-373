from bluer_objects import objects
from bluer_objects import storage
from bluer_objects.testing import create_test_asset


def test_storage():
    object_name = objects.unique_object("test_storage")

    assert create_test_asset(
        object_name=object_name,
        depth=10,
    )

    for filename in [
        "this.yaml",
        "subfolder/this.yaml",
        "test-00.png",
    ]:
        assert storage.upload(
            object_name=object_name,
            filename=filename,
        )

    assert storage.upload(object_name=object_name)

    for filename in [
        "this.yaml",
        "subfolder/this.yaml",
        "test-00.png",
    ]:
        assert storage.download(
            object_name=object_name,
            filename=filename,
        )

    assert storage.download(object_name=object_name)
