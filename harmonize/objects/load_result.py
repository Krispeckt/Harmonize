from __future__ import annotations

from typing import Optional, Union

from harmonize.abstract import Serializable
from harmonize.enums import LoadType, Severity
from harmonize.objects.playlist_info import PlaylistInfo
from harmonize.objects.track import Track

__all__ = (
    "LoadResult",
    "Track",
    "PlaylistInfo",
    "LoadError"
)


class LoadError:
    """
    Represents a load error.

    Attributes
    ----------
        message : str
            The error message.
        severity : :class:`harmonize.enums.Severity`
            The severity of the error.
        cause : str
            The cause of the error.

    """

    def __init__(self, error: dict[str, any]) -> None:
        self.message: str = error['message']
        self.severity: Severity = Severity(error['severity'])
        self.cause: str = error['cause']


class LoadResult(Serializable):
    """
    Represents the result of a load operation.

    Operations
    ----------
        .. describe:: x[key]

            Returns the value of a given attribute of the LoadResult object.

    Attributes
    ----------
        load_type : :class:`harmonize.enums.LoadType`
            The type of load operation.
        playlist_info : :class:`harmonize.objects.PlaylistInfo`
            The playlist information. If the load operation is not a playlist, this will be None.
        tracks : list[:class:`harmonize.objects.Track`]
            The decoded Track objects.
        plugin_info : Optional[dict[str, any]]
            Additional plugin information associated with the load operation, if applicable.
        error : Optional[:class:`harmonize.objects.LoadError`]
            The load error, if applicable.
    """

    __slots__ = ('load_type', 'playlist_info', 'tracks', 'plugin_info', 'error')

    def __init__(
            self,
            load_type: LoadType,
            tracks: list[Track],
            playlist_info: PlaylistInfo = PlaylistInfo.none(),
            plugin_info: Optional[dict[str, any]] = None,
            error: Optional[LoadError] = None
    ) -> None:
        self.load_type: LoadType = load_type
        self.playlist_info: PlaylistInfo = playlist_info
        self.tracks: list[Track] = tracks
        self.plugin_info: Optional[dict[str, any]] = plugin_info
        self.error: Optional[LoadError] = error

    def __getitem__(self, k: str) -> any:
        if k == 'loadType':
            k = 'load_type'
        elif k == 'playlistInfo':
            k = 'playlist_info'

        return self.__getattribute__(k)

    @classmethod
    def empty(cls):
        """
        Creates an empty LoadResult instance.

        Returns
        -------
            LoadResult
        """
        return LoadResult(LoadType.EMPTY, [])

    @classmethod
    def from_dict(cls, mapping: dict) -> LoadResult:
        """
        Creates a LoadResult instance from a dictionary.

        Parameters
        ----------
            mapping : dict
                A dictionary containing the data to create the LoadResult instance.

        Returns
        -------
            LoadResult
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
            error = LoadError(data)  # type: ignore
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
