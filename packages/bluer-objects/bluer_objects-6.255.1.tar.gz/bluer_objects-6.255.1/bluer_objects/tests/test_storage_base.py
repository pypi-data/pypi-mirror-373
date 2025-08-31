from bluer_objects import objects
from bluer_objects.testing import create_test_asset
from bluer_objects.storage import StorageInterface


def test_storage_base():
    object_name = objects.unique_object("test_storage_base")

    assert create_test_asset(
        object_name=object_name,
        depth=10,
    )

    storage = StorageInterface()

    success, list_of_files_local = storage.ls(
        object_name=object_name,
        where="local",
    )
    assert success
    assert list_of_files_local

    success, list_of_files_cloud = storage.ls(
        object_name=object_name,
        where="cloud",
    )
    assert not success
    assert not list_of_files_cloud

    assert storage.upload(object_name=object_name)

    success, list_of_files_cloud = storage.ls(
        object_name=object_name,
        where="cloud",
    )
    assert not success
    assert not list_of_files_cloud

    assert storage.download(object_name=object_name)
