from typing import Optional, Union

from harmonize.abstract import Serializable
from harmonize.enums import LoadType
from harmonize.objects.playlist_info import PlaylistInfo
from harmonize.objects.track import Track

__all__ = (
    "LoadResult",
    "Track",
    "PlaylistInfo"
)


class _LoadError:
    def __init__(self, error: dict[str, any]) -> None:
        """
        Initializes a new instance of the _LoadError class.

        Args:
            error (dict[str, any]): A dictionary containing error information.
                The dictionary must contain the following keys:
                    - 'message' (str): The error message.
                    - 'severity' (str): The severity of the error.
                    - 'cause' (str): The cause of the error.

        Returns:
            None
        """
        self.message: str = error['message']
        self.severity: str = error['severity']
        self.cause: str = error['cause']


class LoadResult(Serializable):
    __slots__ = ('load_type', 'playlist_info', 'tracks', 'plugin_info', 'error')

    def __init__(
            self,
            load_type: LoadType,
            tracks: list[Track],
            playlist_info: PlaylistInfo = PlaylistInfo.none(),
            plugin_info: Optional[dict[str, any]] = None,
            error: Optional[_LoadError] = None
    ):
        """
        Initializes a new instance of the LoadResult class.

        Args:
            load_type (LoadType): The type of load.
            tracks (list[Track]): A list of tracks.
            playlist_info (PlaylistInfo, optional): The playlist information. Defaults to PlaylistInfo.none().
            plugin_info (Optional[dict[str, any]], optional): The plugin information. Defaults to None.
            error (Optional[_LoadError], optional): The load error. Defaults to None.
        """
        self.load_type: LoadType = load_type
        self.playlist_info: PlaylistInfo = playlist_info
        self.tracks: list[Track] = tracks
        self.plugin_info: Optional[dict[str, any]] = plugin_info
        self.error: Optional[_LoadError] = error

    def __getitem__(self, k):
        """
        Gets the value of a LoadResult attribute by its key.

        Args:
            k (str): The key of the attribute.

        Returns:
            any: The value of the attribute.
        """
        if k == 'loadType':
            k = 'load_type'
        elif k == 'playlistInfo':
            k = 'playlist_info'

        return self.__getattribute__(k)

    @classmethod
    def empty(cls):
        """
        Creates an empty LoadResult instance.

        Returns:
            LoadResult: An empty LoadResult instance with a load type of EMPTY and an empty list of tracks.
        """
        return LoadResult(LoadType.EMPTY, [])

    @classmethod
    def from_dict(cls, mapping: dict):
        """
        Creates a LoadResult instance from a dictionary.

        Args:
            cls: The class itself.
            mapping (dict): A dictionary containing the data to create the LoadResult instance.

        Returns:
            LoadResult: A LoadResult instance created from the dictionary.
        """
        plugin_info: Optional[dict] = None
        playlist_info: Optional[PlaylistInfo] = PlaylistInfo.none()
        tracks: list[Track] = []

        data: Union[list[dict[str, any]], dict[str, any]] = mapping['data']
        load_type = LoadType(mapping['loadType'])

        if isinstance(data, dict):
            plugin_info = data.get('pluginInfo')

        if load_type == LoadType.TRACK:
            tracks = [Track(data)]
        elif load_type == LoadType.PLAYLIST:
            playlist_info = PlaylistInfo.from_dict(data['info'])  # type: ignore
            tracks = [Track(track) for track in data['tracks']]  # type: ignore
        elif load_type == LoadType.SEARCH:
            tracks = [Track(track) for track in data]  # type: ignore
        elif load_type == LoadType.ERROR:
            error = _LoadError(data)  # type: ignore
            return cls(load_type, [], playlist_info, plugin_info, error)

        return cls(load_type, tracks, playlist_info, plugin_info)

    @property
    def selected_track(self) -> Optional[Track]:
        """
        Retrieves the currently selected track from the playlist.

        Returns:
            Optional[Track]: The selected track if it exists, otherwise None.
        """
        if self.playlist_info is not None:
            index = self.playlist_info.selected_track

            if 0 <= index < len(self.tracks):
                return self.tracks[index]

        return None

    def __repr__(self):
        return (
            f'<harmonize.objects.LoadResult '
            f'load_type={self.load_type}, '
            f'playlist_info={self.playlist_info}, '
            f'tracks={len(self.tracks)}>')
