from enum import Enum

__all__ = (
    'EndReason',
)


class EndReason(Enum):
    FINISHED = 'finished'
    LOAD_FAILED = 'loadFailed'
    STOPPED = 'stopped'
    REPLACED = 'replaced'
    CLEANUP = 'cleanup'
