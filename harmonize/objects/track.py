from __future__ import annotations

from typing import Union, Optional

from harmonize.abstract.serializable import Serializable
from harmonize.exceptions import InvalidData

__all__ = (
    "Track",
)


class Track(Serializable):
    @classmethod
    def from_dict(cls, mapping: dict) -> Track:
        """
        Create a new instance of the Track class from a dictionary mapping.

        Args:
            mapping (dict): A dictionary containing the mapping data for the Track object.

        Returns:
            Track: A new instance of the Track class initialized with the mapping data.
        """
        return cls(mapping)

    def __init__(
            self,
            data: Union[Track, dict[str, Union[Optional[str], bool, int]]],
            **extra
    ):
        """
        Initializes a new instance of the Track class.

        Args:
            data (Union[Track, dict[str, Union[Optional[str], bool, int]]]): The data used to initialize the Track object.
            **extra: Additional keyword arguments that will be added to the extra dictionary.

        Raises:
            InvalidData: If the data is incomplete and cannot be used to build a Track object.

        Returns:
            None
        """
        if isinstance(data, Track):
            extra = {**data.extra, **extra}  # type: ignore
            data = data.raw

        self.raw_data: dict[str, Union[Optional[str], bool, int]] = data
        info = data.get('info', data)

        try:
            self.encoded: Optional[str] = data.get('encoded')  # type: ignore
            self.identifier: str = info['identifier']  # type: ignore
            self.is_seekable: bool = info['isSeekable']  # type: ignore
            self.author: str = info['author']  # type: ignore
            self.duration: int = info['length']  # type: ignore
            self.is_stream: bool = info['isStream']  # type: ignore
            self.title: str = info['title']  # type: ignore
            self.uri: str = info['uri']  # type: ignore
            self.artwork_url: Optional[str] = info.get('artworkUrl')  # type: ignore
            self.isrc: Optional[str] = info.get('isrc')  # type: ignore
            self.position: int = info.get('position', 0)  # type: ignore
            self.source_name: str = info.get('sourceName', 'unknown')  # type: ignore
            self.plugin_info: Optional[dict[str, any]] = data.get('pluginInfo')  # type: ignore
            self.user_data: Optional[dict[str, any]] = data.get('userData')  # type: ignore
            self.extra: dict[str, any] = extra  # type: ignore
        except KeyError as error:
            raise InvalidData(f'Cannot build a track from partial data! (Missing key: {error.args[0]})') from error

    def __getitem__(self, name: str) -> any:
        return super().__getattribute__(name)

    def __repr__(self) -> str:
        return (
            f'<harmonize.objects.Track '
            f'title={self.title} '
            f'identifier={self.identifier} '
            f'source_name={self.source_name}>'
        )
