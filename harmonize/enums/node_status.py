from enum import Enum

__all__ = (
    "NodeStatus",
)


class NodeStatus(Enum):
    CONNECTED = 1
    CONNECTING = 2
    DISCONNECTED = 3
