__all__ = (
    "PlaylistInfo"
)


class PlaylistInfo:
    def __init__(self, name: str, selected_track: int = -1):
        """
        Initializes a PlaylistInfo object.

        Args:
            name (str): The name of the playlist.
            selected_track (int): The index of the selected track in the playlist. Defaults to -1.

        Returns:
            None
        """
        self.name: str = name
        self.selected_track: int = selected_track

    def __getitem__(self, k: any) -> any:
        """
        Returns the value of a given attribute of the PlaylistInfo object.

        Args:
            k (any): The name of the attribute to retrieve.

        Returns:
            any: The value of the attribute.
        """
        if k == 'selectedTrack':
            k = 'selected_track'
        return self.__getattribute__(k)

    @classmethod
    def from_dict(cls, mapping: dict[str, any]):
        """
        Creates a new instance of the `PlaylistInfo` class from a dictionary.

        Args:
            mapping (dict[str, any]): The dictionary containing the information to create the `PlaylistInfo` object.
                It should have the following keys:
                    - 'name' (str): The name of the playlist.
                    - 'selectedTrack' (int, optional): The index of the selected track in the playlist. Defaults to -1.

        Returns:
            PlaylistInfo: The newly created `PlaylistInfo` object.
        """
        return cls(mapping['name'], mapping.get('selectedTrack', -1))

    @classmethod
    def none(cls):
        """
        Creates a new instance of the `PlaylistInfo` class with default values.

        Returns:
            PlaylistInfo: A new `PlaylistInfo` object with an empty name and a selected track index of -1.
        """
        return cls('', -1)

    def __repr__(self):
        return (
            f'<harmonize.objects.PlaylistInfo ' +
            (f'name={self.name}, ' if self.name else '') +
            f'selected_track={self.selected_track}>'
        )
