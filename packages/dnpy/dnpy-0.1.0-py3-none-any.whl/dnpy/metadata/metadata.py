"""
NET metadata parsing.

Handles metadata root, stream headers, and table heap parsing according to ECMA-335 II.24.
"""

from dataclasses import dataclass

from ..util.buffers import BinaryReader
from .tokens import TokenType

__all__ = [
    "StreamHeader",
    "MetadataRoot",
    "TableInfo",
    "TableHeap",
]


@dataclass(slots=True)
class StreamHeader:
    """Metadata stream header (ECMA-335 II.24.2.2)."""

    offset: int
    size: int
    name: str


@dataclass(slots=True)
class MetadataRoot:
    """Metadata root structure (ECMA-335 II.24.2.1)."""

    signature: int
    major_version: int
    minor_version: int
    reserved: int
    version_length: int
    version: str
    flags: int
    streams: list[StreamHeader]

    @classmethod
    def parse(cls, data: bytes) -> "MetadataRoot":
        """Parse metadata root from bytes."""
        reader = BinaryReader(data)

        signature = reader.read_uint32()
        if signature != 0x424A5342:  # 'BSJB'
            raise ValueError(f"Invalid metadata signature: 0x{signature:08x}")

        major_version = reader.read_uint16()
        minor_version = reader.read_uint16()
        reserved = reader.read_uint32()
        version_length = reader.read_uint32()

        version_bytes = reader.read_bytes(version_length)
        version = version_bytes.rstrip(b"\x00").decode("utf-8")

        reader.align(4)

        flags = reader.read_uint16()
        stream_count = reader.read_uint16()

        # Parse stream headers
        streams = []
        for _ in range(stream_count):
            offset = reader.read_uint32()
            size = reader.read_uint32()

            # Read null-terminated stream name
            name = reader.read_null_terminated_string()
            reader.align(4)
            streams.append(StreamHeader(offset, size, name))

        return cls(
            signature=signature,
            major_version=major_version,
            minor_version=minor_version,
            reserved=reserved,
            version_length=version_length,
            version=version,
            flags=flags,
            streams=streams,
        )


@dataclass(slots=True)
class TableInfo:
    """Information about a metadata table."""

    row_count: int
    row_size: int


