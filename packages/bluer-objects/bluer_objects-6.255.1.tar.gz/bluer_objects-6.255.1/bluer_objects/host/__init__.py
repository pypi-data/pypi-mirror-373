from typing import List

from bluer_ai.host import signature as bluer_ai_signature

from bluer_objects import fullname
from bluer_objects.host.functions import shell, unzip, zip


def signature() -> List[str]:
    return [
        fullname(),
    ] + bluer_ai_signature()
