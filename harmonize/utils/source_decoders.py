# Original https://github.com/devoxin/Lavalink.py/blob/development/lavalink/source_decoders.py

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .reader import DataReader


def decode_probe_info(reader: DataReader) -> dict[str, any]:
    probe_info = reader.read_utf().decode()
    return {'probe_info': probe_info}


def decode_lavasrc_fields(reader: DataReader) -> dict[str, any]:
    if reader.remaining <= 8:
        return {}

    album_name = reader.read_nullable_utf()
    album_url = reader.read_nullable_utf()
    artist_url = reader.read_nullable_utf()
    artist_artwork_url = reader.read_nullable_utf()
    preview_url = reader.read_nullable_utf()
    is_preview = reader.read_boolean()

    return {
        'album_name': album_name,
        'album_url': album_url,
        'artist_url': artist_url,
        'artist_artwork_url': artist_artwork_url,
        'preview_url': preview_url,
        'is_preview': is_preview
    }


DEFAULT_DECODER_MAPPING: dict[str, Callable[[DataReader], dict[str, any]]] = {
    'http': decode_probe_info,
    'local': decode_probe_info,
    'deezer': decode_lavasrc_fields,
    'spotify': decode_lavasrc_fields,
    'applemusic': decode_lavasrc_fields,
    'yandexmusic': decode_lavasrc_fields,
    'vkmusic': decode_lavasrc_fields
}