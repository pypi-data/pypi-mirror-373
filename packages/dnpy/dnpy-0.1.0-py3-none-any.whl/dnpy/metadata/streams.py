"""
Metadata stream parsers.

Handles #Strings, #US (user strings), #Blob, and #GUID heaps (ECMA-335 II.24.2.3-4).
"""

import uuid

from ..util.buffers import BinaryReader

__all__ = [
    "StringsHeap",
    "UserStringHeap",
    "BlobHeap",
    "GuidHeap",
]


class StringsHeap:
    """#Strings heap parser (ECMA-335 II.24.2.3)."""

    def __init__(self, data: bytes):
        self.data = data
        self._cache: dict[int, str] = {}

    def get_string(self, index: int) -> str:
        """Get a string by its heap index."""
        if index == 0:
            return ""  # Null string

        if index in self._cache:
            return self._cache[index]

        if index >= len(self.data):
            raise ValueError(f"String index {index} out of bounds")

        # Find null terminator
        end = index
        while end < len(self.data) and self.data[end] != 0:
            end += 1

        # Decode UTF-8 string
        string_bytes = self.data[index:end]
        result = string_bytes.decode("utf-8")
        self._cache[index] = result
        return result


class UserStringHeap:
    """#US (User String) heap parser (ECMA-335 II.24.2.4)."""

    def __init__(self, data: bytes):
        self.data = data
        self.reader = BinaryReader(data)
        self._cache: dict[int, str] = {}

    def get_string(self, index: int) -> str:
        """Get a user string by its heap index."""
        if index == 0:
            return ""  # Null string

        if index in self._cache:
            return self._cache[index]

        if index >= len(self.data):
            raise ValueError(f"User string index {index} out of bounds")

        # Parse compressed length
        self.reader.seek(index)
        length = self._read_compressed_uint()

        if length == 0:
            result = ""
        else:
            # Read UTF-16 string (subtract 1 for the trailing byte)
            string_length = (length - 1) // 2
            string_bytes = self.reader.read_bytes(string_length * 2)
            result = string_bytes.decode("utf-16le")

            # Skip trailing byte
            self.reader.skip(1)

        self._cache[index] = result
        return result

    def _read_compressed_uint(self) -> int:
        """Read a compressed unsigned integer (ECMA-335 II.24.2.4)."""
        first_byte = self.reader.read_uint8()

        if (first_byte & 0x80) == 0:
            # Single byte: 0xxxxxxx
            return first_byte
        elif (first_byte & 0xC0) == 0x80:
            # Two bytes: 10xxxxxx xxxxxxxx
            second_byte = self.reader.read_uint8()
            return ((first_byte & 0x3F) << 8) | second_byte
        elif (first_byte & 0xE0) == 0xC0:
            # Four bytes: 110xxxxx xxxxxxxx xxxxxxxx xxxxxxxx
            b2 = self.reader.read_uint8()
            b3 = self.reader.read_uint8()
            b4 = self.reader.read_uint8()
            return ((first_byte & 0x1F) << 24) | (b2 << 16) | (b3 << 8) | b4
        else:
            raise ValueError(f"Invalid compressed integer: 0x{first_byte:02x}")


class BlobHeap:
    """#Blob heap parser (ECMA-335 II.24.2.4)."""

    def __init__(self, data: bytes):
        self.data = data
        self.reader = BinaryReader(data)
        self._cache: dict[int, bytes] = {}

    def get_blob(self, index: int) -> bytes:
        """Get a blob by its heap index."""
        if index == 0:
            return b""  # Null blob

        if index in self._cache:
            return self._cache[index]

        if index >= len(self.data):
            raise ValueError(f"Blob index {index} out of bounds")

        # Parse compressed length
        self.reader.seek(index)
        length = self._read_compressed_uint()

        # Read blob data
        blob_data = self.reader.read_bytes(length)
        self._cache[index] = blob_data
        return blob_data

    def _read_compressed_uint(self) -> int:
        """Read a compressed unsigned integer (ECMA-335 II.24.2.4)."""
        first_byte = self.reader.read_uint8()

        if (first_byte & 0x80) == 0:
            # Single byte: 0xxxxxxx
            return first_byte
        elif (first_byte & 0xC0) == 0x80:
            # Two bytes: 10xxxxxx xxxxxxxx
            second_byte = self.reader.read_uint8()
            return ((first_byte & 0x3F) << 8) | second_byte
        elif (first_byte & 0xE0) == 0xC0:
            # Four bytes: 110xxxxx xxxxxxxx xxxxxxxx xxxxxxxx
            b2 = self.reader.read_uint8()
            b3 = self.reader.read_uint8()
            b4 = self.reader.read_uint8()
            return ((first_byte & 0x1F) << 24) | (b2 << 16) | (b3 << 8) | b4
        else:
            raise ValueError(f"Invalid compressed integer: 0x{first_byte:02x}")


class GuidHeap:
    """#GUID heap parser (ECMA-335 II.24.2.5)."""

    def __init__(self, data: bytes):
        self.data = data
        self._cache: dict[int, uuid.UUID] = {}

    def get_guid(self, index: int) -> uuid.UUID | None:
        """Get a GUID by its heap index (1-based)."""
        if index == 0:
            return None  # Null GUID

        if index in self._cache:
            return self._cache[index]

        # GUIDs are stored as 16-byte values, 1-based indexing
        byte_index = (index - 1) * 16
        if byte_index + 16 > len(self.data):
            raise ValueError(f"GUID index {index} out of bounds")

        # Read 16 bytes and create UUID
        guid_bytes = self.data[byte_index : byte_index + 16]
        guid = uuid.UUID(bytes_le=guid_bytes)
        self._cache[index] = guid
        return guid
