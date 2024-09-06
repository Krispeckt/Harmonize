from enum import Enum

__all__ = (
    "NodeStatus",
)


class NodeStatus(Enum):
    """
    Represents the status of a Lavalink node.
    """
    CONNECTED = 1
    CONNECTING = 2
    DISCONNECTED = 3
