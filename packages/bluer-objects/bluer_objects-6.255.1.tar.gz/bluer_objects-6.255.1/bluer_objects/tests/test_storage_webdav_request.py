import pytest

from bluer_objects import objects
from bluer_objects.testing import create_test_asset
from bluer_objects.storage import WebDAVRequestInterface


@pytest.mark.skip(reason="nodisk is super slow")
def test_storage_webdav_request():
    object_name = objects.unique_object("test_storage_webdav_request")

    assert create_test_asset(
        object_name=object_name,
        depth=10,
    )

    storage = WebDAVRequestInterface()

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
    assert success
    assert not list_of_files_cloud

    for filename in [
        "this.yaml",
        "subfolder/this.yaml",
        "test-00.png",
    ]:
        assert storage.upload(
            object_name=object_name,
            filename=filename,
        )

    success, list_of_files_cloud = storage.ls(
        object_name=object_name,
        where="cloud",
    )
    assert success
    assert list_of_files_cloud

    assert storage.upload(object_name=object_name)

    success, list_of_files_cloud = storage.ls(
        object_name=object_name,
        where="cloud",
    )
    assert success
    assert list_of_files_cloud
    assert list_of_files_cloud == list_of_files_local

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

    assert storage.delete(
        object_name=object_name,
        do_dryrun=False,
    )
