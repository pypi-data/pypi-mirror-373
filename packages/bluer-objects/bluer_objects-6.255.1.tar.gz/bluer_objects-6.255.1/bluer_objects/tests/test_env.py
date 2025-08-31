from bluer_ai.tests.test_env import test_bluer_ai_env

from bluer_objects import env
from bluer_objects.storage import (
    S3Interface,
    WebDAVInterface,
    WebDAVRequestInterface,
    WebDAVzipInterface,
)


def test_required_env():
    test_bluer_ai_env()


def test_bluer_objects_env():
    assert env.ABCLI_MLFLOW_EXPERIMENT_PREFIX

    assert env.S3_STORAGE_BUCKET
    assert env.S3_PUBLIC_STORAGE_BUCKET

    assert env.S3_STORAGE_ENDPOINT_URL
    assert env.S3_STORAGE_AWS_ACCESS_KEY_ID
    assert env.S3_STORAGE_AWS_SECRET_ACCESS_KEY

    assert env.BLUER_OBJECTS_STORAGE_INTERFACE in [
        S3Interface.name,
        WebDAVInterface.name,
        WebDAVRequestInterface.name,
        WebDAVzipInterface.name,
    ]

    assert env.MLFLOW_DEPLOYMENT

    assert isinstance(env.MLFLOW_LOCK_WAIT_FOR_CLEARANCE, int)
    assert env.MLFLOW_LOCK_WAIT_FOR_CLEARANCE > 0

    assert isinstance(env.MLFLOW_LOCK_WAIT_FOR_EXCLUSIVITY, int)
    assert env.MLFLOW_LOCK_WAIT_FOR_EXCLUSIVITY > 0

    assert env.WEBDAV_HOSTNAME
    assert env.WEBDAV_LOGIN
    assert env.WEBDAV_PASSWORD
