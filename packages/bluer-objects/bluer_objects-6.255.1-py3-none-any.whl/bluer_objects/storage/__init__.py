from typing import Tuple, List

from bluer_objects.storage.s3 import S3Interface
from bluer_objects.storage.base import StorageInterface
from bluer_objects.storage.WebDAV import WebDAVInterface
from bluer_objects.storage.WebDAVrequest import WebDAVRequestInterface
from bluer_objects.storage.WebDAVzip import WebDAVzipInterface
from bluer_objects.storage.policies import DownloadPolicy
from bluer_objects import env
from bluer_objects.logger import logger

interface = StorageInterface()

if env.BLUER_OBJECTS_STORAGE_INTERFACE == S3Interface.name:
    interface = S3Interface()
elif env.BLUER_OBJECTS_STORAGE_INTERFACE == WebDAVInterface.name:
    interface = WebDAVInterface()
elif env.BLUER_OBJECTS_STORAGE_INTERFACE == WebDAVRequestInterface.name:
    interface = WebDAVRequestInterface()
elif env.BLUER_OBJECTS_STORAGE_INTERFACE == WebDAVzipInterface.name:
    interface = WebDAVzipInterface()
else:
    logger.error(f"{env.BLUER_OBJECTS_STORAGE_INTERFACE}: interface not found.")
    assert False


def clear(
    do_dryrun: bool = True,
) -> bool:
    return interface.clear(
        do_dryrun=do_dryrun,
    )


def download(
    object_name: str,
    filename: str = "",
    log: bool = True,
    policy: DownloadPolicy = DownloadPolicy.NONE,
) -> bool:
    return interface.download(
        object_name=object_name,
        filename=filename,
        log=log,
        policy=policy,
    )


def ls(
    object_name: str,
    where: str = "local",
) -> Tuple[bool, List[str]]:
    return interface.ls(
        object_name=object_name,
        where=where,
    )


def upload(
    object_name: str,
    filename: str = "",
    public: bool = False,
    zip: bool = False,
    log: bool = True,
) -> bool:
    return interface.upload(
        object_name=object_name,
        filename=filename,
        public=public,
        zip=zip,
        log=log,
    )
