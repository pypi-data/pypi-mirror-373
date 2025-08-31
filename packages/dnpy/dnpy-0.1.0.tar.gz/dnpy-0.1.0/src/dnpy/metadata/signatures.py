"""
Type signatures and signature parsing (ECMA-335 II.23.2).

This module provides comprehensive support for parsing and representing .NET type signatures
according to the ECMA-335 specification.
"""

import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model.types import TypeDef, TypeRef
    from .streams import BlobHeap

__all__ = [
    "SignatureParser",
]


class ElementType(IntEnum):
    """Element types for signatures (ECMA-335 II.23.1.16)."""

    VOID = 0x01
    BOOLEAN = 0x02
    CHAR = 0x03
    I1 = 0x04  # sbyte
    U1 = 0x05  # byte
    I2 = 0x06  # short
    U2 = 0x07  # ushort
    I4 = 0x08  # int
    U4 = 0x09  # uint
    I8 = 0x0A  # long
    U8 = 0x0B  # ulong
    R4 = 0x0C  # float
    R8 = 0x0D  # double
    STRING = 0x0E
    PTR = 0x0F  # Followed by type
    BYREF = 0x10  # Followed by type
    VALUETYPE = 0x11  # Followed by TypeDef or TypeRef token
    CLASS = 0x12  # Followed by TypeDef or TypeRef token
    VAR = 0x13  # Generic parameter in a generic type definition
    ARRAY = 0x14  # type rank boundsCount bound1 ... loCount lo1 ...
    GENERICINST = 0x15  # Generic type instantiation
    TYPEDBYREF = 0x16
    I = 0x18  # System.IntPtr
    U = 0x19  # System.UIntPtr
    FNPTR = 0x1B  # Function pointer
    OBJECT = 0x1C  # System.Object
    SZARRAY = 0x1D  # Single-dimensional array with 0 lower bound
    MVAR = 0x1E  # Generic parameter in a generic method definition
    CMOD_REQD = 0x1F  # Required modifier
    CMOD_OPT = 0x20  # Optional modifier
    INTERNAL = 0x21  # Internal use only
    MODIFIER = 0x40  # Or'd with following element types
    SENTINEL = 0x41  # Sentinel for vararg method signatures
    PINNED = 0x45  # Local variable is pinned


class CallingConvention(IntEnum):
    """Calling conventions for signatures (ECMA-335 II.23.2.1)."""

    DEFAULT = 0x00
    C = 0x01
    STDCALL = 0x02
    THISCALL = 0x03
    FASTCALL = 0x04
    VARARG = 0x05
    FIELD = 0x06
    LOCAL_SIG = 0x07
    PROPERTY = 0x08
    UNMANAGED = 0x09
    GENERICINST = 0x0A
    NATIVECVARARG = 0x0B
    GENERIC = 0x10  # Generic method signature
    HASTHIS = 0x20  # Instance method signature
    EXPLICITTHIS = 0x40  # Explicit 'this' parameter


