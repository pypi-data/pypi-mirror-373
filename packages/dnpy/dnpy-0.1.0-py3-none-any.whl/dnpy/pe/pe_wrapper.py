"""
PE wrapper using pefile's _PE abstract class.
"""

from dataclasses import dataclass
from pathlib import Path

import pefile

from ..util.endian import read_le_uint32

__all__ = [
    "NETHeader",
    "DotNetPE",
]


@dataclass(slots=True)
class NETHeader:
    """.NET header structure. (ECMA-335 II.25.3.3)"""

    cb: int
    major_runtime_version: int
    minor_runtime_version: int
    metadata_rva: int
    metadata_size: int
    flags: int
    entry_point_token_or_rva: int
    resources_rva: int
    resources_size: int
    strong_name_signature_rva: int
    strong_name_signature_size: int
    code_manager_table_rva: int
    code_manager_table_size: int
    vtable_fixups_rva: int
    vtable_fixups_size: int
    export_address_table_jumps_rva: int
    export_address_table_jumps_size: int
    managed_native_header_rva: int
    managed_native_header_size: int


class DotNetPE:
    """Wrapper around pefile.PE that adds .NET-specific functionality."""

    def __init__(self, pe: pefile.PE):
        self._pe = pe
        self._net_header: NETHeader | None = None

    @classmethod
    def from_path(cls, path: str | Path):
        """Load a PE file from disk."""
        pe = pefile.PE(str(path))
        return cls(pe)

    @classmethod
    def from_bytes(cls, data: bytes):
        """Load a PE file from bytes."""
        pe = pefile.PE(data=data)
        return cls(pe)

    @property
    def net_header(self) -> NETHeader:
        """Get the .NET header."""
        if self._net_header is None:
            self._net_header = self._parse_net_header()
        return self._net_header

    def _parse_net_header(self) -> NETHeader:
        """Parse the NET header from the PE file."""
        # .NET directory entry
        # (index 14 = IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR)
        net_dir = None
        data_directories = self._pe.OPTIONAL_HEADER.DATA_DIRECTORY

        if len(data_directories) > 14:  # COM+ Runtime Header
            net_dir = data_directories[14]

        if net_dir is None or net_dir.VirtualAddress == 0:
            raise ValueError("Not a .NET assembly - no NET header found")

        # NET header data
        net_data = self._pe.get_data(net_dir.VirtualAddress, net_dir.Size)

        # NET header fields (ECMA-335 II.25.3.3)
        return NETHeader(
            cb=read_le_uint32(net_data, 0),
            major_runtime_version=read_le_uint32(net_data, 4) >> 16,
            minor_runtime_version=read_le_uint32(net_data, 4) & 0xFFFF,
            metadata_rva=read_le_uint32(net_data, 8),
            metadata_size=read_le_uint32(net_data, 12),
            flags=read_le_uint32(net_data, 16),
            entry_point_token_or_rva=read_le_uint32(net_data, 20),
            resources_rva=read_le_uint32(net_data, 24),
            resources_size=read_le_uint32(net_data, 28),
            strong_name_signature_rva=read_le_uint32(net_data, 32),
            strong_name_signature_size=read_le_uint32(net_data, 36),
            code_manager_table_rva=read_le_uint32(net_data, 40),
            code_manager_table_size=read_le_uint32(net_data, 44),
            vtable_fixups_rva=read_le_uint32(net_data, 48),
            vtable_fixups_size=read_le_uint32(net_data, 52),
            export_address_table_jumps_rva=read_le_uint32(net_data, 56),
            export_address_table_jumps_size=read_le_uint32(net_data, 60),
            managed_native_header_rva=(
                read_le_uint32(net_data, 64) if len(net_data) > 64 else 0
            ),
            managed_native_header_size=(
                read_le_uint32(net_data, 68) if len(net_data) > 68 else 0
            ),
        )

    def get_metadata_bytes(self) -> bytes:
        net = self.net_header
        return self._pe.get_data(net.metadata_rva, net.metadata_size)

    def get_offset_from_rva(self, rva: int) -> int | None:
        try:
            return self._pe.get_offset_from_rva(rva)
        except Exception:
            return None

    @property
    def raw_data(self) -> bytes:
        return self._pe.__data__
