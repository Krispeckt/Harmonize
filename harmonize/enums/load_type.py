from enum import Enum

__all__ = (
    "LoadType",
)


class LoadType(Enum):
    """
    Represents the types of load requests.
    """
    TRACK = 'track'
    PLAYLIST = 'playlist'
    SEARCH = 'search'
    EMPTY = 'empty'
    ERROR = 'error'
