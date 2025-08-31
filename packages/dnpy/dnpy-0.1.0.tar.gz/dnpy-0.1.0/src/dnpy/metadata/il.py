"""
CIL instruction model and method body parsing.

This module provides comprehensive CIL instruction parsing and method body analysis
according to ECMA-335 specifications.
"""

import struct
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .opcodes import (
    FlowControl,
    OpCode,
    OpCodeType,
    OperandType,
    StackBehaviour,
)

if TYPE_CHECKING:
    from ..model.module import Module
    from ..model.members import MethodDef

__all__ = [
    "ILParseError",
    "MethodBodyHeaderType",
    "ExceptionHandlerType",
    "Instruction",
    "ExceptionHandler",
    "CilBody",
    "CilBodyParser",
]


class ILParseError(Exception):
    pass


class MethodBodyHeaderType:
    """Method body header types (ECMA-335 II.25.4.4)."""

    TINY = "Tiny"
    FAT = "Fat"


class ExceptionHandlerType:
    """Exception handler types (ECMA-335 II.25.4.6)."""

    EXCEPTION = 0x0000  # Catch clause
    FILTER = 0x0001  # Filter clause
    FINALLY = 0x0002  # Finally clause
    FAULT = 0x0004  # Fault clause


@dataclass(slots=True)
class Instruction:
    """Represents a single CIL instruction (ECMA-335 III.1.2)."""

    opcode: "OpCode"
    raw_operand: Any | None = None
    offset: int = 0
    _module: "Module | None" = None  # for token resolution

    @property
    def operand(self) -> Any | None:
        """Get the resolved operand value if possible, otherwise return raw operand."""
        if self.raw_operand is None:
            return None

        if self._module is not None:
            try:
                resolved = self._module.operand_resolver.resolve_operand(
                    self.raw_operand, self.opcode.operand_type.name
                )
                return (
                    resolved.resolved_value
                    if resolved.resolved_value is not None
                    else self.raw_operand
                )
            except Exception:
                ...

        return self.raw_operand

    @operand.setter
    def operand(self, value: Any | None) -> None:
        self.raw_operand = value

    def __str__(self) -> str:
        if self.operand is not None:
            return f"IL_{self.offset:04x}: {self.opcode.name} {self.operand}"
        return f"IL_{self.offset:04x}: {self.opcode.name}"

    def _is_metadata_token(self, value: int) -> bool:
        """Check if a value is a metadata token."""
        if value <= 0:
            return False

        table_id = (value >> 24) & 0xFF

        # Valid metadata table IDs
        valid_table_ids = {
            0x01,  # TypeRef
            0x02,  # TypeDef
            0x04,  # Field
            0x06,  # MethodDef
            0x0A,  # MemberRef
            0x1B,  # TypeSpec
            0x2B,  # MethodSpec
            0x23,  # AssemblyRef
            0x70,  # UserString
        }

        return table_id in valid_table_ids

    @property
    def size(self) -> int:
        return self.opcode.size + self._get_operand_size()

    def _get_operand_size(self) -> int:
        """Get the size of this instruction's operand in bytes."""
        from .opcodes import OperandType

        operand_type = self.opcode.operand_type
        if operand_type == OperandType.InlineNone:
            return 0
        elif operand_type in [
            OperandType.ShortInlineI,
            OperandType.ShortInlineVar,
        ]:
            return 1
        elif operand_type == OperandType.ShortInlineBrTarget:
            return 1
        elif operand_type == OperandType.ShortInlineR:
            return 4
        elif operand_type in [
            OperandType.InlineI,
            OperandType.InlineMethod,
            OperandType.InlineField,
            OperandType.InlineType,
            OperandType.InlineString,
            OperandType.InlineTok,
            OperandType.InlineSig,
            OperandType.InlineVar,
            OperandType.InlineBrTarget,
        ]:
            return 4
        elif operand_type == OperandType.InlineI8:
            return 8
        elif operand_type == OperandType.InlineR:
            return 8
        elif operand_type == OperandType.InlineSwitch:
            # Switch has variable size based on number of targets
            if isinstance(self.raw_operand, list):
                return 4 + (4 * len(self.raw_operand))  # count + targets
            return 4  # Just the count if no targets
        return 0


