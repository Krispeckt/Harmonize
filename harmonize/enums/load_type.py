from enum import Enum

__all__ = (
    "LoadType",
)


class LoadType(Enum):
    TRACK = 'track'
    PLAYLIST = 'playlist'
    SEARCH = 'search'
    EMPTY = 'empty'
    ERROR = 'error'