class TableHeap:
    """Metadata table heap parser (ECMA-335 II.24.2.6)."""

    def __init__(self, data: bytes):
        self.data = data
        self.reader = BinaryReader(data)

        # Parse table heap header
        self.reserved1 = self.reader.read_uint32()
        self.major_version = self.reader.read_uint8()
        self.minor_version = self.reader.read_uint8()
        self.heap_offset_sizes = self.reader.read_uint8()
        self.reserved2 = self.reader.read_uint8()
        self.valid_mask = self.reader.read_uint64()
        self.sorted_mask = self.reader.read_uint64()

        self.tables: dict[TokenType, TableInfo] = {}
        self._parse_table_info()

        self.table_data_offset = self.reader.position

    def _parse_table_info(self) -> None:
        """Parse row counts for present tables."""
        for table_idx in range(64):  # Maximum 64 tables
            if self.valid_mask & (1 << table_idx):
                try:
                    token_type = TokenType(table_idx)
                    row_count = self.reader.read_uint32()
                    row_size = self._calculate_row_size(token_type)
                    self.tables[token_type] = TableInfo(row_count, row_size)
                except ValueError:
                    # Unknown table type, skip
                    self.reader.read_uint32()

    def _calculate_row_size(self, table: TokenType) -> int:
        """Calculate the size of a row for the given table type."""
        string_idx_size = self.string_index_size
        guid_idx_size = self.guid_index_size
        blob_idx_size = self.blob_index_size

        def table_idx_size(token_type: TokenType) -> int:
            if token_type in self.tables:
                row_count = self.tables[token_type].row_count
                # Use 4 bytes if row count > 65535 (2^16 - 1)
                return 4 if row_count > 0xFFFF else 2
            else:
                return 4 if (string_idx_size == 4 or blob_idx_size == 4) else 2

        def coded_idx_size() -> int:
            max_rows = 0
            for table_type in [
                TokenType.TypeDef,
                TokenType.TypeRef,
                TokenType.MemberRef,
                TokenType.MethodDef,
                TokenType.Field,
                TokenType.ModuleRef,
            ]:
                if table_type in self.tables:
                    max_rows = max(max_rows, self.tables[table_type].row_count)

            if max_rows == 0:
                return 4 if (string_idx_size == 4 or blob_idx_size == 4) else 2

            return 4 if max_rows > 0x3FFF else 2

        if table == TokenType.Module:
            return (
                2
                + string_idx_size
                + guid_idx_size
                + guid_idx_size
                + guid_idx_size
            )
        elif table == TokenType.TypeRef:
            return coded_idx_size() + string_idx_size + string_idx_size
        elif table == TokenType.TypeDef:
            return (
                4
                + string_idx_size
                + string_idx_size
                + coded_idx_size()
                + table_idx_size(TokenType.Field)
                + table_idx_size(TokenType.MethodDef)
            )
        elif table == TokenType.Field:
            return 2 + string_idx_size + blob_idx_size
        elif table == TokenType.MethodDef:
            return (
                4
                + 2
                + 2
                + string_idx_size
                + blob_idx_size
                + table_idx_size(TokenType.Param)
            )
        elif table == TokenType.Param:
            return 2 + 2 + string_idx_size
        elif table == TokenType.InterfaceImpl:
            # InterfaceImpl: Class (TypeDef index) + Interface (TypeDefOrRef coded index)
            return table_idx_size(TokenType.TypeDef) + coded_idx_size()
        elif table == TokenType.MemberRef:
            return coded_idx_size() + string_idx_size + blob_idx_size
        elif table == TokenType.CustomAttribute:
            # CustomAttribute: Parent (coded index) + Type (coded index) + Value (blob index)
            return coded_idx_size() + coded_idx_size() + blob_idx_size
        elif table == TokenType.DeclSecurity:
            # DeclSecurity: Action (2 bytes) + Parent (coded index) + PermissionSet (blob index)
            return 2 + coded_idx_size() + blob_idx_size
        elif table == TokenType.Assembly:
            return (
                4
                + 2
                + 2
                + 2
                + 2
                + 4
                + blob_idx_size
                + string_idx_size
                + string_idx_size
            )
        elif table == TokenType.AssemblyRef:
            return (
                2
                + 2
                + 2
                + 2
                + 4
                + blob_idx_size
                + string_idx_size
                + string_idx_size
                + blob_idx_size
            )
        elif table == TokenType.StandAloneSig:
            # StandAloneSig: Signature (blob index)
            return blob_idx_size
        elif table == TokenType.PropertyMap:
            # PropertyMap: Parent (TypeDef index) + PropertyList (Property index)
            return table_idx_size(TokenType.TypeDef) + table_idx_size(
                TokenType.Property
            )
        elif table == TokenType.Property:
            # Property: Flags (2) + Name (string index) + Type (blob index)
            return 2 + string_idx_size + blob_idx_size
        elif table == TokenType.MethodSemantics:
            # MethodSemantics: Semantics (2) + Method (MethodDef index) + Association (coded index)
            return 2 + table_idx_size(TokenType.MethodDef) + coded_idx_size()
        elif table == TokenType.TypeSpec:
            # TypeSpec: Signature (blob index)
            return blob_idx_size
        elif table == TokenType.ManifestResource:
            # ManifestResource: Offset (4) + Flags (4) + Name (string) + Implementation (coded index)
            return 4 + 4 + string_idx_size + coded_idx_size()
        else:
            return 6

    @property
    def string_index_size(self) -> int:
        """Size of string heap indexes (2 or 4 bytes)."""
        return 4 if (self.heap_offset_sizes & 0x01) else 2

    @property
    def guid_index_size(self) -> int:
        """Size of GUID heap indexes (2 or 4 bytes)."""
        return 4 if (self.heap_offset_sizes & 0x02) else 2

    @property
    def blob_index_size(self) -> int:
        """Size of blob heap indexes (2 or 4 bytes)."""
        return 4 if (self.heap_offset_sizes & 0x04) else 2

    def get_table_row_count(self, table: TokenType) -> int:
        """Get the number of rows in a table."""
        info = self.tables.get(table)
        return info.row_count if info else 0

    def get_table_data(self, table: TokenType, row: int) -> bytes | None:
        """Get raw data for a specific table row (1-based indexing)."""
        if (
            table not in self.tables
            or row == 0
            or row > self.tables[table].row_count
        ):
            return None

        offset = self.table_data_offset

        for table_idx in range(64):
            if table_idx == table.value:
                break
            if self.valid_mask & (1 << table_idx):
                try:
                    tt = TokenType(table_idx)
                    if tt in self.tables:
                        offset += (
                            self.tables[tt].row_count
                            * self.tables[tt].row_size
                        )
                except ValueError:
                    pass

        # Calculate row offset
        info = self.tables[table]
        row_offset = offset + (row - 1) * info.row_size

        return self.data[row_offset : row_offset + info.row_size]
