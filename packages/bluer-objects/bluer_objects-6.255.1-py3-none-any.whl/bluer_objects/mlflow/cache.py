from typing import Tuple

from bluer_objects.mlflow.tags import get_tags, set_tags


def read(keyword: str) -> Tuple[bool, str]:
    success, tags = get_tags(keyword)

    return success, tags.get("referent", "")


def write(keyword: str, value: str) -> bool:
    return set_tags(keyword, {"referent": value})
