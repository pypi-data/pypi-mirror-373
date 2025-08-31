"""
Endianness utilities for reading binary data.
"""

import struct

__all__ = [
    "read_le_uint8",
    "read_le_uint16", 
    "read_le_uint32",
    "read_le_uint64",
    "read_le_int16",
    "read_le_int32",
]


def read_le_uint8(data: bytes | memoryview, offset: int = 0) -> int:
    return struct.unpack_from("<B", data, offset)[0]


def read_le_uint16(data: bytes | memoryview, offset: int = 0) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_le_uint32(data: bytes | memoryview, offset: int = 0) -> int:
    return struct.unpack_from("<L", data, offset)[0]


def read_le_uint64(data: bytes | memoryview, offset: int = 0) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def read_le_int16(data: bytes | memoryview, offset: int = 0) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def read_le_int32(data: bytes | memoryview, offset: int = 0) -> int:
    return struct.unpack_from("<l", data, offset)[0]
