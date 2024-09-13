from enum import Enum

__all__ = (
    "LoopStatus",
)


class LoopStatus(Enum):
    """
    Represents the loop status for a player queue.
    """
    OFF = 0
    TRACK = 1
    QUEUE = 2
