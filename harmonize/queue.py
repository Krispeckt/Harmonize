from __future__ import annotations

from random import shuffle
from typing import TYPE_CHECKING, Optional, overload, Iterator

from harmonize.enums import LoopStatus
from harmonize.objects import MISSING

if TYPE_CHECKING:
    from harmonize.objects import Track, PlaylistInfo, LoadResult
    from harmonize import Player

__all__ = (
    "Queue",
)


class Queue:
    """
    Represents a queue of tracks for a Discord voice player.

    Operations
    ----------
        .. describe:: len(x)

            Returns the number of tracks in the queue.

        .. describe:: x == y

            Checks if two queues are the same.

        .. describe:: x != y

            Checks if two filters are not the same.

        .. describe:: x >= y

            Checks if the first queue is greater or equal to the second queue.

        .. describe:: x <= y

            Checks if the first queue is less than or equal to the second queue.

        .. describe:: x > y

            Checks if the first queue is greater than the second queue.

        .. describe:: x < y

            Checks if the first queue is less than the second queue.

        .. describe:: for y in x

            Returns an iterator over the tracks in the queue.

        .. describe:: x[key]

            Returns the track at the specified index.

        .. describe:: x in y

            Checks if a track is in the queue.

        .. describe:: bool(x)

            Checks if the queue is empty.

        .. describe:: hash(x)

            Return the filter's hash.

        .. describe:: str(x)

            Returns a string representation of the queue.

    Note
    ----
        The ``history`` and ``tracks`` attributes give the ORIGINAL OBJECT, you can change them at will.

    Tip
    ---
        You can implement your own track queue and hook it to the player

        .. code-block:: python3

            player = Player.connect_to_channel(voice)
            player.queue = YourQueue()

    Attributes
    ----------
        current : Optional[:class:`harmonize.objects.Track`]
            The currently playing track in the queue.

        tracks : list[:class:`harmonize.objects.Track`]
            The list of tracks currently in the queue.

        history : list[:class:`harmonize.objects.Track`]
            The list of tracks that have been played in the queue.

        loop : :class:`harmonize.enums.LoopStatus`
            The loop status of the queue.

        listened_count : int
            The number of times a track has been played in the queue.
    """

    def __init__(self, player: Player) -> None:
        self._loop: LoopStatus = LoopStatus(0)
        self._history: list[Track] = []
        self._listened_count = 0
        self._now: list[Track | dict[str, PlaylistInfo | list[Track]]] = []
        self._current: Optional[Track] = None
        self._current_playlist: Optional[PlaylistInfo] = None
        self._player: Player = player

    @property
    def current(self) -> Optional[Track]:
        return self._current

    @property
    def history(self) -> list[Track]:
        return self._history

    @property
    def tracks(self) -> list[Track]:
        return self._now

    @property
    def listened_count(self) -> int:
        return self._listened_count

    @property
    def loop(self) -> LoopStatus:
        return self._loop

    def set_loop(self, value: LoopStatus, /) -> None:
        """
        Sets the loop status of the queue.

        Parameters
        ----------
            value : :class:`harmonize.enums.LoopStatus`
                The new loop status to set.

        Raises
        ------
            ValueError
                If the provided value is not an instance of LoopStatus.

        Returns
        -------
            None
        """
        if not isinstance(value, LoopStatus):
            raise ValueError("Invalid loop value. Please provide LoopStatus enum.")
        self._loop = value

    @overload
    def add(self, search: LoadResult, /) -> None:
        ...

    @overload
    def add(self, *, track: Track) -> None:
        ...

    @overload
    def add(self, *, tracks: list[Track]) -> None:
        ...

    def add(self, *args: LoadResult, **kwargs: Track | list[Track]) -> None:
        """
        Adds a track or multiple tracks to the queue.

        Parameters
        ----------
            *args : :class:`harmonize.objects.LoadResult`

                A single :class:`harmonize.objects.LoadResult` object to add to the queue.

            **kwargs : :class:`harmonize.objects.Track` | list[:class:`harmonize.objects.Track`]

                'track' (:class:`harmonize.objects.Track`): A single track to add to the queue.

                'tracks' (list[:class:`harmonize.objects.Track`]): A list of tracks to add to the queue.

        Raises
        ------
            ValueError: If neither 'track' nor 'tracks' is provided in kwargs.

        Returns
        -------
            None
        """
        if load_result := list(args).pop():
            self._now.append({
                "playlist": load_result.playlist_info,
                "tracks": load_result.tracks
            })

        if 'track' in kwargs:
            self._now.append(kwargs.pop("track"))
        elif 'tracks' in kwargs:
            self._now.extend(kwargs.pop("tracks"))
        else:
            raise ValueError("Invalid arguments. Please provide track or tracks.")

    def clear(self) -> None:
        """
        Clears the queue by removing all tracks from the current and history lists.

        Returns
        -------
            None
        """
        self._now.clear()
        self._history.clear()

    def shuffle(self) -> None:
        """
        Shuffles the current queue in-place.

        Returns
        -------
            None
        """
        shuffle(self._now)

    def reverse(self) -> None:
        """
        Reverses the current queue in-place.

        Returns
        -------
            None
        """
        self._now.reverse()

    async def load_next(self, track: Optional[Track] = MISSING) -> Optional[Track]:
        """
        Loads the next track in the queue and updates the current track.

        Parameters
        ----------
            track : Optional[Track
                The next track to load. Defaults to None.

        Returns
        -------
            Optional[Track]
                The previous current track if it was replaced, otherwise None.

        Note
        ----
            - If the loop status is set to TRACK, the current track will be used as the next track if no other track is provided.

            - If the loop status is set to QUEUE, the current track will be added to the end of the queue.

            - If the queue is empty and no next track is provided, the player will stop.
        """
        self._listened_count += 1

        old = self._current
        if self.loop != LoopStatus.OFF and self._current:
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

            if isinstance(self._now[0], dict):
                data: dict[str, PlaylistInfo | list[Track]] = self._now[0].copy()
                if not (tracks := data["tracks"]):
                    self._now.pop(0)
                    if not self._now:
                        await self._player.stop()
                        return self._player.dispatch('queue_end', self._player)
                else:
                    self._current_playlist = data["playlist"]
                    track = tracks.pop(0)
            else:
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

    def __le__(self, other: int | Queue) -> bool:
        if isinstance(other, Queue):
            return len(self) <= len(other)

        return self.__lt__(other) or len(self) == other

    def __lt__(self, other: int | Queue) -> bool:
        if isinstance(other, Queue):
            return len(self) < len(other)

        return len(self) < other

    def __ge__(self, other: int | Queue) -> bool:
        if isinstance(other, Queue):
            return len(self) >= len(other)

        return self.__gt__(other) or len(self) == other

    def __gt__(self, other: int | Queue) -> bool:
        if isinstance(other, Queue):
            return len(self) > len(other)

        return len(self) > other
