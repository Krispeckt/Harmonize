from __future__ import annotations

import struct
from typing import Union, Optional, Callable

from harmonize.abstract.serializable import Serializable
from harmonize.exceptions import InvalidData

__all__ = (
    "Track",
)

from harmonize.utils.reader import DataReader
from harmonize.utils.source_decoders import DEFAULT_DECODER_MAPPING


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

    @classmethod
    def decode_track(
            cls: type(Track),
            track: str,
            source_decoders: dict[str, Callable[[DataReader], dict[str, any]]] = None
    ) -> Track:
        decoders = DEFAULT_DECODER_MAPPING.copy()

        if source_decoders is not None:
            decoders.update(source_decoders)

        reader = DataReader(track)

        flags = (reader.read_int() & 0xC0000000) >> 30
        version, = struct.unpack('B', reader.read_byte()) if flags & 1 != 0 else (1,)

        title = reader.read_utfm()
        author = reader.read_utfm()
        length = reader.read_long()
        identifier = reader.read_utf().decode()
        is_stream = reader.read_boolean()
        uri = reader.read_nullable_utf()
        extra_fields = {}

        if version == 3:
            extra_fields['artworkUrl'] = reader.read_nullable_utf()
            extra_fields['isrc'] = reader.read_nullable_utf()

        source = reader.read_utf().decode()
        source_specific_fields = {}

        if source in decoders:
            source_specific_fields.update(decoders[source](reader))

        position = reader.read_long()

        track_object = {
            'encoded': track,
            'info': {
                'identifier': identifier,
                'isSeekable': not is_stream,
                'title': title,
                'author': author,
                'length': length,
                'isStream': is_stream,
                'position': position,
                'uri': uri,
                'sourceName': source,
                **extra_fields
            },
            'pluginInfo': source_specific_fields,
            'userData': {}
        }

        return cls(
            track_object,
            position=position,
            encoder_version=version
        )

    def __getitem__(self, name: str) -> any:
        return super().__getattribute__(name)

    def __repr__(self) -> str:
        return (
            f'<harmonize.objects.Track '
            f'title={self.title} '
            f'identifier={self.identifier} '
            f'source_name={self.source_name}>'
        )
