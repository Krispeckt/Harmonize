from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from harmonize.objects import Track


class BaseQueue:
    """
    Base class for a queue that manages a list of tracks.
    """

    def load_next(self, track: Optional[Track]) -> any:
        """
        Loads the next track in the queue.

        Parameters
        ----------
            track : Optional[:class:`harmonize.objects.Track`]
                The next track to load. Defaults to None.

        Returns
        -------
            The next track in the queue, or None if there are no more tracks.
        """
        ...

    @property
    def current(self) -> Track:
        """
        Returns the current track in the queue.

        Returns
        -------
            The current track in the queue, or None if there is no current track.
        """
        return ...
