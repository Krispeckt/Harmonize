# Original https://github.com/devoxin/Lavalink.py/blob/development/lavalink/source_decoders.py

import struct
from base64 import b64decode
from io import BytesIO
from typing import Optional

from harmonize.utils.utfm_codec import read_utfm

__all__ = (
    "DataReader",
    "read_utfm"
)


class DataReader:
    def __init__(self, base64_str: str):
        self._buf = BytesIO(b64decode(base64_str))

    @property
    def remaining(self) -> int:
        """ The amount of bytes left to be read. """
        return self._buf.getbuffer().nbytes - self._buf.tell()

    def _read(self, count: int):
        return self._buf.read(count)

    def read_byte(self) -> bytes:
        """
        Reads a single byte from the stream.

        Returns
        -------
        :class:`bytes`
        """
        return self._read(1)

    def read_boolean(self) -> bool:
        """
        Reads a bool from the stream.

        Returns
        -------
        :class:`bool`
        """
        result, = struct.unpack('B', self.read_byte())
        return result != 0

    def read_unsigned_short(self) -> int:
        """
        Reads an unsigned short from the stream.

        Returns
        -------
        :class:`int`
        """
        result, = struct.unpack('>H', self._read(2))
        return result

    def read_int(self) -> int:
        """
        Reads an int from the stream.

        Returns
        -------
        :class:`int`
        """
        result, = struct.unpack('>i', self._read(4))
        return result

    def read_long(self) -> int:
        """
        Reads a long from the stream.

        Returns
        -------
        :class:`int`
        """
        result, = struct.unpack('>Q', self._read(8))
        return result

    def read_nullable_utf(self, utfm: bool = False) -> Optional[str]:
        """
        .. _modified UTF: https://en.wikipedia.org/wiki/UTF-8#Modified_UTF-8

        Reads an optional UTF string from the stream.

        Internally, this just reads a bool and then a string if the bool is ``True``.

        Parameters
        ----------
        utfm: :class:`bool`
            Whether to read the string as `modified UTF`_.

        Returns
        -------
        Optional[:class:`str`]
        """
        exists = self.read_boolean()

        if not exists:
            return None

        return self.read_utfm() if utfm else self.read_utf().decode()

    def read_utf(self) -> bytes:
        """
        Reads a UTF string from the stream.

        Returns
        -------
        :class:`bytes`
        """
        text_length = self.read_unsigned_short()
        return self._read(text_length)

    def read_utfm(self) -> str:
        """
        .. _modified UTF: https://en.wikipedia.org/wiki/UTF-8#Modified_UTF-8

        Reads a UTF string from the stream.

        This method is different to :func:`read_utf` as it accounts for
        different encoding methods utilised by Java's streams, which uses `modified UTF`_
        for character encoding.

        Returns
        -------
        :class:`str`
        """
        text_length = self.read_unsigned_short()
        utf_string = self._read(text_length)
        return read_utfm(text_length, utf_string)
