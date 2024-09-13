from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harmonize.connection.node import Node

__all__ = (
    "Stats",
)


class Stats:
    """
    Represents the statistics of a Lavalink node.

    Attributes
    ----------
        is_fake : bool
            Inducing whether statistics are fake or not

        uptime : float
            The uptime of the node in milliseconds.

        players : int
            Number of players connected to this node

        playing_players : int
            Number of players currently playing on this node

        memory_free : int
            The free memory in bytes.

        memory_used : int
            The used memory in bytes.

        memory_allocated : int
            The allocated memory in bytes.

        memory_reservable : int
            The reservable memory in bytes.

        cpu_cores : int
            The number of CPU cores.

        system_load : float
            The system load average.

        lavalink_load : float
            The Lavalink load average.

        frames_sent : int
            The number of frames sent by the node.

        frames_nulled : int
            The number of frames nulled by the node.

        frames_deficit : int
            The number of frames deficit by the node.
    """

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
        'frames_deficit'
    )

    def __init__(self, node: Node, data: dict[str, any]) -> None:
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

        Parameters
        ----------
            node : :class:`harmonize.connection.Node`
                The node associated with the stats.

        Returns
        -------
            Stats
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
