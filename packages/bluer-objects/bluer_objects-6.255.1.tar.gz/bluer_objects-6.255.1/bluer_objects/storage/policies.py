from enum import Enum, auto


class DownloadPolicy(Enum):
    NONE = auto()
    DOESNT_EXIST = auto()
    DIFFERENT = auto()
