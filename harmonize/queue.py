from __future__ import annotations

from random import shuffle
from typing import TYPE_CHECKING, Optional, overload, Iterator

from harmonize.enums import LoopStatus
from harmonize.objects import MISSING

if TYPE_CHECKING:
    from harmonize.objects import Track
    from harmonize import Player

__all__ = (
    "Queue",
)


class Queue:
    def __init__(self, player: Player) -> None:
        """
        Initializes a new instance of the Queue class.

        Args:
            player (Player): The player instance associated with this queue.

        Returns:
            None
        """
        self._loop: LoopStatus = LoopStatus(0)
        self._history: list[Track] = []
        self._now: list[Track] = []
        self._current: Optional[Track] = None
        self._player: Player = player

    @property
    def current(self) -> Optional[Track]:
        """
        Gets the currently playing track in the queue.

        Returns:
            Optional[Track]: The currently playing track, or None if no track is playing.
        """
        return self._current

    @property
    def history(self) -> list[Track]:
        """
        Returns a copy of the history list, which contains all the tracks that have been played in the queue.

        Returns:
            list[Track]: A list of Track objects representing the history of tracks played in the queue.
        """
        return self._history.copy()

    @property
    def tracks(self) -> list[Track]:
        """
        Returns the list of tracks in the queue.

        Returns:
            list[Track]: A list of Track objects representing the tracks in the queue.
        """
        return self._now

    @property
    def listened_count(self) -> int:
        return len(self._history)

    @property
    def loop(self) -> LoopStatus:
        """
        Gets the loop status of the queue.

        Returns:
            LoopStatus: The loop status of the queue.
        """
        return self._loop

    def set_loop(self, value: LoopStatus, /) -> None:
        """
        Sets the loop status of the queue.

        Args:
            value (LoopStatus): The new loop status to set.

        Raises:
            ValueError: If the provided value is not an instance of LoopStatus.

        Returns:
            None
        """
        if not isinstance(value, LoopStatus):
            raise ValueError("Invalid loop value. Please provide LoopStatus enum.")
        self._loop = value

    @overload
    def add(self, track: Track) -> None:
        ...

    @overload
    def add(self, tracks: list[Track]) -> None:
        ...

    def add(self, **kwargs) -> None:
        """
        Adds a track or multiple tracks to the queue.

        Args:
            **kwargs: Keyword arguments containing either 'track' or 'tracks'.
                'track' (Track): A single track to add to the queue.
                'tracks' (list[Track]): A list of tracks to add to the queue.

        Raises:
            ValueError: If neither 'track' nor 'tracks' is provided in kwargs.

        Returns:
            None
        """
        if 'track' in kwargs:
            self._now.append(kwargs.pop("track"))
        elif 'tracks' in kwargs:
            self._now.extend(kwargs.pop("tracks"))
        else:
            raise ValueError("Invalid arguments. Please provide track or tracks.")

    def clear(self) -> None:
        """
        Clears the queue by removing all tracks from the current and history lists.

        Returns:
            None
        """
        self._now.clear()
        self._history.clear()

    def shuffle(self) -> None:
        """
        Shuffles the current queue in-place.

        Args:
            None

        Returns:
            None
        """
        shuffle(self._now)

    def reverse(self) -> None:
        """
        Reverses the current queue in-place.

        Returns:
            None
        """
        self._now.reverse()

    async def _go_to_next(self, track: Optional[Track] = MISSING) -> Optional[Track]:
        old = self._current
        if self.loop.value > 0 and self._current:
            match self.loop:
                case LoopStatus.TRACK:
                    if track is MISSING:
                        track = self._current
                case LoopStatus.QUEUE:
                    self._now.append(self._current)

        if track is MISSING:
            if not self._now:
                await self._player.stop()
                return self._player.dispatch('queue_end', self._player)

            track = self._now.pop(0)

        if old:
            self._history.insert(0, old)

        self._current = track
        return track

    def __repr__(self) -> str:
        return (
            f'<harmonize.Queue '
            f'tracks={len(self._now)}, '
            f'history={len(self._history)}, '
            f'current={self._current.title}, '
            f'loop={self._loop.value}>'
        )

    def __len__(self) -> int:
        return len(self._now)

    def __getitem__(self, index: int) -> Track:
        return self._now[index]

    def __iter__(self) -> Iterator[Track]:
        return iter(self._now)

    def __contains__(self, track: Track) -> bool:
        return track in self._now

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Queue):
            return self._now == other._now
        return False

    def __bool__(self) -> bool:
        return bool(self._now)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._now)

    def __str__(self) -> str:
        return str(self._now)
