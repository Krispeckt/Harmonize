# Original https://github.com/devoxin/Lavalink.py/blob/development/lavalink/utfm_codec.py

__all__ = (
    "read_utfm",
)


def read_utfm(utf_len: int, utf_bytes: bytes) -> str:
    """
    This function reads a UTF-8 encoded byte stream and decodes it into a string.

    Parameters
    ----------
        utf_len : int
            The length of the UTF-8 encoded byte stream.
        utf_bytes : bytes
            The UTF-8 encoded byte stream to be decoded.

    Returns:
        str
            The decoded string from the UTF-8 encoded byte stream.

    Raises
    ------
        UnicodeDecodeError
            If the input is malformed or incomplete.
    """
    chars = []
    count = 0

    while count < utf_len:
        char = utf_bytes[count] & 0xff
        if char > 127:
            break

        count += 1
        chars.append(chr(char))

    while count < utf_len:
        char = utf_bytes[count] & 0xff
        shift = char >> 4

        if 0 <= shift <= 7:
            count += 1
            chars.append(chr(char))
        elif 12 <= shift <= 13:
            count += 2
            if count > utf_len:
                raise UnicodeDecodeError('utf8', b'', 0, utf_len, 'malformed input: partial character at end')
            char2 = utf_bytes[count - 1]
            if (char2 & 0xC0) != 0x80:
                raise UnicodeDecodeError('utf8', b'', 0, utf_len, f'malformed input around byte {count}')

            char_shift = ((char & 0x1F) << 6) | (char2 & 0x3F)
            chars.append(chr(char_shift))
        elif shift == 14:
            count += 3
            if count > utf_len:
                raise UnicodeDecodeError('utf8', b'', 0, utf_len, 'malformed input: partial character at end')

            char2 = utf_bytes[count - 2]
            char3 = utf_bytes[count - 1]

            if (char2 & 0xC0) != 0x80 or (char3 & 0xC0) != 0x80:
                raise UnicodeDecodeError('utf8', b'', 0, utf_len, f'malformed input around byte {(count - 1)}')

            char_shift = ((char & 0x0F) << 12) | ((char2 & 0x3F) << 6) | ((char3 & 0x3F) << 0)
            chars.append(chr(char_shift))
        else:
            raise UnicodeDecodeError('utf8', b'', 0, utf_len, f'malformed input around byte {count}')

    return ''.join(chars).encode('utf-16', 'surrogatepass').decode('utf-16')