class TypeSig(ABC):
    """Base class for all type signatures."""

    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of this type signature."""
        pass

    @property
    @abstractmethod
    def element_type(self) -> ElementType:
        """Get the element type for this signature."""
        pass


@dataclass(slots=True)
class VoidSig(TypeSig):
    """Void type signature."""

    def __str__(self) -> str:
        return "void"

    @property
    def element_type(self) -> ElementType:
        return ElementType.VOID


@dataclass(slots=True)
class CorLibTypeSig(TypeSig):
    """Built-in CLR type signature."""

    type_: ElementType
    name: str

    def __str__(self) -> str:
        return self.name

    @property
    def element_type(self) -> ElementType:
        return self.type_


@dataclass(slots=True)
class ClassSig(TypeSig):
    """Class type signature (reference type)."""

    type_def_or_ref: "TypeDef | TypeRef"

    def __str__(self) -> str:
        return self.type_def_or_ref.full_name

    @property
    def element_type(self) -> ElementType:
        return ElementType.CLASS


@dataclass(slots=True)
class ValueTypeSig(TypeSig):
    """Value type signature."""

    type_def_or_ref: "TypeDef | TypeRef"

    def __str__(self) -> str:
        return self.type_def_or_ref.full_name

    @property
    def element_type(self) -> ElementType:
        return ElementType.VALUETYPE


@dataclass(slots=True)
class PtrSig(TypeSig):
    """Pointer type signature."""

    next_: TypeSig

    def __str__(self) -> str:
        return f"{self.next_}*"

    @property
    def element_type(self) -> ElementType:
        return ElementType.PTR


@dataclass(slots=True)
class ByRefSig(TypeSig):
    """By-reference type signature."""

    next_: TypeSig

    def __str__(self) -> str:
        return f"{self.next_}&"

    @property
    def element_type(self) -> ElementType:
        return ElementType.BYREF


@dataclass(slots=True)
class SZArraySig(TypeSig):
    """Single-dimensional, zero-based array signature."""

    next_: TypeSig

    def __str__(self) -> str:
        return f"{self.next_}[]"

    @property
    def element_type(self) -> ElementType:
        return ElementType.SZARRAY


@dataclass(slots=True)
class ArraySig(TypeSig):
    """Multi-dimensional array signature."""

    next_: TypeSig
    rank: int
    sizes: list[int]
    lo_bounds: list[int]

    def __str__(self) -> str:
        if self.rank == 1 and not self.sizes and not self.lo_bounds:
            return f"{self.next_}[*]"
        dims = ",".join("" for _ in range(self.rank))
        return f"{self.next_}[{dims}]"

    @property
    def element_type(self) -> ElementType:
        return ElementType.ARRAY


@dataclass(slots=True)
class GenericInstSig(TypeSig):
    """Generic type instantiation signature."""

    generic_type: TypeSig
    generic_args: list[TypeSig]

    def __str__(self) -> str:
        args = ",".join(str(arg) for arg in self.generic_args)
        return f"{self.generic_type}<{args}>"

    @property
    def element_type(self) -> ElementType:
        return ElementType.GENERICINST


@dataclass(slots=True)
class GenericVar(TypeSig):
    """Generic type parameter (T)."""

    number: int

    def __str__(self) -> str:
        return f"!{self.number}"

    @property
    def element_type(self) -> ElementType:
        return ElementType.VAR


@dataclass(slots=True)
class GenericMVar(TypeSig):
    """Generic method parameter (!!T)."""

    number: int

    def __str__(self) -> str:
        return f"!!{self.number}"

    @property
    def element_type(self) -> ElementType:
        return ElementType.MVAR


@dataclass(slots=True)
class FnPtrSig(TypeSig):
    """Function pointer signature."""

    calling_convention: CallingConvention
    return_type: TypeSig
    params: list[TypeSig]

    def __str__(self) -> str:
        param_str = ",".join(str(p) for p in self.params)
        return f"method {self.return_type} *({param_str})"

    @property
    def element_type(self) -> ElementType:
        return ElementType.FNPTR


@dataclass(slots=True)
class MethodSig:
    """Method signature."""

    calling_convention: CallingConvention
    return_type: TypeSig
    params: list[TypeSig]
    generic_param_count: int = 0

    def __str__(self) -> str:
        param_str = ",".join(str(p) for p in self.params)
        generic_str = (
            f"<[{self.generic_param_count}]>"
            if self.generic_param_count > 0
            else ""
        )
        return f"{self.return_type} {generic_str}({param_str})"

    @property
    def is_generic(self) -> bool:
        """Check if this is a generic method signature."""
        return self.generic_param_count > 0

    @property
    def has_this(self) -> bool:
        """Check if this method has an implicit 'this' parameter."""
        return bool(self.calling_convention & CallingConvention.HASTHIS)

    @property
    def is_vararg(self) -> bool:
        """Check if this method uses variable arguments."""
        return (self.calling_convention & 0x0F) == CallingConvention.VARARG


@dataclass(slots=True)
class FunctionPointerSig(TypeSig):
    """Function pointer signature."""

    calling_convention: int
    return_type: TypeSig
    param_types: list[TypeSig]

    def __str__(self) -> str:
        param_str = ",".join(str(p) for p in self.param_types)
        return f"fnptr({param_str}) -> {self.return_type}"

    @property
    def element_type(self) -> ElementType:
        return ElementType.FNPTR


@dataclass(slots=True)
class FieldSig:
    """Field signature."""

    type_: TypeSig

    def __str__(self) -> str:
        return str(self.type_)


@dataclass(slots=True)
class PropertySig:
    """Property signature."""

    calling_convention: CallingConvention
    type_: TypeSig
    params: list[TypeSig]  # For indexed properties

    def __str__(self) -> str:
        if self.params:
            param_str = ",".join(str(p) for p in self.params)
            return f"{self.type_} this[{param_str}]"
        return str(self.type_)

    @property
    def has_this(self) -> bool:
        """Check if this property has an implicit 'this' parameter."""
        return bool(self.calling_convention & CallingConvention.HASTHIS)


class SignatureParser:
    """Parser for .NET signatures from blob heap."""

    def __init__(self, blob_heap: "BlobHeap"):
        self.blob_heap = blob_heap
        # Built-in type mappings
        self._corlib_types = {
            ElementType.VOID: VoidSig(),
            ElementType.BOOLEAN: CorLibTypeSig(ElementType.BOOLEAN, "bool"),
            ElementType.CHAR: CorLibTypeSig(ElementType.CHAR, "char"),
            ElementType.I1: CorLibTypeSig(ElementType.I1, "sbyte"),
            ElementType.U1: CorLibTypeSig(ElementType.U1, "byte"),
            ElementType.I2: CorLibTypeSig(ElementType.I2, "short"),
            ElementType.U2: CorLibTypeSig(ElementType.U2, "ushort"),
            ElementType.I4: CorLibTypeSig(ElementType.I4, "int"),
            ElementType.U4: CorLibTypeSig(ElementType.U4, "uint"),
            ElementType.I8: CorLibTypeSig(ElementType.I8, "long"),
            ElementType.U8: CorLibTypeSig(ElementType.U8, "ulong"),
            ElementType.R4: CorLibTypeSig(ElementType.R4, "float"),
            ElementType.R8: CorLibTypeSig(ElementType.R8, "double"),
            ElementType.STRING: CorLibTypeSig(ElementType.STRING, "string"),
            ElementType.OBJECT: CorLibTypeSig(ElementType.OBJECT, "object"),
            ElementType.I: CorLibTypeSig(ElementType.I, "System.IntPtr"),
            ElementType.U: CorLibTypeSig(ElementType.U, "System.UIntPtr"),
            ElementType.TYPEDBYREF: CorLibTypeSig(
                ElementType.TYPEDBYREF, "System.TypedReference"
            ),
        }

    def parse_method_sig(self, blob_index: int) -> MethodSig:
        """Parse a method signature from the blob heap."""
        data = self.blob_heap.get_blob(blob_index)
        return self._parse_method_sig_from_data(data)

    def parse_field_sig(self, blob_index: int) -> FieldSig:
        """Parse a field signature from the blob heap."""
        data = self.blob_heap.get_blob(blob_index)
        return self._parse_field_sig_from_data(data)

    def parse_property_sig(self, blob_index: int) -> PropertySig:
        """Parse a property signature from the blob heap."""
        data = self.blob_heap.get_blob(blob_index)
        return self._parse_property_sig_from_data(data)

    def parse_type_spec_sig(self, blob_index: int) -> TypeSig:
        """Parse a type specification signature from the blob heap."""
        data = self.blob_heap.get_blob(blob_index)
        reader = SignatureReader(data)
        return self._read_type_sig(reader)

    def _parse_method_sig_from_data(self, data: bytes) -> MethodSig:
        """Parse method signature from raw data."""
        reader = SignatureReader(data)

        # Read calling convention
        calling_conv = CallingConvention(reader.read_byte())

        # Read generic parameter count if generic
        generic_param_count = 0
        if calling_conv & CallingConvention.GENERIC:
            generic_param_count = reader.read_compressed_uint()

        # Read parameter count
        param_count = reader.read_compressed_uint()

        # Read return type
        return_type = self._read_type_sig(reader)

        # Read parameters
        params = []
        for _ in range(param_count):
            param_type = self._read_type_sig(reader)
            params.append(param_type)

        return MethodSig(
            calling_convention=calling_conv,
            return_type=return_type,
            params=params,
            generic_param_count=generic_param_count,
        )

    def _parse_field_sig_from_data(self, data: bytes) -> FieldSig:
        """Parse field signature from raw data."""
        reader = SignatureReader(data)

        # Read calling convention (should be FIELD = 0x06)
        calling_conv = reader.read_byte()
        if calling_conv != CallingConvention.FIELD:
            raise ValueError(
                f"Invalid field signature calling convention: 0x{calling_conv:02x}"
            )

        # Read field type
        field_type = self._read_type_sig(reader)

        return FieldSig(type_=field_type)

    def _parse_property_sig_from_data(self, data: bytes) -> PropertySig:
        """Parse property signature from raw data."""
        reader = SignatureReader(data)

        # Read calling convention
        calling_conv = CallingConvention(reader.read_byte())

        # Read parameter count
        param_count = reader.read_compressed_uint()

        # Read property type
        prop_type = self._read_type_sig(reader)

        # Read parameters (for indexed properties)
        params = []
        for _ in range(param_count):
            param_type = self._read_type_sig(reader)
            params.append(param_type)

        return PropertySig(
            calling_convention=calling_conv, type_=prop_type, params=params
        )

    def _read_type_sig(self, reader: "SignatureReader") -> TypeSig:
        """Read a type signature from the signature stream."""
        element_type = ElementType(reader.read_byte())

        # Handle simple types
        if element_type in self._corlib_types:
            return self._corlib_types[element_type]

        # Handle complex types
        if element_type == ElementType.PTR:
            next_type = self._read_type_sig(reader)
            return PtrSig(next_type)
        elif element_type == ElementType.BYREF:
            next_type = self._read_type_sig(reader)
            return ByRefSig(next_type)
        elif element_type == ElementType.SZARRAY:
            next_type = self._read_type_sig(reader)
            return SZArraySig(next_type)
        elif element_type == ElementType.ARRAY:
            next_type = self._read_type_sig(reader)
            rank = reader.read_compressed_uint()

            num_sizes = reader.read_compressed_uint()
            sizes = []
            for _ in range(num_sizes):
                sizes.append(reader.read_compressed_uint())

            num_lo_bounds = reader.read_compressed_uint()
            lo_bounds = []
            for _ in range(num_lo_bounds):
                lo_bounds.append(reader.read_compressed_int())

            return ArraySig(next_type, rank, sizes, lo_bounds)
        elif element_type == ElementType.CLASS:
            token = reader.read_type_def_or_ref_token()
            # Try to resolve token to actual type
            type_def = (
                self._resolve_type_token(token)
                if hasattr(self, "_resolve_type_token")
                else None
            )
            return ClassSig(type_def)
        elif element_type == ElementType.VALUETYPE:
            token = reader.read_type_def_or_ref_token()
            # Try to resolve token to actual type
            type_def = (
                self._resolve_type_token(token)
                if hasattr(self, "_resolve_type_token")
                else None
            )
            return ValueTypeSig(type_def)
        elif element_type == ElementType.VAR:
            number = reader.read_compressed_uint()
            return GenericVar(number)
        elif element_type == ElementType.MVAR:
            number = reader.read_compressed_uint()
            return GenericMVar(number)
        elif element_type == ElementType.GENERICINST:
            # Read the generic type (CLASS or VALUETYPE)
            generic_element = ElementType(reader.read_byte())
            if generic_element == ElementType.CLASS:
                token = reader.read_type_def_or_ref_token()
                generic_type = ClassSig(None)  # type: ignore
            elif generic_element == ElementType.VALUETYPE:
                token = reader.read_type_def_or_ref_token()
                generic_type = ValueTypeSig(None)  # type: ignore
            else:
                raise ValueError(
                    f"Invalid generic instantiation element type: {generic_element}"
                )

            # Read generic argument count
            arg_count = reader.read_compressed_uint()

            # Read generic arguments
            generic_args = []
            for _ in range(arg_count):
                arg_type = self._read_type_sig(reader)
                generic_args.append(arg_type)

            return GenericInstSig(generic_type, generic_args)
        elif element_type == ElementType.FNPTR:
            # Parse function pointer signature (ECMA-335 II.23.2.5)
            # A function pointer signature is essentially a method signature
            calling_convention = reader.read_byte()
            param_count = reader.read_compressed_uint()

            # Read return type
            return_type = self._read_type_sig(reader)

            # Read parameter types
            param_types = []
            for _ in range(param_count):
                param_type = self._read_type_sig(reader)
                param_types.append(param_type)

            return FunctionPointerSig(
                calling_convention, return_type, param_types
            )
        else:
            raise ValueError(f"Unknown element type: {element_type}")


class SignatureReader:
    """Helper class for reading signature data."""

    def __init__(self, data: bytes):
        self.data = data
        self.position = 0

    def read_byte(self) -> int:
        """Read a single byte."""
        if self.position >= len(self.data):
            raise ValueError("Unexpected end of signature data")
        value = self.data[self.position]
        self.position += 1
        return value

    def read_compressed_uint(self) -> int:
        """Read a compressed unsigned integer (ECMA-335 II.23.2)."""
        b1 = self.read_byte()

        if (b1 & 0x80) == 0:
            # Single byte: 0xxxxxxx
            return b1
        elif (b1 & 0xC0) == 0x80:
            # Two bytes: 10xxxxxx xxxxxxxx
            b2 = self.read_byte()
            return ((b1 & 0x3F) << 8) | b2
        elif (b1 & 0xE0) == 0xC0:
            # Four bytes: 110xxxxx xxxxxxxx xxxxxxxx xxxxxxxx
            b2 = self.read_byte()
            b3 = self.read_byte()
            b4 = self.read_byte()
            return ((b1 & 0x1F) << 24) | (b2 << 16) | (b3 << 8) | b4
        else:
            raise ValueError("Invalid compressed integer encoding")

    def read_compressed_int(self) -> int:
        """Read a compressed signed integer."""
        value = self.read_compressed_uint()
        # Handle sign extension for negative values
        if value & 1:
            return -(value >> 1)
        else:
            return value >> 1

    def read_type_def_or_ref_token(self) -> int:
        """Read a TypeDefOrRef coded index token."""
        return self.read_compressed_uint()
