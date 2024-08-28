from enum import Enum

__all__ = (
    "LoopStatus",
)


class LoopStatus(Enum):
    OFF = 0
    TRACK = 1
    QUEUE = 2
