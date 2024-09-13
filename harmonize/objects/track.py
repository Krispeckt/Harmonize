from __future__ import annotations

import struct
from typing import Union, Optional, Callable

from harmonize.abstract.serializable import Serializable
from harmonize.exceptions import InvalidData
from harmonize.utils import DataReader, DEFAULT_DECODER_MAPPING

__all__ = (
    "Track",
)


class Track(Serializable):
    """
    Represents a track.

    Operations
    ----------
        .. describe:: x[key]

            Returns the value of a given attribute of the LoadResult object.

    Attributes
    ----------
        raw : dict[str, Union[Optional[str], bool, int]]
            Unserialized object track

        encoded : str
            The encoded track data

        identifier : str
            The unique identifier of the track.

        is_seekable : bool
            Indicates whether the track can be seeked or not.

        author : str
            The author of the track.

        duration : int
            The duration of the track in milliseconds.

        is_stream : bool
            Indicates whether the track is a stream or not.

        title : str
            The title of the track.

        uri : str
            The URI of the track.

        artwork_url : Optional[str]
            The URL of the track's artwork.

        isrc: Optional[str]
            The ISRC of the track.

        position : int
            The current position in the track in milliseconds.

        source_name : str
            The name of the source of the track.

        plugin_info : Optional[dict[str, any]]
            Additional plugin information associated with the track, if applicable.

        user_data : Optional[dict[str, any]]
            Additional user data associated with the track, if applicable.
    """

    @classmethod
    def from_dict(cls, mapping: dict) -> Track:
        """
        Create a new instance of the Track class from a dictionary mapping.

        Parameters
        ----------
            mapping : dict
                A dictionary containing the mapping data for the Track object.

        Returns
        -------
            :class:`harmonize.objects.Track`
        """
        return cls(mapping)

    @property
    def raw(self) -> dict[str, Union[Optional[str], bool, int]]:
        return self._raw_data

    def __init__(
            self,
            data: dict[str, Union[Optional[str], bool, int]]
    ) -> None:
        self._raw_data: dict[str, Union[Optional[str], bool, int]] = data
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
        except KeyError as error:
            raise InvalidData(f'Cannot build a track from partial data! (Missing key: {error.args[0]})') from error

    @classmethod
    def from_encode(
            cls: type(Track),
            track: str,
            source_decoders: dict[str, Callable[[DataReader], dict[str, any]]] = None
    ) -> Track:
        """
        Decodes a track from a given string representation.

        Parameters
        -----------
            track : str
                The string representation of the track to be decoded.
            source_decoders : dict[str, Callable[[:class:`harmonize.utils.DataReader`], dict[str, any]]]
                A dictionary mapping source names to their respective decoding functions.
                These functions take a DataReader object as input and return a dictionary
                containing the decoded source-specific fields.
                If not provided, the function will use the default decoders from DEFAULT_DECODER_MAPPING.

        Returns
        --------
            :class:`harmonize.objects.Track`
                An instance of the Track class representing the decoded track.
        """
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

        return cls(track_object)

    def __getitem__(self, name: str) -> any:
        return super().__getattribute__(name)

    def __repr__(self) -> str:
        return (
            f'<harmonize.objects.Track '
            f'title={self.title} '
            f'identifier={self.identifier} '
            f'source_name={self.source_name}>'
        )