@dataclass(slots=True)
class ExceptionHandler:
    """Exception handler block (ECMA-335 II.25.4.6)."""

    flags: int  # ExceptionHandlingClauseOptions
    try_offset: int
    try_length: int
    handler_offset: int
    handler_length: int
    class_token: int | None = None  # For catch clauses
    filter_offset: int | None = None  # For filter clauses

    @property
    def is_catch(self) -> bool:
        """Check if this is a catch handler."""
        return (self.flags & 0x0007) == ExceptionHandlerType.EXCEPTION

    @property
    def is_filter(self) -> bool:
        """Check if this is a filter handler."""
        return (self.flags & 0x0007) == ExceptionHandlerType.FILTER

    @property
    def is_finally(self) -> bool:
        """Check if this is a finally handler."""
        return (self.flags & 0x0007) == ExceptionHandlerType.FINALLY

    @property
    def is_fault(self) -> bool:
        """Check if this is a fault handler."""
        return (self.flags & 0x0007) == ExceptionHandlerType.FAULT


@dataclass(slots=True)
class CilBody:
    """CIL method body (ECMA-335 II.25.4)."""

    max_stack: int
    init_locals: bool
    local_var_sig_tok: int
    instructions: list[Instruction]
    exception_handlers: list[ExceptionHandler]

    @property
    def code_size(self) -> int:
        """Get the size of the IL code in bytes."""
        if not self.instructions:
            return 0
        total_size = 0
        for instruction in self.instructions:
            total_size += instruction.size
        return total_size

    def get_instruction_at_offset(self, offset: int) -> Instruction | None:
        """Get the instruction at the specified IL offset."""
        for instruction in self.instructions:
            if instruction.offset == offset:
                return instruction
        return None

    def get_branch_targets(self) -> set[int]:
        """Get all branch target offsets in this method body."""
        targets = set()
        for instruction in self.instructions:
            if (
                instruction.opcode.flow_control.name.endswith("Branch")
                or instruction.opcode.flow_control.name == "Cond_Branch"
            ):
                if isinstance(instruction.operand, int):
                    targets.add(instruction.operand)
                elif isinstance(
                    instruction.operand, list
                ):  # Switch instruction
                    targets.update(instruction.operand)
        return targets


