"""
Instruction operand resolution and token handling.

This module provides functionality to resolve instruction operands from tokens
to their actual values (strings, method references, type references, etc.).
"""

from dataclasses import dataclass
from typing import Any

from ..model.module import Module
from ..util.string_utils import clean_string_for_display

__all__ = [
    "ResolvedOperand",
    "OperandResolver",
]


@dataclass(slots=True)
class ResolvedOperand:
    """Represents a resolved instruction operand."""

    raw_value: Any  # Original token or value
    resolved_value: Any  # Resolved actual value
    operand_type: str  # Type description

    def __str__(self) -> str:
        if self.resolved_value is not None:
            return str(self.resolved_value)
        return f"unresolved({self.raw_value})"


class OperandResolver:
    """Resolves instruction operands from tokens to their actual values."""

    def __init__(self, module: "Module"):
        self.module = module
        self.strings_heap = module.strings_heap
        self.user_strings_heap = module.user_strings_heap
        self.blob_heap = module.blob_heap
        self.table_heap = module.table_heap

    def resolve_operand(
        self, operand: Any, operand_type_name: str
    ) -> ResolvedOperand:
        """Resolve an instruction operand based on its type."""
        if operand is None:
            return ResolvedOperand(None, None, "none")

        # Additional validation for operand type
        if not operand_type_name:
            return ResolvedOperand(operand, operand, "unknown")

        # Handle different operand types
        if operand_type_name == "InlineString":
            return self._resolve_string_token(operand)
        elif operand_type_name == "InlineMethod":
            return self._resolve_method_token(operand)
        elif operand_type_name == "InlineField":
            return self._resolve_field_token(operand)
        elif operand_type_name == "InlineType":
            return self._resolve_type_token(operand)
        elif operand_type_name == "InlineTok":
            return self._resolve_generic_token(operand)
        elif operand_type_name in ["InlineI", "InlineI8", "ShortInlineI"]:
            return ResolvedOperand(operand, operand, "integer")
        elif operand_type_name in ["InlineR", "ShortInlineR"]:
            return ResolvedOperand(operand, operand, "float")
        elif operand_type_name in ["InlineBrTarget", "ShortInlineBrTarget"]:
            return ResolvedOperand(
                operand, f"IL_{operand:04x}", "branch_target"
            )
        elif operand_type_name in ["InlineVar", "ShortInlineVar"]:
            return ResolvedOperand(operand, f"V_{operand}", "variable")
        elif operand_type_name == "InlineSwitch":
            if isinstance(operand, list):
                targets = [f"IL_{target:04x}" for target in operand]
                return ResolvedOperand(operand, targets, "switch_targets")
            return ResolvedOperand(operand, operand, "switch")
        else:
            return ResolvedOperand(operand, operand, "unknown")

    def _resolve_string_token(self, token: int) -> ResolvedOperand:
        """Resolve a string token from the user string heap."""
        try:
            if self.user_strings_heap:
                string_index = token & 0x00FFFFFF
                if string_index == 0:
                    return ResolvedOperand(token, '""', "string")

                resolved_string = self.user_strings_heap.get_string(
                    string_index
                )
                if resolved_string is not None:
                    # Use the string cleaning function that preserves readable Unicode
                    cleaned_string = clean_string_for_display(resolved_string)
                    return ResolvedOperand(
                        token, f"{cleaned_string}", "string"
                    )
        except (IndexError, ValueError, AttributeError):
            pass

        return ResolvedOperand(
            token, f"ldstr(0x{token:08x})", "unresolved_string"
        )

    def _resolve_method_token(self, token: int) -> ResolvedOperand:
        """Resolve a method token to method definition or reference."""
        try:
            table_id = (token >> 24) & 0xFF
            rid = token & 0x00FFFFFF

            if rid == 0:
                return ResolvedOperand(
                    token, f"method(0x{token:08x})", "unresolved_method"
                )

            if table_id == 0x06:  # MethodDef table
                if self.table_heap:
                    from .tokens import TokenType

                    max_rid = self.table_heap.get_table_row_count(
                        TokenType.MethodDef
                    )
                    if rid > max_rid:
                        return ResolvedOperand(
                            token,
                            f"method(0x{token:08x})",
                            "unresolved_method",
                        )

                if self.module.types:
                    for type_def in self.module.types:
                        for method in type_def.methods:
                            if method.token.rid == rid:
                                # Return the actual MethodDef object instead of string
                                return ResolvedOperand(
                                    token, method, "method_def"
                                )
            elif table_id == 0x0A:  # MemberRef table
                try:
                    member_ref = self.module.find_member_ref_by_token(token)
                    if member_ref:
                        return ResolvedOperand(token, member_ref, "member_ref")
                except Exception:
                    pass

                return self._resolve_member_ref_token(token)
            # elif table_id == 0x2B:  # MethodSpec table TODO: Implement this
            #    ...
        except (IndexError, ValueError, AttributeError, KeyError):
            pass

        return ResolvedOperand(
            token, f"method(0x{token:08x})", "unresolved_method"
        )

    def _resolve_member_ref_token(self, token: int) -> ResolvedOperand:
        """Resolve a MemberRef token to method or field reference."""
        try:
            from .tokens import TokenType

            rid = token & 0x00FFFFFF

            # Validate table heap and RID
            if not self.table_heap:
                return ResolvedOperand(
                    token, f"memberref(0x{token:08x})", "member_ref"
                )

            if rid == 0 or rid > self.table_heap.get_table_row_count(
                TokenType.MemberRef
            ):
                return ResolvedOperand(
                    token, f"memberref(0x{token:08x})", "member_ref"
                )

            # Get the MemberRef table row data
            row_data = self.table_heap.get_table_data(TokenType.MemberRef, rid)
            if not row_data or len(row_data) == 0:
                return ResolvedOperand(
                    token, f"memberref(0x{token:08x})", "member_ref"
                )

            from ..util.buffers import BinaryReader

            reader = BinaryReader(row_data)

            # Read MemberRef structure (ECMA-335 II.22.25):
            # Class: MemberRefParent coded index
            # Name: String heap index
            # Signature: Blob heap index

            class_value = (
                reader.read_uint32()
                if self._uses_4_byte_coded_index()
                else reader.read_uint16()
            )

            if class_value != 0:
                from .tokens import decode_coded_index, CodedIndexType

                decode_coded_index(CodedIndexType.MemberRefParent, class_value)

            # Read name index
            name_index = (
                reader.read_uint32()
                if self.table_heap.string_index_size == 4
                else reader.read_uint16()
            )

            # Read signature index (not used in basic name resolution)
            _ = (
                reader.read_uint32()
                if self.table_heap.blob_index_size == 4
                else reader.read_uint16()
            )

            # Get the name from string heap with validation
            name = f"name_{name_index}"  # Default fallback
            if self.strings_heap and name_index > 0:
                try:
                    resolved_name = self.strings_heap.get_string(name_index)
                    if resolved_name is not None:
                        name = clean_string_for_display(resolved_name)
                except (IndexError, ValueError):
                    pass  # Keep fallback name

            # Try to resolve the parent class for context
            parent_name = self._resolve_member_ref_parent(class_value)

            if parent_name:
                cleaned_parent_name = clean_string_for_display(parent_name)
                full_name = f"{cleaned_parent_name}::{name}"
            else:
                full_name = name

            return ResolvedOperand(token, full_name, "member_ref")

        except (IndexError, ValueError, AttributeError, KeyError):
            return ResolvedOperand(
                token, f"memberref(0x{token:08x})", "member_ref"
            )

    def _resolve_member_ref_parent(self, coded_index: int) -> str | None:
        """Resolve MemberRefParent coded index to get the parent type name."""
        try:
            from .tokens import CodedIndexType, TokenType, decode_coded_index

            parent_token = decode_coded_index(
                CodedIndexType.MemberRefParent, coded_index
            )

            if parent_token.table == TokenType.TypeRef:
                # Try to resolve TypeRef
                return self._resolve_type_ref_name(parent_token.rid)
            elif parent_token.table == TokenType.TypeDef:
                # Find in our loaded types
                for type_def in self.module.types:
                    if type_def.token.rid == parent_token.rid:
                        return type_def.full_name
            elif parent_token.table == TokenType.ModuleRef:
                # External module reference
                return f"module_{parent_token.rid}"
            elif parent_token.table == TokenType.MethodDef:
                # Method reference (for vararg calls)
                return f"method_{parent_token.rid}"

        except (IndexError, ValueError, AttributeError, KeyError):
            pass

        return None

    def _resolve_type_ref_name(self, rid: int) -> str | None:
        """Resolve TypeRef token to type name."""
        try:
            from .tokens import TokenType

            # Validate inputs
            if not self.table_heap or rid == 0:
                return None

            if rid > self.table_heap.get_table_row_count(TokenType.TypeRef):
                return None

            row_data = self.table_heap.get_table_data(TokenType.TypeRef, rid)
            if not row_data or len(row_data) == 0:
                return None

            from ..util.buffers import BinaryReader

            reader = BinaryReader(row_data)

            # TypeRef structure (ECMA-335 II.22.38):
            # ResolutionScope: ResolutionScope coded index
            # TypeName: String heap index
            # TypeNamespace: String heap index

            # Skip resolution scope
            _ = (
                reader.read_uint32()
                if self._uses_4_byte_coded_index()
                else reader.read_uint16()
            )

            # Read type name
            name_index = (
                reader.read_uint32()
                if self.table_heap.string_index_size == 4
                else reader.read_uint16()
            )

            # Read namespace
            namespace_index = (
                reader.read_uint32()
                if self.table_heap.string_index_size == 4
                else reader.read_uint16()
            )

            # Get type name with validation
            name = f"type_{name_index}"  # Default fallback
            if self.strings_heap and name_index > 0:
                try:
                    resolved_name = self.strings_heap.get_string(name_index)
                    if resolved_name is not None:
                        name = resolved_name
                except (IndexError, ValueError):
                    pass

            # Get namespace with validation
            namespace = ""
            if self.strings_heap and namespace_index > 0:
                try:
                    resolved_namespace = self.strings_heap.get_string(
                        namespace_index
                    )
                    if resolved_namespace is not None:
                        namespace = resolved_namespace
                except (IndexError, ValueError):
                    pass

            if namespace:
                return f"{namespace}.{name}"
            else:
                return name

        except (IndexError, ValueError, AttributeError, KeyError):
            # Handle specific metadata parsing errors
            pass

        return None

    def _uses_4_byte_coded_index(self, coded_index_type=None) -> bool:
        """Determine if coded indices use 4 bytes based on actual table sizes."""
        if not self.table_heap or not hasattr(self.table_heap, "tables"):
            # Fallback to heap size indicators
            return (
                self.table_heap.string_index_size == 4
                or self.table_heap.blob_index_size == 4
            )

        # Calculate based on the largest table that could be referenced
        max_rows = 0

        # Import here to avoid circular imports
        from .tokens import TokenType

        # Get relevant tables for coded index calculation
        relevant_tables = [
            TokenType.TypeDef,
            TokenType.TypeRef,
            TokenType.MemberRef,
            TokenType.MethodDef,
            TokenType.Field,
            TokenType.ModuleRef,
            TokenType.TypeSpec,
        ]

        for table_type in relevant_tables:
            row_count = self.table_heap.get_table_row_count(table_type)
            max_rows = max(max_rows, row_count)

        return max_rows > 0x3FFF

    def _resolve_field_token(self, token: int) -> ResolvedOperand:
        """Resolve a field token to field definition or reference."""
        try:
            table_id = (token >> 24) & 0xFF
            rid = token & 0x00FFFFFF

            # Validate RID
            if rid == 0:
                return ResolvedOperand(
                    token, f"field(0x{token:08x})", "unresolved_field"
                )

            if table_id == 0x04:  # Field table
                # Validate table bounds if table_heap is available
                if self.table_heap:
                    from .tokens import TokenType

                    max_rid = self.table_heap.get_table_row_count(
                        TokenType.Field
                    )
                    if rid > max_rid:
                        return ResolvedOperand(
                            token, f"field(0x{token:08x})", "unresolved_field"
                        )

                if self.module.types:
                    for type_def in self.module.types:
                        for field in type_def.fields:
                            if field.token.rid == rid:
                                # Return the actual FieldDef object instead of string
                                return ResolvedOperand(
                                    token, field, "field_def"
                                )
            elif table_id == 0x0A:  # MemberRef table
                return self._resolve_member_ref_token(token)
        except (IndexError, ValueError, AttributeError, KeyError):
            pass

        return ResolvedOperand(
            token, f"field(0x{token:08x})", "unresolved_field"
        )

    def _resolve_type_token(self, token: int) -> ResolvedOperand:
        """Resolve a type token to type definition or reference."""
        try:
            table_id = (token >> 24) & 0xFF
            rid = token & 0x00FFFFFF

            # Validate RID
            if rid == 0:
                return ResolvedOperand(
                    token, f"type(0x{token:08x})", "unresolved_type"
                )

            if table_id == 0x02:  # TypeDef table
                if self.table_heap:
                    from .tokens import TokenType

                    max_rid = self.table_heap.get_table_row_count(
                        TokenType.TypeDef
                    )
                    if rid > max_rid:
                        return ResolvedOperand(
                            token, f"type(0x{token:08x})", "unresolved_type"
                        )

                if self.module.types:
                    for type_def in self.module.types:
                        if type_def.token.rid == rid:
                            return ResolvedOperand(
                                token, type_def.full_name, "type_def"
                            )
            elif table_id == 0x01:  # TypeRef table
                # Resolve TypeRef using module's resolver
                resolved_name = self.module.resolve_token(token)
                if resolved_name.startswith("0x"):
                    # Fallback if module resolution failed
                    return ResolvedOperand(
                        token, f"typeref(0x{token:08x})", "type_ref"
                    )
                else:
                    return ResolvedOperand(token, resolved_name, "type_ref")
            elif table_id == 0x1B:  # TypeSpec table
                # Resolve TypeSpec - these are complex type signatures
                rid = token & 0x00FFFFFF
                if (
                    self.module.table_heap
                    and self.module.blob_heap
                    and rid > 0
                ):
                    row_data = self.module.table_heap.get_table_data(
                        0x1B, rid
                    )  # TokenType.TypeSpec
                    if row_data:
                        from ..util.buffers import BinaryReader

                        reader = BinaryReader(row_data)

                        # TypeSpec structure (ECMA-335 II.22.39):
                        # Signature (blob index)
                        sig_index = (
                            reader.read_uint32()
                            if self.module.table_heap.blob_index_size == 4
                            else reader.read_uint16()
                        )

                        try:
                            from ..metadata.signatures import SignatureParser

                            parser = SignatureParser(self.module.blob_heap)
                            type_sig = parser.parse_type_spec_sig(sig_index)
                            return ResolvedOperand(
                                token, str(type_sig), "type_spec"
                            )
                        except (
                            IndexError,
                            ValueError,
                            AttributeError,
                            ImportError,
                        ):
                            pass

                return ResolvedOperand(
                    token, f"typespec(0x{token:08x})", "type_spec"
                )
        except (IndexError, ValueError, AttributeError, KeyError):
            pass

        return ResolvedOperand(
            token, f"type(0x{token:08x})", "unresolved_type"
        )

    def _resolve_generic_token(self, token: int) -> ResolvedOperand:
        """Resolve a generic token (could be method, field, or type)."""
        table_id = (token >> 24) & 0xFF

        # Determine token type and delegate to appropriate resolver
        if table_id in [0x06, 0x0A, 0x2B]:  # Method tokens
            return self._resolve_method_token(token)
        elif table_id in [0x04]:  # Field tokens
            return self._resolve_field_token(token)
        elif table_id in [0x01, 0x02, 0x1B]:  # Type tokens
            return self._resolve_type_token(token)
        else:
            return ResolvedOperand(
                token, f"token(0x{token:08x})", "generic_token"
            )


