from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harmonize.connection.node import Node

__all__ = (
    "Stats",
)


class Stats:
    __slots__ = (
        '_node',
        'is_fake',
        'uptime',
        'players',
        'playing_players',
        'memory_free',
        'memory_used',
        'memory_allocated',
        'memory_reservable',
        'cpu_cores',
        'system_load',
        'lavalink_load',
        'frames_sent',
        'frames_nulled',
        'frames_deficit',
        'penalty'
    )

    def __init__(self, node: Node, data: dict[str, any]) -> None:
        """
        Initializes a Stats object with the given node and data.

        Args:
            node (Node): The node associated with the stats.
            data (dict[str, any]): A dictionary containing the stats data.

        Returns:
            None
        """
        self._node = node

        self.is_fake: bool = data.get('isFake', False)
        self.uptime: int = data['uptime']

        self.players: int = data['players']
        self.playing_players: int = data['playingPlayers']

        memory = data['memory']
        self.memory_free: int = memory['free']
        self.memory_used: int = memory['used']
        self.memory_allocated: int = memory['allocated']
        self.memory_reservable: int = memory['reservable']

        cpu = data['cpu']
        self.cpu_cores: int = cpu['cores']
        self.system_load: float = cpu['systemLoad']
        self.lavalink_load: float = cpu['lavalinkLoad']

        frame_stats = data.get('frameStats') or {}
        self.frames_sent: int = frame_stats.get('sent', 0)
        self.frames_nulled: int = frame_stats.get('nulled', 0)
        self.frames_deficit: int = frame_stats.get('deficit', 0)

    @classmethod
    def empty(cls, node: Node) -> Stats:
        """
        Creates an empty Stats object with default values.

        Args:
            node (Node): The node associated with the stats.

        Returns:
            Stats: An empty Stats object.
        """
        data = {
            'isFake': True,
            'uptime': 0,
            'players': 0,
            'playingPlayers': 0,
            'memory': {
                'free': 0,
                'used': 0,
                'allocated': 0,
                'reservable': 0
            },
            'cpu': {
                'cores': 0,
                'systemLoad': 0,
                'lavalinkLoad': 0
            }
        }

        return cls(node, data)
