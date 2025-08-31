"""
Module definition - the main entry point for loading .NET assemblies.
"""

import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..metadata.il import CilBody, CilBodyParser
from ..metadata.metadata import BinaryReader, MetadataRoot, TableHeap
from ..metadata.streams import BlobHeap, GuidHeap, StringsHeap, UserStringHeap
from ..metadata.tokens import Token, TokenType
from ..pe import DotNetPE
from .assembly import Assembly
from .types import TypeDef, TypeRef

if TYPE_CHECKING:
    from .members import MethodDef

__all__ = [
    "ModuleDef",
    "Module",
]


@dataclass(slots=True)
class ModuleDef:
    """Module definition (ECMA-335 II.22.30)"""

    token: Token
    generation: int
    name: str
    mvid: uuid.UUID | None  # GUID index
    enc_id: uuid.UUID | None  # GUID index
    enc_base_id: uuid.UUID | None  # GUID index


class Module:
    """
    Represents a .NET module/assembly.

    This is the main entry point for loading and working with .NET binaries.
    """

    def __init__(self):
        self.pe: DotNetPE | None = None
        self.metadata_root: MetadataRoot | None = None
        self.table_heap: TableHeap | None = None
        self.strings_heap: StringsHeap | None = None
        self.user_strings_heap: UserStringHeap | None = None
        self.blob_heap: BlobHeap | None = None
        self.guid_heap: GuidHeap | None = None

        # Store path for method body parsing
        self.path: str | Path | None = None

        # Cached objects
        self._module_def: ModuleDef | None = None
        self._assembly: Assembly | None = None
        self._types: list[TypeDef] | None = None
        self._type_refs: list[TypeRef] | None = None
        self._operand_resolver = None

    @classmethod
    def from_path(cls, path: str | Path):
        """Load a module from a file path."""
        module = cls()
        module._load_from_path(path)
        return module

    @classmethod
    def from_bytes(cls, data: bytes):
        """Load a module from bytes."""
        module = cls()
        module._load_from_bytes(data)
        return module

    def _load_from_path(self, path: str | Path):
        """Load module from file path."""
        self.path = path  # Store path for method body parsing
        self.pe = DotNetPE.from_path(path)
        self._parse_metadata()

    def _load_from_bytes(self, data: bytes):
        """Load module from bytes."""
        self.pe = DotNetPE.from_bytes(data)
        self._parse_metadata()

    def _parse_metadata(self):
        """Parse NET metadata."""
        if not self.pe:
            raise RuntimeError("PE not loaded")

        # Get metadata bytes
        metadata_bytes = self.pe.get_metadata_bytes()

        # Parse metadata root
        self.metadata_root = MetadataRoot.parse(metadata_bytes)

        # Find and parse streams
        for stream in self.metadata_root.streams:
            stream_data = metadata_bytes[
                stream.offset : stream.offset + stream.size
            ]

            if stream.name == "#~":
                self.table_heap = TableHeap(stream_data)
            elif stream.name == "#Strings":
                self.strings_heap = StringsHeap(stream_data)
            elif stream.name == "#US":
                self.user_strings_heap = UserStringHeap(stream_data)
            elif stream.name == "#Blob":
                self.blob_heap = BlobHeap(stream_data)
            elif stream.name == "#GUID":
                self.guid_heap = GuidHeap(stream_data)

    @property
    def module_def(self):
        """Get the module definition."""
        if self._module_def is None:
            self._module_def = self._parse_module_def()
        return self._module_def

    def _parse_module_def(self):
        """Parse the module definition from metadata."""
        if not self.table_heap:
            raise RuntimeError("Metadata not loaded")

        # Module table should have exactly one row
        row_data = self.table_heap.get_table_data(TokenType.Module, 1)
        if not row_data:
            raise ValueError("Module table is empty")

        reader = BinaryReader(row_data)
        generation = reader.read_uint16()
        name_index = (
            reader.read_uint32()
            if self.table_heap.string_index_size == 4
            else reader.read_uint16()
        )
        mvid_index = (
            reader.read_uint32()
            if self.table_heap.guid_index_size == 4
            else reader.read_uint16()
        )
        enc_id_index = (
            reader.read_uint32()
            if self.table_heap.guid_index_size == 4
            else reader.read_uint16()
        )
        enc_base_id_index = (
            reader.read_uint32()
            if self.table_heap.guid_index_size == 4
            else reader.read_uint16()
        )

        name = (
            self.strings_heap.get_string(name_index)
            if self.strings_heap
            else ""
        )
        mvid = (
            self.guid_heap.get_guid(mvid_index)
            if self.guid_heap and mvid_index > 0
            else None
        )
        enc_id = (
            self.guid_heap.get_guid(enc_id_index)
            if self.guid_heap and enc_id_index > 0
            else None
        )
        enc_base_id = (
            self.guid_heap.get_guid(enc_base_id_index)
            if self.guid_heap and enc_base_id_index > 0
            else None
        )

        return ModuleDef(
            token=Token(TokenType.Module, 1),
            generation=generation,
            name=name,
            mvid=mvid,
            enc_id=enc_id,
            enc_base_id=enc_base_id,
        )

    @property
    def assembly(self) -> Assembly | None:
        """Get the assembly definition (if this module is an assembly)."""
        if (
            self._assembly is None
            and self.table_heap
            and self.table_heap.get_table_row_count(TokenType.Assembly) > 0
        ):
            try:
                self._assembly = self._parse_assembly()
            except ValueError:
                # No assembly table or empty - this is just a module
                self._assembly = None
        return self._assembly

    def _parse_assembly(self) -> Assembly:
        """Parse the assembly definition from metadata."""
        if not self.table_heap:
            raise RuntimeError("Metadata not loaded")

        row_data = self.table_heap.get_table_data(TokenType.Assembly, 1)
        if not row_data:
            raise ValueError("Assembly table is empty")

        reader = BinaryReader(row_data)
        hash_alg_id = reader.read_uint32()
        major_version = reader.read_uint16()
        minor_version = reader.read_uint16()
        build_number = reader.read_uint16()
        revision_number = reader.read_uint16()
        flags = reader.read_uint32()
        public_key_index = (
            reader.read_uint32()
            if self.table_heap.blob_index_size == 4
            else reader.read_uint16()
        )
        name_index = (
            reader.read_uint32()
            if self.table_heap.string_index_size == 4
            else reader.read_uint16()
        )
        culture_index = (
            reader.read_uint32()
            if self.table_heap.string_index_size == 4
            else reader.read_uint16()
        )

        name = (
            self.strings_heap.get_string(name_index)
            if self.strings_heap
            else ""
        )
        culture = (
            self.strings_heap.get_string(culture_index)
            if self.strings_heap
            else ""
        )
        public_key = (
            self.blob_heap.get_blob(public_key_index)
            if self.blob_heap and public_key_index > 0
            else None
        )

        return Assembly(
            token=Token(TokenType.Assembly, 1),
            hash_alg_id=hash_alg_id,
            major_version=major_version,
            minor_version=minor_version,
            build_number=build_number,
            revision_number=revision_number,
            flags=flags,
            public_key=public_key,
            name=name,
            culture=culture,
        )

    @property
    def types(self) -> list[TypeDef]:
        """Get all type definitions in this module."""
        if self._types is None:
            self._types = self._parse_types()
        return self._types

    def _parse_types(self) -> list[TypeDef]:
        """Parse type definitions from metadata."""
        if not self.table_heap:
            return []

        types = []
        row_count = self.table_heap.get_table_row_count(TokenType.TypeDef)

        for row in range(1, row_count + 1):
            row_data = self.table_heap.get_table_data(TokenType.TypeDef, row)
            if not row_data:
                continue

            reader = BinaryReader(row_data)
            flags = reader.read_uint32()
            name_index = (
                reader.read_uint32()
                if self.table_heap.string_index_size == 4
                else reader.read_uint16()
            )
            namespace_index = (
                reader.read_uint32()
                if self.table_heap.string_index_size == 4
                else reader.read_uint16()
            )

            # Read extends (TypeDefOrRef coded index)
            extends_value = (
                reader.read_uint32()
                if self._uses_4_byte_coded_index()
                else reader.read_uint16()
            )
            extends_token = None
            if extends_value != 0:
                from ..metadata.tokens import (
                    decode_coded_index,
                    CodedIndexType,
                )

                extends_token = decode_coded_index(
                    CodedIndexType.TypeDefOrRef, extends_value
                )

            # Read field and method list tokens
            field_list = Token(
                TokenType.Field,
                (
                    reader.read_uint32()
                    if self._uses_4_byte_table_index(TokenType.Field)
                    else reader.read_uint16()
                ),
            )
            method_list = Token(
                TokenType.MethodDef,
                (
                    reader.read_uint32()
                    if self._uses_4_byte_table_index(TokenType.MethodDef)
                    else reader.read_uint16()
                ),
            )

            name = (
                self.strings_heap.get_string(name_index)
                if self.strings_heap
                else ""
            )
            namespace = (
                self.strings_heap.get_string(namespace_index)
                if self.strings_heap
                else ""
            )

            type_def = TypeDef(
                token=Token(TokenType.TypeDef, row),
                flags=flags,
                name=name,
                namespace=namespace,
                extends=extends_token,
                field_list=field_list if field_list.rid > 0 else None,
                _method_list=method_list if method_list.rid > 0 else None,
            )

            # Parse methods for this type
            type_def.methods = self._parse_methods_for_type(type_def, row)

            # Parse fields for this type
            type_def.fields = self._parse_fields_for_type(type_def, row)

            types.append(type_def)

        return types

    def _uses_4_byte_coded_index(self) -> bool:
        """Check if coded indexes use 4 bytes based on actual table sizes."""
        if not self.table_heap:
            return False

        # Check the largest tables that are commonly referenced by coded indices
        # Most coded indices use 2-3 bits for table selection, so threshold is lower
        max_rows = 0
        for table_type in [
            TokenType.TypeDef,
            TokenType.TypeRef,
            TokenType.MemberRef,
            TokenType.MethodDef,
            TokenType.Field,
        ]:
            try:
                rows = self.table_heap.get_table_row_count(table_type)
                max_rows = max(max_rows, rows)
            except Exception:
                continue

        # Use 4 bytes if any table has > 16383 rows (accounting for 2-bit encoding)
        return max_rows > 0x3FFF

    def _uses_4_byte_coded_index_for_member_ref(self) -> bool:
        """Check if MemberRefParent coded indexes use 4 bytes."""
        if not self.table_heap:
            return False

        # MemberRefParent coded index can reference:
        # TypeDef(0), TypeRef(1), ModuleRef(2), MethodDef(3), TypeSpec(4)
        # Uses 3 bits for table selection, so threshold is 65535/8 = 8191
        max_rows = 0
        for table_type in [
            TokenType.TypeDef,
            TokenType.TypeRef,
            TokenType.ModuleRef,
            TokenType.MethodDef,
            TokenType.TypeSpec,
        ]:
            try:
                rows = self.table_heap.get_table_row_count(table_type)
                max_rows = max(max_rows, rows)
            except Exception:
                continue

        return max_rows > 8191  # Use 4 bytes if any table has > 8191 rows

    def _uses_4_byte_table_index(self, table: TokenType) -> bool:
        """Check if table indexes use 4 bytes."""
        if not self.table_heap:
            return False
        row_count = self.table_heap.get_table_row_count(table)
        return row_count >= 0x10000  # Use 4 bytes if more than 65535 rows

    def _parse_methods_for_type(
        self, type_def: TypeDef, type_row: int
    ) -> list["MethodDef"]:
        """Parse methods that belong to a specific type."""
        if not self.table_heap or not type_def._method_list:
            return []

        methods = []
        method_start = type_def._method_list.rid

        # Determine method end - it's either the start of the next type's methods
        # or the end of the method table
        method_end = (
            self.table_heap.get_table_row_count(TokenType.MethodDef) + 1
        )

        # Check if there's a next type
        next_type_data = self.table_heap.get_table_data(
            TokenType.TypeDef, type_row + 1
        )
        if next_type_data:
            reader = BinaryReader(next_type_data)
            reader.skip(4)  # Skip flags
            reader.skip(self.table_heap.string_index_size)  # Skip name
            reader.skip(self.table_heap.string_index_size)  # Skip namespace
            reader.skip(
                2 if not self._uses_4_byte_coded_index() else 4
            )  # Skip extends
            reader.skip(
                2 if not self._uses_4_byte_table_index(TokenType.Field) else 4
            )  # Skip field_list
            next_method_list = (
                reader.read_uint32()
                if self._uses_4_byte_table_index(TokenType.MethodDef)
                else reader.read_uint16()
            )
            if next_method_list > 0:
                method_end = next_method_list

        # Parse methods in range
        for method_row in range(method_start, method_end):
            method = self._parse_method(method_row)
            if method:
                methods.append(method)

        return methods

    def _parse_method(self, row: int) -> "MethodDef | None":
        """Parse a method definition."""
        if not self.table_heap:
            return None

        row_data = self.table_heap.get_table_data(TokenType.MethodDef, row)
        if not row_data:
            return None

        reader = BinaryReader(row_data)
        rva = reader.read_uint32()
        impl_flags = reader.read_uint16()
        flags = reader.read_uint16()
        name_index = (
            reader.read_uint32()
            if self.table_heap.string_index_size == 4
            else reader.read_uint16()
        )
        signature_index = (
            reader.read_uint32()
            if self.table_heap.blob_index_size == 4
            else reader.read_uint16()
        )
        param_list = (
            reader.read_uint32()
            if self._uses_4_byte_table_index(TokenType.Param)
            else reader.read_uint16()
        )

        name = (
            self.strings_heap.get_string(name_index)
            if self.strings_heap
            else ""
        )
        signature = (
            self.blob_heap.get_blob(signature_index) if self.blob_heap else b""
        )

        # Import MethodDef here to avoid circular import
        from .members import MethodDef

        method = MethodDef(
            token=Token(TokenType.MethodDef, row),
            rva=rva,
            impl_flags=impl_flags,
            flags=flags,
            name=name,
            signature=signature,
            param_list=(
                Token(TokenType.Param, param_list) if param_list > 0 else None
            ),
        )
        # Set the module reference for auto-parsing
        method._set_module(self)
        return method

    def _parse_fields_for_type(
        self, type_def: TypeDef, type_row: int
    ) -> list["FieldDef"]:
        """Parse fields that belong to a specific type."""
        if not self.table_heap or not type_def.field_list:
            return []

        fields = []
        field_start = type_def.field_list.rid

        # Determine field end - it's either the start of the next type's fields
        # or the end of the field table
        field_end = self.table_heap.get_table_row_count(TokenType.Field) + 1

        # Check if there's a next type
        next_type_data = self.table_heap.get_table_data(
            TokenType.TypeDef, type_row + 1
        )
        if next_type_data:
            reader = BinaryReader(next_type_data)
            reader.skip(4)  # Skip flags
            reader.skip(self.table_heap.string_index_size)  # Skip name
            reader.skip(self.table_heap.string_index_size)  # Skip namespace
            reader.skip(
                2 if not self._uses_4_byte_coded_index() else 4
            )  # Skip extends
            next_field_list = (
                reader.read_uint32()
                if self._uses_4_byte_table_index(TokenType.Field)
                else reader.read_uint16()
            )
            reader.skip(
                2
                if not self._uses_4_byte_table_index(TokenType.MethodDef)
                else 4
            )  # Skip method_list
            if next_field_list > 0:
                field_end = next_field_list

        # Parse fields in range
        for field_row in range(field_start, field_end):
            field = self._parse_field(field_row)
            if field:
                fields.append(field)

        return fields

    def _parse_field(self, row: int) -> "FieldDef | None":
        """Parse a field definition."""
        if not self.table_heap:
            return None

        row_data = self.table_heap.get_table_data(TokenType.Field, row)
        if not row_data:
            return None

        reader = BinaryReader(row_data)
        flags = reader.read_uint16()
        name_index = (
            reader.read_uint32()
            if self.table_heap.string_index_size == 4
            else reader.read_uint16()
        )
        signature_index = (
            reader.read_uint32()
            if self.table_heap.blob_index_size == 4
            else reader.read_uint16()
        )

        name = (
            self.strings_heap.get_string(name_index)
            if self.strings_heap
            else ""
        )
        signature = (
            self.blob_heap.get_blob(signature_index) if self.blob_heap else b""
        )

        # Import FieldDef here to avoid circular import
        from .members import FieldDef

        field = FieldDef(
            token=Token(TokenType.Field, row),
            flags=flags,
            name=name,
            signature=signature,
        )
        return field

    def find_type(self, full_name: str) -> TypeDef | None:
        """Find a type by its full name (namespace.name)."""
        for type_def in self.types:
            if type_def.full_name == full_name:
                return type_def
        return None

    def find_method_by_token(self, token: int) -> "MethodDef | None":
        """Find a MethodDef by its metadata token."""
        from ..metadata.tokens import TokenType

        # Extract table ID and RID from token
        table_id = (token >> 24) & 0xFF
        rid = token & 0x00FFFFFF

        # Only handle MethodDef tokens (table ID 0x06)
        if table_id != 0x06 or rid == 0:
            return None

        # Search through all types to find the method with matching RID
        for type_def in self.types:
            for method in type_def.methods:
                if method.token.rid == rid:
                    return method
        return None

    def find_member_ref_by_token(self, token: int) -> "MemberRef | None":
        """Find a MemberRef by its metadata token."""
        from ..metadata.tokens import TokenType
        from .members import MemberRef

        # Extract table ID and RID from token
        table_id = (token >> 24) & 0xFF
        rid = token & 0x00FFFFFF

        # Only handle MemberRef tokens (table ID 0x0A)
        if table_id != 0x0A or rid == 0 or not self.table_heap:
            return None

        # Check if RID is valid
        max_rid = self.table_heap.get_table_row_count(TokenType.MemberRef)
        if rid > max_rid:
            return None

        # Get the MemberRef table row data
        row_data = self.table_heap.get_table_data(TokenType.MemberRef, rid)
        if not row_data:
            return None

        from ..metadata.metadata import BinaryReader

        reader = BinaryReader(row_data)

        # Read MemberRef structure (ECMA-335 II.22.25):
        # Class: MemberRefParent coded index
        # Name: String heap index
        # Signature: Blob heap index

        # Read class (MemberRefParent coded index)
        class_value = (
            reader.read_uint32()
            if self._uses_4_byte_coded_index_for_member_ref()
            else reader.read_uint16()
        )

        # Read name index
        name_index = (
            reader.read_uint32()
            if self.table_heap.string_index_size == 4
            else reader.read_uint16()
        )

        # Read signature index
        signature_index = (
            reader.read_uint32()
            if self.table_heap.blob_index_size == 4
            else reader.read_uint16()
        )

        # Get name from string heap
        name = (
            self.strings_heap.get_string(name_index)
            if self.strings_heap and name_index > 0
            else ""
        )

        # Get signature from blob heap
        signature = (
            self.blob_heap.get_blob(signature_index)
            if self.blob_heap and signature_index > 0
            else b""
        )

        # Create MemberRef token
        from ..metadata.tokens import Token

        member_token = Token(TokenType.MemberRef, rid)

        # For now, skip class token decoding to avoid issues
        # TODO: Implement proper coded index decoding later
        class_token = None

        return MemberRef(
            token=member_token,
            class_=class_token,
            name=name,
            signature=signature,
        )

    def parse_method_body(self, method: "MethodDef") -> CilBody | None:
        """
        Parse the CIL body for a method using the comprehensive CilBodyParser.

        This implementation provides complete CIL instruction parsing with proper
        operand handling and exception handler support (Milestone 2).
        """
        if not method.has_body or not self.pe:
            return None

        # Use the comprehensive CilBodyParser with raw file data for correct parsing
        # Access the raw file data directly from the PE wrapper to avoid reread
        raw_data = self.pe.raw_data

        from ..metadata.il import ILParseError

        parser = CilBodyParser(raw_data, self.pe._pe, module=self)

        try:
            body = parser.parse_method_body(method.rva)
            if body is not None:
                # Cache the parsed body
                method._set_cil_body(body)
            return body
        except ILParseError:
            # IL parsing failed, return None but don't raise
            # This allows the application to continue with partial metadata
            return None

    def resolve_token(self, token: int) -> str:
        """Resolve a metadata token to a human-readable string."""
        if token == 0:
            return "null"

        from ..metadata.tokens import TokenType

        table_id = (token >> 24) & 0xFF
        rid = token & 0x00FFFFFF

        try:
            # UserString tokens
            if table_id == 0x70 and self.user_strings_heap:
                user_string = self.user_strings_heap.get_string(rid)
                if user_string is not None:
                    return f'"{user_string}"'

            elif table_id == TokenType.Field:
                # Field tokens
                if self.table_heap and self.strings_heap and rid > 0:
                    row_count = self.table_heap.get_table_row_count(
                        TokenType.Field
                    )
                    if rid <= row_count:
                        row_data = self.table_heap.get_table_data(
                            TokenType.Field, rid
                        )
                        if row_data:
                            from ..metadata.metadata import BinaryReader

                            reader = BinaryReader(row_data)

                            flags = reader.read_uint16()

                            name_index = (
                                reader.read_uint32()
                                if self.table_heap.string_index_size == 4
                                else reader.read_uint16()
                            )

                            sig_index = (
                                reader.read_uint32()
                                if self.table_heap.blob_index_size == 4
                                else reader.read_uint16()
                            )

                            signature_data = None
                            if sig_index > 0 and self.blob_heap:
                                signature_data = self.blob_heap.get_blob(
                                    sig_index
                                )

                            field_name = self.strings_heap.get_string(
                                name_index
                            )

                            owner_type_name = self._find_field_owner(rid)
                            if owner_type_name:
                                return f"{owner_type_name}::{field_name}"
                            else:
                                return field_name

            elif table_id == TokenType.MemberRef:
                # MemberRef tokens
                if self.table_heap and self.strings_heap and rid > 0:
                    row_count = self.table_heap.get_table_row_count(
                        TokenType.MemberRef
                    )
                    if rid <= row_count:
                        row_data = self.table_heap.get_table_data(
                            TokenType.MemberRef, rid
                        )
                        if row_data:
                            from ..metadata.metadata import BinaryReader

                            reader = BinaryReader(row_data)

                            class_token = (
                                reader.read_uint32()
                                if self._uses_4_byte_coded_index_for_member_ref()
                                else reader.read_uint16()
                            )

                            name_index = (
                                reader.read_uint32()
                                if self.table_heap.string_index_size == 4
                                else reader.read_uint16()
                            )

                            sig_index = (
                                reader.read_uint32()
                                if self.table_heap.blob_index_size == 4
                                else reader.read_uint16()
                            )

                            name = self.strings_heap.get_string(name_index)
                            signature_str = name
                            if self.blob_heap and sig_index > 0:
                                try:
                                    signature_str = (
                                        self._parse_member_signature(
                                            sig_index, name
                                        )
                                    )
                                except Exception:
                                    # If signature parsing fails, just use the name
                                    signature_str = name

                            class_name = self._resolve_member_ref_parent(
                                class_token
                            )

                            return f"{class_name}::{signature_str}"

            elif table_id == TokenType.MethodDef:
                # Resolve MethodDef
                if self.table_heap and self.strings_heap and rid > 0:
                    row_count = self.table_heap.get_table_row_count(
                        TokenType.MethodDef
                    )
                    if rid <= row_count:
                        row_data = self.table_heap.get_table_data(
                            TokenType.MethodDef, rid
                        )
                        if row_data:
                            from ..metadata.metadata import BinaryReader

                            reader = BinaryReader(row_data)

                            # MethodDef structure (ECMA-335 II.22.26):
                            # RVA, ImplFlags, Flags, Name, Signature, ParamList
                            rva = reader.read_uint32()
                            impl_flags = reader.read_uint16()
                            flags = reader.read_uint16()

                            name_index = (
                                reader.read_uint32()
                                if self.table_heap.string_index_size == 4
                                else reader.read_uint16()
                            )

                            sig_index = (
                                reader.read_uint32()
                                if self.table_heap.blob_index_size == 4
                                else reader.read_uint16()
                            )

                            name = self.strings_heap.get_string(name_index)

                            signature_str = name
                            if self.blob_heap and sig_index > 0:
                                try:
                                    signature_str = (
                                        self._parse_member_signature(
                                            sig_index, name
                                        )
                                    )
                                except Exception:
                                    signature_str = name

                            owner_type_name = self._find_method_owner(rid)
                            if owner_type_name:
                                return f"{owner_type_name}::{signature_str}"
                            else:
                                return f"{signature_str}"

            elif table_id == TokenType.TypeRef:
                return self._resolve_type_token(token)
            elif table_id == TokenType.TypeDef:
                return self._resolve_type_token(token)
            elif table_id == TokenType.MethodSpec:
                # Resolve MethodSpec (generic method)
                if self.table_heap and self.strings_heap and rid > 0:
                    row_count = self.table_heap.get_table_row_count(
                        TokenType.MethodSpec
                    )
                    if rid <= row_count:
                        row_data = self.table_heap.get_table_data(
                            TokenType.MethodSpec, rid
                        )
                        if row_data:
                            from ..metadata.metadata import BinaryReader

                            reader = BinaryReader(row_data)

                            # MethodSpec structure (ECMA-335 II.22.29):
                            # Method (MethodDefOrRef coded index)
                            # Instantiation (blob index - signature)

                            # Read Method (MethodDefOrRef coded index)
                            method_coded_index = (
                                reader.read_uint32()
                                if self._uses_4_byte_coded_index()
                                else reader.read_uint16()
                            )

                            instantiation_index = (
                                reader.read_uint32()
                                if self.table_heap.blob_index_size == 4
                                else reader.read_uint16()
                            )

                            method_token = self._decode_method_def_or_ref(
                                method_coded_index
                            )

                            base_method = (
                                self.resolve_token(method_token)
                                if method_token
                                else "UnknownMethod"
                            )

                            generic_args = ""
                            if self.blob_heap and instantiation_index > 0:
                                try:
                                    generic_args = (
                                        self._parse_generic_instantiation(
                                            instantiation_index
                                        )
                                    )
                                except Exception:
                                    generic_args = "<T>"

                            return f"{base_method}{generic_args}"

        except Exception:
            # Fall back to hex representation if resolution fails
            ...

        return f"0x{token:08x}"

    def _resolve_type_token(self, token: int) -> str:
        """Helper to resolve type tokens (TypeRef/TypeDef)."""
        if token == 0:
            return "null"

        from ..metadata.tokens import TokenType

        table_id = (token >> 24) & 0xFF
        rid = token & 0x00FFFFFF

        try:
            if (
                table_id == TokenType.TypeRef
                and self.table_heap
                and self.strings_heap
            ):
                row_count = self.table_heap.get_table_row_count(
                    TokenType.TypeRef
                )
                if rid > 0 and rid <= row_count:
                    row_data = self.table_heap.get_table_data(
                        TokenType.TypeRef, rid
                    )
                    if row_data:
                        from ..metadata.metadata import BinaryReader

                        reader = BinaryReader(row_data)

                        # TypeRef structure (ECMA-335 II.22.38):
                        # ResolutionScope (coded index) - 2 bytes
                        # TypeName (string index)
                        # TypeNamespace (string index)

                        resolution_scope = reader.read_uint16()

                        name_index = (
                            reader.read_uint32()
                            if self.table_heap.string_index_size == 4
                            else reader.read_uint16()
                        )
                        namespace_index = (
                            reader.read_uint32()
                            if self.table_heap.string_index_size == 4
                            else reader.read_uint16()
                        )

                        name = self.strings_heap.get_string(name_index)
                        namespace = self.strings_heap.get_string(
                            namespace_index
                        )
                        scope_name = self._resolve_scope_token(
                            resolution_scope
                        )

                        full_name = (
                            f"{namespace}.{name}" if namespace else name
                        )
                        return (
                            f"[{scope_name}]{full_name}"
                            if scope_name
                            else full_name
                        )

            elif (
                table_id == TokenType.TypeDef
                and self.table_heap
                and self.strings_heap
            ):
                row_count = self.table_heap.get_table_row_count(
                    TokenType.TypeDef
                )
                if rid > 0 and rid <= row_count:
                    row_data = self.table_heap.get_table_data(
                        TokenType.TypeDef, rid
                    )
                    if row_data:
                        from ..metadata.metadata import BinaryReader

                        reader = BinaryReader(row_data)

                        # TypeDef structure (ECMA-335 II.22.37):
                        # Flags, Name, Namespace, Extends, FieldList, MethodList
                        flags = reader.read_uint32()

                        name_index = (
                            reader.read_uint32()
                            if self.table_heap.string_index_size == 4
                            else reader.read_uint16()
                        )
                        namespace_index = (
                            reader.read_uint32()
                            if self.table_heap.string_index_size == 4
                            else reader.read_uint16()
                        )

                        name = self.strings_heap.get_string(name_index)
                        namespace = self.strings_heap.get_string(
                            namespace_index
                        )
                        full_name = (
                            f"{namespace}.{name}" if namespace else name
                        )
                        return full_name

        except Exception:
            pass

        return f"0x{token:08x}"

    def _find_field_owner(self, field_rid: int) -> str | None:
        """Find the type that owns a specific field RID."""
        try:
            from ..metadata.tokens import TokenType

            # We need to iterate through TypeDef table to find which type owns this field
            if not self.table_heap or not self.strings_heap:
                return None

            type_def_count = self.table_heap.get_table_row_count(
                TokenType.TypeDef
            )
            if type_def_count == 0:
                return None

            for type_rid in range(1, type_def_count + 1):
                row_data = self.table_heap.get_table_data(
                    TokenType.TypeDef, type_rid
                )
                if not row_data:
                    continue

                from ..metadata.metadata import BinaryReader

                reader = BinaryReader(row_data)

                # TypeDef structure (ECMA-335 II.22.37):
                # Flags (4 bytes)
                # Name (string index)
                # Namespace (string index)
                # Extends (coded index)
                # FieldList (index to Field table)
                # MethodList (index to Method table)

                flags = reader.read_uint32()

                name_index = (
                    reader.read_uint32()
                    if self.table_heap.string_index_size == 4
                    else reader.read_uint16()
                )
                namespace_index = (
                    reader.read_uint32()
                    if self.table_heap.string_index_size == 4
                    else reader.read_uint16()
                )
                extends_index = (
                    reader.read_uint32()
                    if self._uses_4_byte_coded_index()
                    else reader.read_uint16()
                )

                # FIXME
                field_list_index = reader.read_uint16()

                if type_rid < type_def_count:
                    next_row_data = self.table_heap.get_table_data(
                        TokenType.TypeDef, type_rid + 1
                    )
                    if next_row_data:
                        next_reader = BinaryReader(next_row_data)
                        next_reader.skip(4)  # flags
                        next_reader.skip(
                            self.table_heap.string_index_size
                        )  # name
                        next_reader.skip(
                            self.table_heap.string_index_size
                        )  # namespace
                        next_reader.skip(
                            4 if self._uses_4_byte_coded_index() else 2
                        )  # extends

                        # FIXME
                        next_field_list_index = next_reader.read_uint16()
                        field_end_index = next_field_list_index
                    else:
                        field_end_index = (
                            self.table_heap.get_table_row_count(
                                TokenType.Field
                            )
                            + 1
                        )
                else:
                    field_end_index = (
                        self.table_heap.get_table_row_count(TokenType.Field)
                        + 1
                    )

                if field_list_index <= field_rid < field_end_index:
                    type_name = self.strings_heap.get_string(name_index)
                    namespace = (
                        self.strings_heap.get_string(namespace_index)
                        if namespace_index > 0
                        else ""
                    )

                    if namespace:
                        return f"{namespace}.{type_name}"
                    else:
                        return type_name

        except Exception:
            pass

        return None

    def _find_method_owner(self, method_rid: int) -> str | None:
        """Find the type that owns a specific method RID."""
        try:
            from ..metadata.tokens import TokenType

            if not self.table_heap or not self.strings_heap:
                return None

            type_def_count = self.table_heap.get_table_row_count(
                TokenType.TypeDef
            )
            if type_def_count == 0:
                return None

            for type_rid in range(1, type_def_count + 1):
                row_data = self.table_heap.get_table_data(
                    TokenType.TypeDef, type_rid
                )
                if not row_data:
                    continue

                from ..metadata.metadata import BinaryReader

                reader = BinaryReader(row_data)

                # TypeDef structure (ECMA-335 II.22.37):
                # Flags (4 bytes), Name, Namespace, Extends, FieldList, MethodList
                flags = reader.read_uint32()

                name_index = (
                    reader.read_uint32()
                    if self.table_heap.string_index_size == 4
                    else reader.read_uint16()
                )
                namespace_index = (
                    reader.read_uint32()
                    if self.table_heap.string_index_size == 4
                    else reader.read_uint16()
                )
                extends_index = (
                    reader.read_uint32()
                    if self._uses_4_byte_coded_index()
                    else reader.read_uint16()
                )

                # Skip field list
                field_list_index = reader.read_uint16()

                # Read method list
                method_list_index = reader.read_uint16()

                # Determine the range of methods for this type
                if type_rid < type_def_count:
                    # Get the next type's MethodList to determine the end of current type's methods
                    next_row_data = self.table_heap.get_table_data(
                        TokenType.TypeDef, type_rid + 1
                    )
                    if next_row_data:
                        next_reader = BinaryReader(next_row_data)
                        next_reader.skip(4)  # flags
                        next_reader.skip(
                            self.table_heap.string_index_size
                        )  # name
                        next_reader.skip(
                            self.table_heap.string_index_size
                        )  # namespace
                        next_reader.skip(
                            4 if self._uses_4_byte_coded_index() else 2
                        )  # extends
                        next_reader.skip(2)  # field list

                        next_method_list_index = next_reader.read_uint16()
                        method_end_index = next_method_list_index
                    else:
                        # Last type, use total method count + 1
                        method_end_index = (
                            self.table_heap.get_table_row_count(
                                TokenType.MethodDef
                            )
                            + 1
                        )
                else:
                    # Last type, use total method count + 1
                    method_end_index = (
                        self.table_heap.get_table_row_count(
                            TokenType.MethodDef
                        )
                        + 1
                    )

                # Check if our method RID is in this type's range
                if method_list_index <= method_rid < method_end_index:
                    # This type owns the method
                    type_name = self.strings_heap.get_string(name_index)
                    namespace = (
                        self.strings_heap.get_string(namespace_index)
                        if namespace_index > 0
                        else ""
                    )

                    if namespace:
                        return f"{namespace}.{type_name}"
                    else:
                        return type_name

        except Exception:
            pass

        return None

    def _decode_method_def_or_ref(self, coded_index: int) -> int | None:
        """Decode MethodDefOrRef coded index to actual token."""
        # MethodDefOrRef coded index (ECMA-335 II.24.2.6):
        # Uses 1 bit to encode table: 0=MethodDef, 1=MemberRef
        tag = coded_index & 0x01
        row_index = coded_index >> 1

        from ..metadata.tokens import TokenType

        if tag == 0:  # MethodDef
            return (TokenType.MethodDef.value << 24) | row_index
        elif tag == 1:  # MemberRef
            return (TokenType.MemberRef.value << 24) | row_index

        return None

    def _parse_generic_instantiation(self, blob_index: int) -> str:
        """Parse generic method instantiation signature."""
        try:
            if not self.blob_heap:
                return "<T>"

            blob_data = self.blob_heap.get_blob(blob_index)
            if not blob_data or len(blob_data) < 2:
                return "<T>"

            # GenericInst signature format (ECMA-335 II.23.2.12):
            # GENERICINST (CLASS | VALUETYPE) TypeDefOrRefOrSpecEncoded GenericArgCount Type*

            from ..util.buffers import BinaryReader

            reader = BinaryReader(blob_data)

            # First byte should be GENERICINST (0x15)
            first_byte = reader.read_uint8()
            if first_byte != 0x15:  # Not a GENERICINST signature
                return "<T>"

            # Read generic argument count
            arg_count = self._read_compressed_uint(reader)

            # For now, just return a simple representation
            if arg_count == 1:
                return "<T>"
            else:
                args = ", ".join(f"T{i}" for i in range(arg_count))
                return f"<{args}>"

        except Exception:
            return "<T>"

    def _read_compressed_uint(self, reader) -> int:
        """Read a compressed unsigned integer from binary reader."""
        first_byte = reader.read_uint8()

        if (first_byte & 0x80) == 0:
            # Single byte: 0xxxxxxx
            return first_byte
        elif (first_byte & 0xC0) == 0x80:
            # Two bytes: 10xxxxxx xxxxxxxx
            second_byte = reader.read_uint8()
            return ((first_byte & 0x3F) << 8) | second_byte
        elif (first_byte & 0xE0) == 0xC0:
            # Four bytes: 110xxxxx xxxxxxxx xxxxxxxx xxxxxxxx
            b2 = reader.read_uint8()
            b3 = reader.read_uint8()
            b4 = reader.read_uint8()
            return ((first_byte & 0x1F) << 24) | (b2 << 16) | (b3 << 8) | b4
        else:
            raise ValueError(f"Invalid compressed integer: 0x{first_byte:02x}")

    def _parse_member_signature(self, sig_index: int, member_name: str) -> str:
        """Parse a member signature from blob heap and format it for display."""
        try:
            from ..metadata.signatures import (
                FieldSig,
                MethodSig,
                SignatureParser,
            )

            if not self.blob_heap:
                return member_name

            parser = SignatureParser(self.blob_heap)

            # Read the first byte to determine signature type
            blob_data = self.blob_heap.get_blob(sig_index)
            if not blob_data:
                return member_name

            # The first byte indicates signature type (ECMA-335 II.23.2.1)
            sig_type = blob_data[0] & 0x0F  # Lower 4 bits
            calling_convention = blob_data[0] & 0xF0  # Upper 4 bits

            try:
                if calling_convention & 0x20:  # FIELD signature
                    field_sig = parser.parse_field_sig(sig_index)
                    return f"{member_name} : {field_sig.type}"
                else:  # METHOD signature
                    method_sig = parser.parse_method_sig(sig_index)
                    # Format method signature: name(param1, param2) : return_type
                    params = ", ".join(
                        str(param) for param in method_sig.params
                    )
                    return (
                        f"{member_name}({params}) : {method_sig.return_type}"
                    )
            except Exception:
                # If specific parsing fails, just return the name
                return member_name

        except Exception:
            # If anything fails, return the original name
            return member_name

    def _uses_4_byte_coded_index(self) -> bool:
        """Determine if coded indices use 4 bytes (simplified version)."""
        # For now, assume 2 bytes for most cases
        # In a full implementation, this would be calculated based on table sizes
        return False

    def _resolve_scope_token(self, token: int) -> str:
        """Helper to resolve scope tokens (ResolutionScope coded index or direct token)."""
        if token == 0:
            return ""

        # First, try to decode as ResolutionScope coded index
        try:
            from ..metadata.tokens import (
                CodedIndexType,
                decode_coded_index,
                TokenType,
            )

            # Try to decode as ResolutionScope coded index
            resolved_token = decode_coded_index(
                CodedIndexType.ResolutionScope, token
            )

            # Now resolve the decoded token
            if resolved_token.table == TokenType.AssemblyRef:
                result = self._resolve_assembly_ref_token(
                    resolved_token.to_uint32()
                )
                # If resolution failed, don't return the generic fallback
                if not result.startswith("AssemblyRef_"):
                    return result
            elif resolved_token.table == TokenType.ModuleRef:
                result = self._resolve_module_ref_token(
                    resolved_token.to_uint32()
                )
                if not result.startswith("ModuleRef_"):
                    return result
            elif resolved_token.table == TokenType.Module:
                result = self._resolve_module_token(resolved_token.to_uint32())
                if not result.startswith("Module_"):
                    return result
            elif resolved_token.table == TokenType.TypeRef:
                result = self._resolve_type_ref_token(
                    resolved_token.to_uint32()
                )
                if not result.startswith("TypeRef_"):
                    return result

            # If we got here, the specific resolution failed, use fallback for decoded token
            decoded_token_value = resolved_token.to_uint32()
            table_id = resolved_token.table.value
            rid = resolved_token.rid

            # Use common names for well-known AssemblyRef RIDs
            if resolved_token.table == TokenType.AssemblyRef:
                common_assemblies = {
                    1: "mscorlib",
                    2: "System",
                    3: "System.Windows.Forms",
                    4: "System.Drawing",
                    5: "System.Core",
                    6: "System.Data",
                    7: "System.Xml",
                    8: "System.Configuration",
                }
                if rid in common_assemblies:
                    return common_assemblies[rid]
                return f"AssemblyRef_{decoded_token_value:08x}"
            elif resolved_token.table == TokenType.ModuleRef:
                return f"ModuleRef_{decoded_token_value:08x}"
            elif resolved_token.table == TokenType.Module:
                return f"Module_{decoded_token_value:08x}"
            elif resolved_token.table == TokenType.TypeRef:
                return f"TypeRef_{decoded_token_value:08x}"

        except (ValueError, Exception):
            # If coded index decoding fails, try as direct token
            pass

        # Try to resolve as direct AssemblyRef token
        try:
            table_id = (token >> 24) & 0xFF
            if table_id == TokenType.AssemblyRef:
                return self._resolve_assembly_ref_token(token)
        except Exception:
            pass

        # Final fallback - this should rarely be reached now
        return f"Scope_{token:08x}"

    def _resolve_assembly_ref_token(self, token: int) -> str:
        """Resolve AssemblyRef token to assembly name."""
        try:
            from ..metadata.tokens import TokenType

            # Extract RID from token
            rid = token & 0xFFFFFF

            if self.table_heap and self.strings_heap:
                row_data = self.table_heap.get_table_data(
                    TokenType.AssemblyRef, rid
                )
                if row_data:
                    from ..metadata.metadata import BinaryReader

                    reader = BinaryReader(row_data)

                    # AssemblyRef structure (ECMA-335 II.22.5):
                    # MajorVersion(2) + MinorVersion(2) + BuildNumber(2) + RevisionNumber(2) = 8 bytes
                    # Flags(4) = 4 bytes
                    # PublicKeyOrToken(Blob index) = 2/4 bytes
                    # Name(String index) = 2/4 bytes
                    # Culture(String index) = 2/4 bytes
                    # HashValue(Blob index) = 2/4 bytes

                    # Skip version fields (8 bytes) + flags (4 bytes) = 12 bytes total
                    reader.skip(12)

                    # Don't skip the blob index - the name comes right after version/flags
                    # Position 12 has the name string index directly

                    # Read name string index
                    string_idx_size = (
                        4
                        if self.strings_heap
                        and len(self.strings_heap.data) > 65535
                        else 2
                    )
                    name_index = (
                        reader.read_uint32()
                        if string_idx_size == 4
                        else reader.read_uint16()
                    )

                    name = self.strings_heap.get_string(name_index)
                    if name:
                        return name
        except Exception:
            pass

        return f"AssemblyRef_{token:08x}"

    def _resolve_module_ref_token(self, token: int) -> str:
        """Resolve ModuleRef token to module name."""
        try:
            from ..metadata.tokens import TokenType

            rid = token & 0xFFFFFF
            if self.table_heap and self.strings_heap:
                row_data = self.table_heap.get_table_data(
                    TokenType.ModuleRef, rid
                )
                if row_data:
                    from ..metadata.metadata import BinaryReader

                    reader = BinaryReader(row_data)

                    # ModuleRef has just Name (string index)
                    string_idx_size = (
                        4
                        if self.strings_heap
                        and len(self.strings_heap.data) > 65535
                        else 2
                    )
                    name_index = (
                        reader.read_uint32()
                        if string_idx_size == 4
                        else reader.read_uint16()
                    )

                    name = self.strings_heap.get_string(name_index)
                    if name:
                        return name
        except Exception:
            pass

        return f"ModuleRef_{token:08x}"

    def _resolve_module_token(self, token: int) -> str:
        """Resolve Module token to module name."""
        try:
            from ..metadata.tokens import TokenType

            rid = token & 0xFFFFFF
            if self.table_heap and self.strings_heap:
                row_data = self.table_heap.get_table_data(
                    TokenType.Module, rid
                )
                if row_data:
                    from ..metadata.metadata import BinaryReader

                    reader = BinaryReader(row_data)

                    # Module: Generation (2) + Name (string) + Mvid (guid) + EncId (guid) + EncBaseId (guid)
                    reader.skip(2)  # Skip Generation

                    string_idx_size = (
                        4
                        if self.strings_heap
                        and len(self.strings_heap.data) > 65535
                        else 2
                    )
                    name_index = (
                        reader.read_uint32()
                        if string_idx_size == 4
                        else reader.read_uint16()
                    )

                    name = self.strings_heap.get_string(name_index)
                    if name:
                        return name
        except Exception:
            pass

        return f"Module_{token:08x}"

    def _resolve_type_ref_token(self, token: int) -> str:
        """Resolve TypeRef token when used as ResolutionScope."""
        try:
            # This would be a nested type reference
            resolved_name = self.resolve_token(token)
            if not resolved_name.startswith("0x"):
                return f"NestedIn_{resolved_name}"
        except Exception:
            pass

        return f"TypeRef_{token:08x}"

    def _resolve_member_ref_parent(self, coded_index: int) -> str:
        """Resolve MemberRefParent coded index."""
        # MemberRefParent coded index (ECMA-335 II.24.2.6):
        # Uses 3 bits to encode table: 0=TypeDef, 1=TypeRef, 2=ModuleRef, 3=MethodDef, 4=TypeSpec
        tag = coded_index & 0x07
        row_index = coded_index >> 3

        from ..metadata.tokens import TokenType

        if tag == 1:  # TypeRef
            # Try to resolve TypeRef
            type_token = (TokenType.TypeRef.value << 24) | row_index
            return self._resolve_type_token(type_token)
        elif tag == 0:  # TypeDef
            # Try to resolve TypeDef
            type_token = (TokenType.TypeDef.value << 24) | row_index
            return self._resolve_type_token(type_token)

        # For other types, return a placeholder for now
        return f"Parent_{coded_index:04x}"

    @property
    def entry_point(self) -> "MethodDef | None":
        """Get the entry point method of the assembly, if any."""
        if not self.pe:
            return None

        try:
            net_header = self.pe.net_header
            entry_point_token_or_rva = net_header.entry_point_token_or_rva

            if entry_point_token_or_rva == 0:
                return None

            # Check if it's a token (high bit determines token vs RVA)
            if entry_point_token_or_rva & 0xFF000000:
                # It's a method token
                token = Token.from_uint32(entry_point_token_or_rva)
                if token.table == TokenType.MethodDef:
                    return self._parse_method(token.rid)

            # If it's an RVA or other format, we can't handle it yet
            return None

        except (ValueError, RuntimeError):
            return None

    def __iter__(self) -> Iterator[TypeDef]:
        """Iterate over all types in the module."""
        return iter(self.types)

    @property
    def operand_resolver(self):
        """Get cached operand resolver for this module."""
        if self._operand_resolver is None:
            from ..metadata.operands import OperandResolver

            self._operand_resolver = OperandResolver(self)
        return self._operand_resolver
