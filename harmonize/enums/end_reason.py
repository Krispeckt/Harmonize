from enum import Enum

__all__ = (
    'EndReason',
)


class EndReason(Enum):
    """
    Represents the end reasons for a player.
    """
    FINISHED = 'finished'
    LOAD_FAILED = 'loadFailed'
    STOPPED = 'stopped'
    REPLACED = 'replaced'
    CLEANUP = 'cleanup'
