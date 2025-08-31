"""
Token and table definitions for .NET metadata.

Based on ECMA-335 II.22 and II.24.
"""

from dataclasses import dataclass
from enum import IntEnum

__all__ = [
    "TokenType",
    "Token",
    "CodedIndexType",
]


class TokenType(IntEnum):
    """Metadata token types (ECMA-335 II.24.2.6)."""

    Module = 0x00
    TypeRef = 0x01
    TypeDef = 0x02
    FieldPtr = 0x03  # Not used
    Field = 0x04
    MethodPtr = 0x05  # Not used
    MethodDef = 0x06
    ParamPtr = 0x07  # Not used
    Param = 0x08
    InterfaceImpl = 0x09
    MemberRef = 0x0A
    DeclSecurity = 0x0B
    CustomAttribute = 0x0C
    Permission = 0x0E
    ClassLayout = 0x0F
    FieldLayout = 0x10
    StandAloneSig = 0x11
    EventMap = 0x12
    EventPtr = 0x13  # Not used
    Event = 0x14
    PropertyMap = 0x15
    PropertyPtr = 0x16  # Not used
    Property = 0x17
    MethodSemantics = 0x18
    MethodImpl = 0x19
    ModuleRef = 0x1A
    TypeSpec = 0x1B
    ImplMap = 0x1C
    FieldRva = 0x1D
    ENCLog = 0x1E  # Not used
    ENCMap = 0x1F  # Not used
    Assembly = 0x20
    AssemblyProcessor = 0x21
    AssemblyOS = 0x22
    AssemblyRef = 0x23
    AssemblyRefProcessor = 0x24
    AssemblyRefOS = 0x25
    File = 0x26
    ExportedType = 0x27
    ManifestResource = 0x28
    NestedClass = 0x29
    GenericParam = 0x2A
    MethodSpec = 0x2B
    GenericParamConstraint = 0x2C
    # UserString = 0x70  # Special case for user string heap


@dataclass(frozen=True, slots=True)
class Token:
    """Represents a metadata token (ECMA-335 II.24.2.6)."""

    table: TokenType
    rid: int  # Row ID (1-based)

    @classmethod
    def from_uint32(cls, value: int) -> "Token":
        """Create a token from a 32-bit value."""
        table = TokenType((value >> 24) & 0xFF)
        rid = value & 0x00FFFFFF
        return cls(table, rid)

    def to_uint32(self) -> int:
        """Convert token to 32-bit value."""
        return (self.table << 24) | (self.rid & 0x00FFFFFF)

    @property
    def is_null(self) -> bool:
        """Check if this is a null token."""
        return self.rid == 0

    def __str__(self) -> str:
        return f"0x{self.to_uint32():08x}"


class CodedIndexType(IntEnum):
    """Coded index types (ECMA-335 II.24.2.6)."""

    TypeDefOrRef = 0
    HasConstant = 1
    HasCustomAttribute = 2
    HasFieldMarshal = 3
    HasDeclSecurity = 4
    MemberRefParent = 5
    HasSemantics = 6
    MethodDefOrRef = 7
    MemberForwarded = 8
    Implementation = 9
    CustomAttributeType = 10
    ResolutionScope = 11
    TypeOrMethodDef = 12


# Coded index mappings (ECMA-335 II.24.2.6)
CODED_INDEX_TABLES = {
    CodedIndexType.TypeDefOrRef: [
        TokenType.TypeDef,
        TokenType.TypeRef,
        TokenType.TypeSpec,
    ],
    CodedIndexType.HasConstant: [TokenType.Field, TokenType.Param, TokenType.Property],
    CodedIndexType.HasCustomAttribute: [
        TokenType.MethodDef,
        TokenType.Field,
        TokenType.TypeRef,
        TokenType.TypeDef,
        TokenType.Param,
        TokenType.InterfaceImpl,
        TokenType.MemberRef,
        TokenType.Module,
        TokenType.Permission,
        TokenType.Property,
        TokenType.Event,
        TokenType.StandAloneSig,
        TokenType.ModuleRef,
        TokenType.TypeSpec,
        TokenType.Assembly,
        TokenType.AssemblyRef,
        TokenType.File,
        TokenType.ExportedType,
        TokenType.ManifestResource,
        TokenType.GenericParam,
        TokenType.GenericParamConstraint,
        TokenType.MethodSpec,
    ],
    CodedIndexType.MemberRefParent: [
        TokenType.TypeDef,
        TokenType.TypeRef,
        TokenType.ModuleRef,
        TokenType.MethodDef,
        TokenType.TypeSpec,
    ],
    CodedIndexType.MethodDefOrRef: [TokenType.MethodDef, TokenType.MemberRef],
    CodedIndexType.ResolutionScope: [
        TokenType.Module,
        TokenType.ModuleRef,
        TokenType.AssemblyRef,
        TokenType.TypeRef,
    ],
    CodedIndexType.Implementation: [
        TokenType.File,
        TokenType.AssemblyRef,
        TokenType.ExportedType,
    ],
}


def decode_coded_index(coded_index: CodedIndexType, value: int) -> Token:
    """Decode a coded index into a token."""
    if coded_index not in CODED_INDEX_TABLES:
        raise ValueError(f"Unknown coded index type: {coded_index}")

    tables = CODED_INDEX_TABLES[coded_index]
    tag_bits_needed = (len(tables) - 1).bit_length()
    tag_bits = value & ((1 << tag_bits_needed) - 1)
    rid = value >> tag_bits_needed

    if tag_bits >= len(tables):
        raise ValueError(f"Invalid tag {tag_bits} for coded index {coded_index}")

    return Token(tables[tag_bits], rid)


def encode_coded_index(coded_index: CodedIndexType, token: Token) -> int:
    """Encode a token into a coded index value."""
    if coded_index not in CODED_INDEX_TABLES:
        raise ValueError(f"Unknown coded index type: {coded_index}")

    tables = CODED_INDEX_TABLES[coded_index]
    try:
        tag = tables.index(token.table)
    except ValueError:
        raise ValueError(
            f"Token table {token.table} not valid for coded index {coded_index}"
        )

    tag_bits_needed = (len(tables) - 1).bit_length()
    return (token.rid << tag_bits_needed) | tag
