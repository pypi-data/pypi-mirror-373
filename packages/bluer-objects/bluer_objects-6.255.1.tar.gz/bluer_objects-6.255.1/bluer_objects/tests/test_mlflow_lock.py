from bluer_options import string

from bluer_objects import objects
from bluer_objects.mlflow.lock.functions import lock, unlock


def test_mlflow_lock():
    object_name = objects.unique_object("test_mlflow_lock")
    lock_name = "lock-{}".format(string.random())

    assert lock(
        object_name=object_name,
        lock_name=lock_name,
        timeout=10,
    )

    assert not lock(
        object_name=object_name,
        lock_name=lock_name,
        timeout=10,
    )

    assert unlock(
        object_name=object_name,
        lock_name=lock_name,
    )
