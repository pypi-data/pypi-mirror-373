"""
Member definitions (methods, fields, properties, events).
"""

from dataclasses import dataclass, field
from enum import IntFlag
from typing import TYPE_CHECKING

from ..metadata.tokens import Token

if TYPE_CHECKING:
    from ..metadata.il import CilBody, Instruction
    from .module import Module

__all__ = [
    "FieldAttributes",
    "MethodAttributes",
    "MethodImplAttributes",
    "FieldDef",
    "MethodDef",
    "PropertyDef",
    "EventDef",
    "MemberRef",
]


class FieldAttributes(IntFlag):
    """Field attributes (ECMA-335 II.23.1.5)."""

    # Accessibility
    CompilerControlled = 0x0000
    Private = 0x0001
    FamANDAssem = 0x0002
    Assembly = 0x0003
    Family = 0x0004
    FamORAssem = 0x0005
    Public = 0x0006
    FieldAccessMask = 0x0007

    # Contract attributes
    Static = 0x0010
    InitOnly = 0x0020
    Literal = 0x0040
    NotSerialized = 0x0080
    SpecialName = 0x0200

    # Interop attributes
    PinvokeImpl = 0x2000

    # Additional flags
    RTSpecialName = 0x0400
    HasFieldMarshal = 0x1000
    HasDefault = 0x8000
    HasFieldRVA = 0x0100


class MethodAttributes(IntFlag):
    """Method attributes (ECMA-335 II.23.1.10)."""

    # Accessibility
    CompilerControlled = 0x0000
    Private = 0x0001
    FamANDAssem = 0x0002
    Assembly = 0x0003
    Family = 0x0004
    FamORAssem = 0x0005
    Public = 0x0006
    MemberAccessMask = 0x0007

    # Contract attributes
    Static = 0x0010
    Final = 0x0020
    Virtual = 0x0040
    HideBySig = 0x0080

    # Vtable layout
    ReuseSlot = 0x0000
    NewSlot = 0x0100
    VtableLayoutMask = 0x0100

    # Implementation attributes
    CheckAccessOnOverride = 0x0200
    Abstract = 0x0400
    SpecialName = 0x0800

    # Interop attributes
    PinvokeImpl = 0x2000
    UnmanagedExport = 0x0008

    # Additional flags
    RTSpecialName = 0x1000
    HasSecurity = 0x4000
    RequireSecObject = 0x8000


class MethodImplAttributes(IntFlag):
    """Method implementation attributes (ECMA-335 II.23.1.11)."""

    # Code type
    IL = 0x0000
    Native = 0x0001
    OPTIL = 0x0002
    Runtime = 0x0003
    CodeTypeMask = 0x0003

    # Managed type
    Unmanaged = 0x0004
    Managed = 0x0000
    ManagedMask = 0x0004

    # Implementation flags
    ForwardRef = 0x0010
    PreserveSig = 0x0080
    InternalCall = 0x1000
    Synchronized = 0x0020
    NoInlining = 0x0008
    MaxMethodImplVal = 0xFFFF


@dataclass(slots=True)
class FieldDef:
    """Field definition (ECMA-335 II.22.15)."""

    token: Token
    flags: FieldAttributes
    name: str
    signature: bytes

    @property
    def is_public(self) -> bool:
        """Check if field is public."""
        return (
            self.flags & FieldAttributes.FieldAccessMask
        ) == FieldAttributes.Public

    @property
    def is_static(self) -> bool:
        """Check if field is static."""
        return bool(self.flags & FieldAttributes.Static)

    @property
    def is_literal(self) -> bool:
        """Check if field is a literal (constant)."""
        return bool(self.flags & FieldAttributes.Literal)

    def __str__(self) -> str:
        """Return the field name for display."""
        return self.name


@dataclass(slots=True)
class MethodDef:
    """Method definition (ECMA-335 II.22.26)."""

    token: Token
    rva: int
    impl_flags: MethodImplAttributes
    flags: MethodAttributes
    name: str
    signature: bytes
    param_list: Token | None = None

    # lazy load
    _cil_body: "CilBody | None" = field(default=None, init=False)
    _module: "Module | None" = field(default=None, init=False)

    @property
    def is_public(self) -> bool:
        """Check if method is public."""
        return (
            self.flags & MethodAttributes.MemberAccessMask
        ) == MethodAttributes.Public

    @property
    def is_static(self) -> bool:
        """Check if method is static."""
        return bool(self.flags & MethodAttributes.Static)

    @property
    def is_virtual(self) -> bool:
        """Check if method is virtual."""
        return bool(self.flags & MethodAttributes.Virtual)

    @property
    def is_abstract(self) -> bool:
        """Check if method is abstract."""
        return bool(self.flags & MethodAttributes.Abstract)

    @property
    def has_body(self) -> bool:
        """Check if method has a CIL body."""
        return self.rva > 0 and not (self.flags & MethodAttributes.Abstract)

    @property
    def body(self) -> "CilBody | None":
        """Get the CIL body for this method (if available)."""
        # Auto-parse the method body
        if (
            self._cil_body is None
            and self._module is not None
            and self.has_body
        ):
            self._cil_body = self._module.parse_method_body(self)
        return self._cil_body

    @property
    def instructions(self) -> list["Instruction"]:
        """Get the CIL instructions for this method."""
        body = self.body
        if body and hasattr(body, "instructions"):
            return body.instructions
        return []

    def _set_cil_body(self, body: "CilBody") -> None:
        """Set the CIL body (used by the parser)."""
        self._cil_body = body

    def _set_module(self, module: "Module") -> None:
        """Set the parent module reference (used during method creation)."""
        self._module = module

    @property
    def parsed_signature(self) -> str:
        """Get the human-readable signature for this method."""
        if self._module is None:
            return self.name

        if isinstance(self.signature, bytes) and len(self.signature) > 0:
            try:
                from ..metadata.signatures import SignatureParser

                if self._module.blob_heap:
                    parser = SignatureParser(self._module.blob_heap)
                    method_sig = parser._parse_method_sig_from_data(
                        self.signature
                    )
                    params = ", ".join(
                        str(param) for param in method_sig.params
                    )
                    return f"{self.name}({params}) : {method_sig.return_type}"
            except Exception as e:
                # return just the method name
                pass

        return self.name

    def __str__(self) -> str:
        """Return the method name for display."""
        return self.name


@dataclass(slots=True)
class PropertyDef:
    """Property definition (ECMA-335 II.22.34)."""

    token: Token
    flags: int
    name: str
    type_signature: bytes
    getter: MethodDef | None = None
    setter: MethodDef | None = None
    other_methods: list[MethodDef] = field(default_factory=list)


@dataclass(slots=True)
class EventDef:
    """Event definition (ECMA-335 II.22.13)."""

    token: Token
    flags: int  # EventAttributes
    name: str
    event_type: Token | None = None  # TypeDefOrRef
    add_method: MethodDef | None = None
    remove_method: MethodDef | None = None
    fire_method: MethodDef | None = None
    other_methods: list[MethodDef] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class MemberRef:
    """Member reference (ECMA-335 II.22.25)."""

    token: Token
    class_: Token | None
    name: str
    signature: bytes

    def __str__(self) -> str:
        """Return the member name for display."""
        return self.name
