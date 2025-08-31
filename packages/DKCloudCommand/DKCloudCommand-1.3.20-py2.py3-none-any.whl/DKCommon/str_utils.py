import logging

from typing import Optional

from chardet import detect as detect_encoding

LOG = logging.getLogger(__name__)


def decode_bytes(value: bytes, encoding: Optional[str] = None) -> str:
    """
    Attempt to decode bytes into a string value.

    Uses chardet to detect encoding. This is in place because there were checks in the old logging system that implied
    that messages could come in as utf-8 signed with a byte order mark - this is also called `utf-8-sig`. Here is the
    problem; suppose you have some bytes that were encoded as `utf-8-sig` and you tried to decode it  as `utf-8`; this
    will NOT raise a UnicodeDecodeError, but that first byte ends up as a weird unprintable unicode character::

        >>> d = "foo".encode("utf-8-sig")
        >>> d.decode("utf-8-sig")
        'foo'
        >>> d.decode("utf-8")
        '\ufefffoo'
        >>>

    For simplicity, we detect the encoding in advance. Low confidence detection values are attempted as utf-8 and
    fallback to the detected encoding in the case of a UnicodeDecodeError.
    """
    if encoding is None:
        detect_info = detect_encoding(value)
        if detect_info["confidence"] == 1.0:
            return value.decode(detect_info["encoding"])
        else:
            # chardet has issue with some simple utf-8 strings, misdetecting as Windows-1252, try
            # decoding as utf-8 since that's likely the safest option anyway. If that fails, fallback
            # to the detected encoding
            try:
                return value.decode("utf-8")
            except UnicodeDecodeError:
                return value.decode(detect_info["encoding"])
    else:
        return value.decode(encoding)
