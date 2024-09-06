from __future__ import annotations

__all__ = (
    "PlaylistInfo"
)


class PlaylistInfo:
    """
    Represents the information about a playlist.

    Operations
    ----------
        .. describe:: x[key]

            Returns the value of a given attribute of the LoadResult object.

    Attributes
    ----------
        name : str
            The name of the playlist.
        selected_track : int
            The index of the selected track in the playlist. If no track is selected, it defaults to -1.

    """
    def __init__(self, name: str, selected_track: int = -1):
        self.name: str = name
        self.selected_track: int = selected_track

    def __getitem__(self, k: any) -> any:
        if k == 'selectedTrack':
            k = 'selected_track'
        return self.__getattribute__(k)

    @classmethod
    def from_dict(cls, mapping: dict[str, any]) -> PlaylistInfo:
        """
        Creates a new instance of the `PlaylistInfo` class from a dictionary.

        Parameters
        ----------
            mapping : dict[str, any]
                A dictionary containing the playlist information.

        Returns
        -------
            PlaylistInfo
        """
        return cls(mapping['name'], mapping.get('selectedTrack', -1))

    @classmethod
    def none(cls) -> PlaylistInfo:
        """
        Creates a new instance of the `PlaylistInfo` class with default values.

        Returns:
            PlaylistInfo
        """
        return cls('', -1)

    def __repr__(self):
        return (
            f'<harmonize.objects.PlaylistInfo ' +
            (f'name={self.name}, ' if self.name else '') +
            f'selected_track={self.selected_track}>'
        )
