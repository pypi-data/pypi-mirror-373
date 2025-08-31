"""
Binary buffer reading utilities.
"""

import struct
from typing import BinaryIO

from .endian import (
    read_le_int16,
    read_le_int32,
    read_le_uint8,
    read_le_uint16,
    read_le_uint32,
    read_le_uint64,
)

__all__ = [
    "BinaryReader",
]


class BinaryReader:
    """A binary reader that tracks position in a buffer."""

    def __init__(self, data: bytes | memoryview):
        self.data = memoryview(data) if isinstance(data, bytes) else data
        self.position = 0

    def read_uint8(self) -> int:
        value = read_le_uint8(self.data, self.position)
        self.position += 1
        return value

    def read_uint16(self) -> int:
        value = read_le_uint16(self.data, self.position)
        self.position += 2
        return value

    def read_uint32(self) -> int:
        value = read_le_uint32(self.data, self.position)
        self.position += 4
        return value

    def read_uint64(self) -> int:
        value = read_le_uint64(self.data, self.position)
        self.position += 8
        return value

    def read_int16(self) -> int:
        value = read_le_int16(self.data, self.position)
        self.position += 2
        return value

    def read_int32(self) -> int:
        value = read_le_int32(self.data, self.position)
        self.position += 4
        return value

    def read_bytes(self, count: int) -> bytes:
        value = bytes(self.data[self.position : self.position + count])
        self.position += count
        return value

    def read_null_terminated_string(self) -> str:
        start = self.position
        while self.position < len(self.data) and self.data[self.position] != 0:
            self.position += 1

        result = bytes(self.data[start : self.position]).decode("utf-8")
        if self.position < len(self.data):
            self.position += 1
        return result

    def seek(self, position: int) -> None:
        self.position = position

    def skip(self, count: int) -> None:
        self.position += count

    @property
    def remaining(self) -> int:
        return len(self.data) - self.position

    def align(self, boundary: int) -> None:
        remainder = self.position % boundary
        if remainder != 0:
            self.position += boundary - remainder
