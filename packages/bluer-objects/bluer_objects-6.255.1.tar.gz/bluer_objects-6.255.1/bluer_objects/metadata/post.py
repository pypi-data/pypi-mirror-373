from typing import Any
import base64
import copy

from blueness import module

from bluer_objects.metadata.enums import MetadataSourceType
from bluer_objects import NAME, file
from bluer_objects import objects
from bluer_objects import storage
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def post(
    key: str,
    value: Any,
    filename: str = "metadata.yaml",
    source=".",
    source_type: MetadataSourceType = MetadataSourceType.FILENAME,
    is_base64_encoded=False,
    verbose: bool = False,
) -> bool:
    if is_base64_encoded:
        value = str(base64.b64decode(value))

    filename = source_type.filename(source, filename)

    _, metadata = file.load_yaml(filename, ignore_error=True)

    metadata[key] = copy.deepcopy(value)

    logger.info(
        "{}.post[{}]: {}{}".format(
            NAME,
            filename,
            key,
            f"={value}" if verbose else "",
        )
    )

    return file.save_yaml(filename, metadata)


def post_to_file(
    filename: str,
    key: str,
    value: Any,
    **kwargs,
) -> bool:
    return post(
        key=key,
        value=value,
        source=filename,
        source_type=MetadataSourceType.FILENAME,
        **kwargs,
    )


def post_to_object(
    object_name: str,
    key: str,
    value: Any,
    download: bool = False,
    upload: bool = False,
    **kwargs,
) -> bool:
    if download and not storage.download(
        object_name=object_name,
        filename="metadata.yaml",
    ):
        return False

    if not post(
        key=key,
        value=value,
        source=object_name,
        source_type=MetadataSourceType.OBJECT,
        **kwargs,
    ):
        return False

    return not upload or storage.upload(
        object_name=object_name,
        filename="metadata.yaml",
    )


def post_to_path(
    path: str,
    key: str,
    value: Any,
    **kwargs,
) -> bool:
    return post(
        key=key,
        value=value,
        source=path,
        source_type=MetadataSourceType.PATH,
        **kwargs,
    )
