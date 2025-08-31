"""
Type definitions and references.
"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import IntFlag
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .members import EventDef, FieldDef, MethodDef, PropertyDef

from ..metadata.tokens import Token

__all__ = [
    "TypeAttributes",
    "TypeDef",
    "TypeRef",
]


class TypeAttributes(IntFlag):
    """Type attributes (ECMA-335 II.23.1.15)."""

    # Visibility attributes
    NotPublic = 0x00000000
    Public = 0x00000001
    NestedPublic = 0x00000002
    NestedPrivate = 0x00000003
    NestedFamily = 0x00000004
    NestedAssembly = 0x00000005
    NestedFamANDAssem = 0x00000006
    NestedFamORAssem = 0x00000007
    VisibilityMask = 0x00000007

    # Layout attributes
    AutoLayout = 0x00000000
    SequentialLayout = 0x00000008
    ExplicitLayout = 0x00000010
    LayoutMask = 0x00000018

    # Class semantics attributes
    Class = 0x00000000
    Interface = 0x00000020
    ClassSemanticsMask = 0x00000020

    # Special semantics
    Abstract = 0x00000080
    Sealed = 0x00000100
    SpecialName = 0x00000400

    # Implementation attributes
    Import = 0x00001000
    Serializable = 0x00002000
    WindowsRuntime = 0x00004000

    # String formatting attributes
    AnsiClass = 0x00000000
    UnicodeClass = 0x00010000
    AutoClass = 0x00020000
    CustomFormatClass = 0x00030000
    StringFormatMask = 0x00030000

    # Initialization attributes
    BeforeFieldInit = 0x00100000

    # Additional flags
    RTSpecialName = 0x00000800
    HasSecurity = 0x00040000
    IsTypeForwarder = 0x00200000


@dataclass(slots=True)
class TypeDef:
    """Type definition (ECMA-335 II.22.37)."""

    token: Token
    flags: TypeAttributes
    name: str
    namespace: str
    extends: Token | None = None
    field_list: Token | None = None
    _method_list: Token | None = None

    # for resolution
    fields: list["FieldDef"] = field(default_factory=list)
    methods: list["MethodDef"] = field(default_factory=list)
    properties: list["PropertyDef"] = field(default_factory=list)
    events: list["EventDef"] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Get the full type name (namespace + name)."""
        if self.namespace:
            return f"{self.namespace}.{self.name}"
        return self.name

    @property
    def is_public(self) -> bool:
        """Check if type is public."""
        visibility = self.flags & TypeAttributes.VisibilityMask
        return visibility == TypeAttributes.Public

    @property
    def is_nested(self) -> bool:
        """Check if type is nested."""
        visibility = self.flags & TypeAttributes.VisibilityMask
        return visibility >= TypeAttributes.NestedPublic

    @property
    def is_interface(self) -> bool:
        """Check if type is an interface."""
        return bool(self.flags & TypeAttributes.Interface)

    @property
    def is_abstract(self) -> bool:
        """Check if type is abstract."""
        return bool(self.flags & TypeAttributes.Abstract)

    @property
    def is_sealed(self) -> bool:
        """Check if type is sealed."""
        return bool(self.flags & TypeAttributes.Sealed)

    def find_method(self, name: str) -> Optional["MethodDef"]:
        """Find a method by name."""
        for method in self.methods:
            if method.name == name:
                return method
        return None

    def __iter__(self) -> Iterator["MethodDef"]:
        """Iterate over methods in this type."""
        return iter(self.methods)

    def __str__(self) -> str:
        """Return the full type name for display."""
        return self.full_name


@dataclass(frozen=True, slots=True)
class TypeRef:
    """Type reference (ECMA-335 II.22.38)."""

    token: Token
    resolution_scope: Token | None
    name: str
    namespace: str

    @property
    def full_name(self) -> str:
        """Get the full type name (namespace + name)."""
        if self.namespace:
            return f"{self.namespace}.{self.name}"
        return self.name

    def __str__(self) -> str:
        """Return the full type name for display."""
        return self.full_name


@dataclass(frozen=True, slots=True)
class TypeSpec:
    """Type specification (ECMA-335 II.22.39)."""

    token: Token
    signature: bytes