class CilBodyParser:
    """Parser for CIL method bodies (ECMA-335 II.25.4)."""

    def __init__(self, pe_data: bytes, pe_instance=None, module=None):
        self.pe_data = pe_data
        self.pe_instance = pe_instance
        self.module = module

    def parse_method_body(self, rva: int) -> CilBody | None:
        """Parse a CIL method body from the given RVA."""
        if rva == 0:
            return None
        try:
            file_offset = self._rva_to_file_offset(rva)
            if file_offset is None:
                raise ILParseError(
                    f"Could not convert RVA 0x{rva:x} to file offset"
                )

            header_info = self._parse_method_header(file_offset)
            if header_info is None:
                raise ILParseError(
                    f"Could not parse method header at file offset 0x{file_offset:x}"
                )

            (
                header_type,
                max_stack,
                init_locals,
                local_var_sig_tok,
                code_size,
                eh_size,
                code_offset,
            ) = header_info

            if code_size > 1024 * 1024:
                raise ILParseError(f"Method body too large: {code_size} bytes")

            instructions = self._parse_instructions(code_offset, code_size)

            exception_handlers = []
            if eh_size > 0:
                eh_offset = code_offset + code_size
                exception_handlers = self._parse_exception_handlers(
                    eh_offset, eh_size
                )
            return CilBody(
                max_stack=max_stack,
                init_locals=init_locals,
                local_var_sig_tok=local_var_sig_tok,
                instructions=instructions,
                exception_handlers=exception_handlers,
            )

        except ILParseError:
            raise
        except Exception as e:
            raise ILParseError(
                f"Unexpected error parsing method body at RVA 0x{rva:x}: {e}"
            ) from e

    def _rva_to_file_offset(self, rva: int) -> int | None:
        """Convert RVA to file offset using proper PE section mapping."""
        if self.pe_instance is not None:
            try:
                return self.pe_instance.get_offset_from_rva(rva)
            except Exception:
                pass
        return None

    def _parse_method_header(self, file_offset: int) -> tuple | None:
        """Parse method body header (ECMA-335 II.25.4.4)."""
        if file_offset + 1 >= len(self.pe_data):
            return None

        first_byte = self.pe_data[file_offset]

        if (first_byte & 0x03) == 0x02:  # Tiny header
            code_size = first_byte >> 2
            return (
                MethodBodyHeaderType.TINY,
                8,  # Default max stack for tiny
                False,  # init_locals
                0,  # local_var_sig_tok
                code_size,
                0,  # eh_size
                file_offset + 1,  # code_offset
            )
        elif (first_byte & 0x03) == 0x03:  # Fat header
            if file_offset + 12 >= len(self.pe_data):
                return None

            try:
                fat_header = struct.unpack_from(
                    "<HHIIH", self.pe_data, file_offset
                )
                flags_size = fat_header[0]
                max_stack = fat_header[1]
                code_size = fat_header[2]
                local_var_sig_tok = fat_header[3]
            except (struct.error, IndexError):
                return None

            init_locals = bool(flags_size & 0x10)
            more_sects = bool(flags_size & 0x08)

            header_size = (flags_size & 0xF000) >> 12
            if header_size != 3:  # Should be 3 for fat header
                return None

            eh_size = 0
            if more_sects:
                # Calculate actual exception handler size
                eh_size = self._calculate_exception_handler_size(
                    file_offset + 12 + code_size
                )

            return (
                MethodBodyHeaderType.FAT,
                max_stack,
                init_locals,
                local_var_sig_tok,
                code_size,
                eh_size,
                file_offset + 12,  # code_offset
            )

        return None

    def _parse_instructions(
        self, code_offset: int, code_size: int
    ) -> list[Instruction]:
        """Parse CIL instructions from method body."""
        from .opcodes import OpCodes, OperandType

        instructions = []
        offset = 0

        while offset < code_size and code_offset + offset < len(self.pe_data):
            il_offset = offset

            # Bounds check
            if code_offset + offset >= len(self.pe_data):
                break

            opcode_byte = self.pe_data[code_offset + offset]
            offset += 1

            # Handle two-byte opcodes (0xFE prefix)
            if opcode_byte == 0xFE:
                # bounds check
                if offset >= code_size or code_offset + offset >= len(
                    self.pe_data
                ):
                    break
                second_byte = self.pe_data[code_offset + offset]
                offset += 1
                opcode_value = (0xFE << 8) | second_byte
            else:
                opcode_value = opcode_byte

            opcode = OpCodes.get_opcode(opcode_value)
            if opcode is None:
                opcode = OpCode(
                    f"unknown_{opcode_value:02x}",
                    opcode_value,
                    2 if opcode_value > 0xFF else 1,
                    OperandType.InlineNone,
                    FlowControl.Next,
                    OpCodeType.Primitive,
                    StackBehaviour.Pop0,
                    StackBehaviour.Push0,
                )

            operand = None
            operand_size = self._get_operand_size(opcode.operand_type)

            if opcode.operand_type == OperandType.InlineSwitch:
                # For switch, we need at least 4 bytes for count
                if (
                    offset + 4 <= code_size
                    and code_offset + offset + 4 <= len(self.pe_data)
                ):
                    count = struct.unpack_from(
                        "<I", self.pe_data, code_offset + offset
                    )[0]
                    if count <= 10000:
                        actual_size = 4 + (count * 4)
                        if (
                            offset + actual_size <= code_size
                            and code_offset + offset + actual_size
                            <= len(self.pe_data)
                        ):
                            operand = self._parse_operand(
                                code_offset + offset,
                                opcode.operand_type,
                                il_offset,
                                opcode,
                            )
                            offset += actual_size
                    else:
                        break
            elif operand_size > 0:
                if (
                    offset + operand_size <= code_size
                    and code_offset + offset + operand_size
                    <= len(self.pe_data)
                ):
                    operand = self._parse_operand(
                        code_offset + offset,
                        opcode.operand_type,
                        il_offset,
                        opcode,
                    )
                    offset += operand_size
                else:
                    break

            instruction = Instruction(
                opcode=opcode,
                raw_operand=operand,
                offset=il_offset,
                _module=self.module,
            )
            instructions.append(instruction)

        return instructions

    def _get_operand_size(self, operand_type: "OperandType") -> int:
        """Get the size of an operand in bytes."""
        from .opcodes import OperandType

        operand_sizes = {
            OperandType.InlineNone: 0,
            OperandType.ShortInlineI: 1,
            OperandType.ShortInlineVar: 1,
            OperandType.ShortInlineBrTarget: 1,
            OperandType.ShortInlineR: 4,
            OperandType.InlineI: 4,
            OperandType.InlineVar: 4,
            OperandType.InlineBrTarget: 4,
            OperandType.InlineMethod: 4,
            OperandType.InlineField: 4,
            OperandType.InlineType: 4,
            OperandType.InlineString: 4,
            OperandType.InlineTok: 4,
            OperandType.InlineSig: 4,
            OperandType.InlineI8: 8,
            OperandType.InlineR: 8,
            OperandType.InlineSwitch: 4,  # At least 4 bytes for count
        }
        return operand_sizes.get(operand_type, 0)

    def _parse_operand(
        self,
        file_offset: int,
        operand_type: "OperandType",
        instruction_offset: int,
        opcode: "OpCode" = None,
    ) -> Any:
        """Parse an instruction operand."""
        from .opcodes import OperandType

        if operand_type == OperandType.InlineNone:
            return None
        elif operand_type == OperandType.ShortInlineI:
            return self._safe_unpack("<b", file_offset, 0)
        elif operand_type == OperandType.ShortInlineVar:
            return self._safe_unpack("<B", file_offset, 0)
        elif operand_type == OperandType.ShortInlineBrTarget:
            offset = self._safe_unpack("<b", file_offset, 0)
            if offset is None:
                return instruction_offset  # Safe fallback
            # Branch target = next instruction offset + branch offset
            # Short branch: opcode + operand(1)
            opcode_size = opcode.size if opcode else 1
            next_instruction_offset = instruction_offset + opcode_size + 1
            return next_instruction_offset + offset
        elif operand_type == OperandType.ShortInlineR:
            return self._safe_unpack("<f", file_offset, 0.0)
        elif operand_type == OperandType.InlineI:
            return self._safe_unpack("<i", file_offset, 0)
        elif operand_type == OperandType.InlineVar:
            return self._safe_unpack("<H", file_offset, 0)
        elif operand_type == OperandType.InlineBrTarget:
            offset = self._safe_unpack("<i", file_offset, 0)
            if offset is None:
                return instruction_offset  # Safe fallback
            # Branch target = next instruction offset + branch offset
            # Long branch: opcode(1 or 2) + operand(4) = 5 or 6 bytes
            # Use the actual opcode size if available
            opcode_size = opcode.size if opcode else 1
            next_instruction_offset = instruction_offset + opcode_size + 4
            return next_instruction_offset + offset
        elif operand_type in [
            OperandType.InlineMethod,
            OperandType.InlineField,
            OperandType.InlineType,
            OperandType.InlineString,
            OperandType.InlineTok,
            OperandType.InlineSig,
        ]:
            return self._safe_unpack("<I", file_offset, 0)
        elif operand_type == OperandType.InlineI8:
            return self._safe_unpack("<q", file_offset, 0)
        elif operand_type == OperandType.InlineR:
            return self._safe_unpack("<d", file_offset, 0.0)
        elif operand_type == OperandType.InlineSwitch:
            count = self._safe_unpack("<I", file_offset, 0)
            if count is None or count == 0:
                return []

            # prevent memory issues
            if count > 10000:
                return []

            # Check if we have enough data for all targets
            required_bytes = 4 + (count * 4)  # count(4) + targets(count*4)
            if file_offset + required_bytes > len(self.pe_data):
                return []

            targets = []
            # swithc opcode + count(4) + targets(count*4)
            opcode_size = 1  # switch is single-byte opcode (0x45)
            next_instruction_offset = (
                instruction_offset + opcode_size + required_bytes
            )

            for i in range(count):
                target_offset = self._safe_unpack(
                    "<i", file_offset + 4 + (i * 4), 0
                )
                if target_offset is None:
                    continue
                target_address = next_instruction_offset + target_offset
                targets.append(target_address)
            return targets

        return None

    def _parse_exception_handlers(
        self, eh_offset: int, eh_size: int
    ) -> list[ExceptionHandler]:
        """Parse exception handler blocks (ECMA-335 II.25.4.6)."""
        exception_handlers = []

        if eh_size == 0 or eh_offset + 4 >= len(self.pe_data):
            return exception_handlers

        try:
            kind = self.pe_data[eh_offset]

            if (kind & 0x01) == 0x01:  # EH_TABLE
                data_size = (
                    self.pe_data[eh_offset + 1]
                    | (self.pe_data[eh_offset + 2] << 8)
                    | (self.pe_data[eh_offset + 3] << 16)
                ) >> 8
                clause_count = data_size // 12
                offset = eh_offset + 4

                for i in range(clause_count):
                    if offset + 12 > len(self.pe_data):
                        break

                    flags = self._safe_unpack("<H", offset, 0)
                    try_offset = self._safe_unpack("<H", offset + 2, 0)
                    try_length = self._safe_unpack("<B", offset + 4, 0)
                    handler_offset = self._safe_unpack("<H", offset + 5, 0)
                    handler_length = self._safe_unpack("<B", offset + 7, 0)
                    class_token_or_filter = self._safe_unpack(
                        "<I", offset + 8, 0
                    )

                    if any(
                        v is None
                        for v in [
                            flags,
                            try_offset,
                            try_length,
                            handler_offset,
                            handler_length,
                            class_token_or_filter,
                        ]
                    ):
                        continue

                    class_token = None
                    filter_offset = None

                    if (flags & 0x0007) == ExceptionHandlerType.EXCEPTION:
                        class_token = class_token_or_filter
                    elif (flags & 0x0007) == ExceptionHandlerType.FILTER:
                        filter_offset = class_token_or_filter

                    eh = ExceptionHandler(
                        flags=flags,
                        try_offset=try_offset,
                        try_length=try_length,
                        handler_offset=handler_offset,
                        handler_length=handler_length,
                        class_token=class_token,
                        filter_offset=filter_offset,
                    )
                    exception_handlers.append(eh)
                    offset += 12

            elif (kind & 0x40) == 0x40:  # EH_FAT_FORMAT
                data_size = (
                    self.pe_data[eh_offset + 1]
                    | (self.pe_data[eh_offset + 2] << 8)
                    | (self.pe_data[eh_offset + 3] << 16)
                ) >> 8
                clause_count = data_size // 24
                offset = eh_offset + 4

                for i in range(clause_count):
                    if offset + 24 > len(self.pe_data):
                        break

                    flags = self._safe_unpack("<I", offset, 0)
                    try_offset = self._safe_unpack("<I", offset + 4, 0)
                    try_length = self._safe_unpack("<I", offset + 8, 0)
                    handler_offset = self._safe_unpack("<I", offset + 12, 0)
                    handler_length = self._safe_unpack("<I", offset + 16, 0)

                    class_token_or_filter = self._safe_unpack(
                        "<I", offset + 20, 0
                    )

                    if any(
                        v is None
                        for v in [
                            flags,
                            try_offset,
                            try_length,
                            handler_offset,
                            handler_length,
                            class_token_or_filter,
                        ]
                    ):
                        continue  # Skip invalid clause

                    class_token = None
                    filter_offset = None

                    if (flags & 0x0007) == ExceptionHandlerType.EXCEPTION:
                        class_token = class_token_or_filter
                    elif (flags & 0x0007) == ExceptionHandlerType.FILTER:
                        filter_offset = class_token_or_filter

                    eh = ExceptionHandler(
                        flags=flags,
                        try_offset=try_offset,
                        try_length=try_length,
                        handler_offset=handler_offset,
                        handler_length=handler_length,
                        class_token=class_token,
                        filter_offset=filter_offset,
                    )
                    exception_handlers.append(eh)
                    offset += 24

            if (kind & 0x80) == 0x80:
                next_offset = eh_offset + eh_size
                # Align to 4-byte boundary
                next_offset = (next_offset + 3) & ~3
                if next_offset < len(self.pe_data):
                    next_eh_size = self._calculate_exception_handler_size(
                        next_offset
                    )
                    additional_handlers = self._parse_exception_handlers(
                        next_offset, next_eh_size
                    )
                    exception_handlers.extend(additional_handlers)

        except Exception:
            pass

        return exception_handlers

    def _calculate_exception_handler_size(self, eh_offset: int) -> int:
        """Calculate the actual size of exception handler section."""
        if eh_offset + 4 >= len(self.pe_data):
            return 0

        try:
            kind = self.pe_data[eh_offset]

            if (kind & 0x01) == 0x01:  # EH_TABLE (small format)
                data_size = (
                    self.pe_data[eh_offset + 1]
                    | (self.pe_data[eh_offset + 2] << 8)
                    | (self.pe_data[eh_offset + 3] << 16)
                ) >> 8
                return 4 + data_size  # Header (4) + data

            elif (kind & 0x40) == 0x40:  # EH_FAT_FORMAT
                # Data size is in bytes 1-3 (24-bit value)
                data_size = (
                    self.pe_data[eh_offset + 1]
                    | (self.pe_data[eh_offset + 2] << 8)
                    | (self.pe_data[eh_offset + 3] << 16)
                ) >> 8
                return 4 + data_size  # Header (4) + data

            return 0

        except (IndexError, struct.error):
            return 0

    def _safe_unpack(self, format_str: str, offset: int, default=None):
        """Safely unpack data from PE file with bounds checking."""
        try:
            size = struct.calcsize(format_str)
            if offset + size > len(self.pe_data):
                return default
            return struct.unpack_from(format_str, self.pe_data, offset)[0]
        except (struct.error, IndexError, ValueError):
            return default
