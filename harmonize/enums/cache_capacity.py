from enum import Enum

__all__ = (
    "CacheCapacity",
)


class CacheCapacity(Enum):
    """
    Represents the cache capacity parameters for Lavalink node requests.
    """
    LITTLE = 16
    SMALL = 64
    MEDIUM = 256
    LARGE = 1024
    HUGE = 2048