class InstructionFormatter:
    """Formats instructions with resolved operands for display."""

    def __init__(self, resolver: OperandResolver):
        self.resolver = resolver

    def format_instruction(self, instruction) -> str:
        """Format an instruction with resolved operands."""
        from .il import Instruction

        if not isinstance(instruction, Instruction):
            return str(instruction)

        if instruction.operand is None:
            return f"IL_{instruction.offset:04x}: {instruction.opcode.name}"

        resolved = self.resolver.resolve_operand(
            instruction.operand, instruction.opcode.operand_type.name
        )

        return f"IL_{instruction.offset:04x}: {instruction.opcode.name} {resolved}"

    def format_method_body(self, body) -> list[str]:
        """Format all instructions in a method body."""
        from .il import CilBody

        if not isinstance(body, CilBody):
            return []

        formatted_instructions = []
        for instruction in body.instructions:
            formatted = self.format_instruction(instruction)
            formatted_instructions.append(formatted)

        return formatted_instructions


def format_instruction_with_context(instruction, module) -> str:
    """Convenience function to format a single instruction with resolved operands."""
    formatter = InstructionFormatter(module.operand_resolver)
    return formatter.format_instruction(instruction)


def format_method_body_with_context(body, module) -> list[str]:
    """Convenience function to format all instructions in a method body with resolved operands."""
    formatter = InstructionFormatter(module.operand_resolver)
    return formatter.format_method_body(body)
