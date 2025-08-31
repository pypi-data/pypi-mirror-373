"""
Complete CIL OpCode implementation based on ECMA-335.

This module provides all ~220 CIL opcodes with their metadata including
operand types, stack behavior, and flow control information.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

__all__ = [
    "OperandType",
    "FlowControl", 
    "OpCodeType",
    "StackBehaviour",
    "OpCode",
    "OpCodes",
]


class OperandType(IntEnum):
    """CIL instruction operand types (ECMA-335 II.23.1.17)."""

    InlineBrTarget = 0  # 4-byte signed branch target
    InlineField = 1  # 4-byte field token
    InlineI = 2  # 4-byte signed integer
    InlineI8 = 3  # 8-byte signed integer
    InlineMethod = 4  # 4-byte method token
    InlineNone = 5  # No operand
    InlineR = 6  # 8-byte floating point
    InlineSig = 7  # 4-byte signature token
    InlineString = 8  # 4-byte string token
    InlineSwitch = 9  # Variable length switch table
    InlineTok = 10  # 4-byte arbitrary metadata token
    InlineType = 11  # 4-byte type token
    InlineVar = 12  # 2-byte local variable index
    ShortInlineBrTarget = 13  # 1-byte signed branch target
    ShortInlineI = 14  # 1-byte signed integer
    ShortInlineR = 15  # 4-byte floating point
    ShortInlineVar = 16  # 1-byte local variable index


class FlowControl(IntEnum):
    """Flow control behavior (ECMA-335 II.23.1.7.3)."""

    Branch = 0  # Unconditional branch
    Break = 1  # Break to debugger
    Call = 2  # Method call
    Cond_Branch = 3  # Conditional branch
    Meta = 4  # Provides metadata (e.g. ldtoken)
    Next = 5  # Falls through to next instruction
    Phi = 6  # Used in SSA form
    Return = 7  # Returns from method
    Throw = 8  # Throws exception


class OpCodeType(IntEnum):
    """OpCode type classification (ECMA-335 II.23.1.17)."""

    Annotation = 0  # Reserved for internal use
    Macro = 1  # Provided for convenience
    Nternal = 2  # Reserved for internal use
    Objmodel = 3  # Object model instruction
    Prefix = 4  # Instruction prefix
    Primitive = 5  # Primitive operation


class StackBehaviour(IntEnum):
    """Stack behavior patterns (ECMA-335 II.23.1.17)."""

    Pop0 = 0  # No items popped
    Pop1 = 1  # One item popped
    Pop1_pop1 = 2  # Two items popped
    Popi = 3  # Pop integer
    Popi_pop1 = 4  # Pop integer and one more
    Popi_popi = 5  # Pop two integers
    Popi_popi8 = 6  # Pop integer and int64
    Popi_popr4 = 7  # Pop integer and float32
    Popi_popr8 = 8  # Pop integer and float64
    Popref = 9  # Pop object reference
    Popref_pop1 = 10  # Pop reference and one more
    Popref_popi = 11  # Pop reference and integer
    Popref_popi_popi = 12  # Pop reference and two integers
    Popref_popi_popi8 = 13  # Pop reference, integer, and int64
    Popref_popi_popr4 = 14  # Pop reference, integer, and float32
    Popref_popi_popr8 = 15  # Pop reference, integer, and float64
    Popref_popi_popref = 16  # Pop reference, integer, and another reference
    Varpop = 17  # Variable number popped
    Push0 = 18  # No items pushed
    Push1 = 19  # One item pushed
    Push1_push1 = 20  # Two items pushed
    Pushi = 21  # Push integer
    Pushi8 = 22  # Push int64
    Pushr4 = 23  # Push float32
    Pushr8 = 24  # Push float64
    Pushref = 25  # Push object reference
    Varpush = 26  # Variable number pushed


@dataclass(frozen=True, slots=True)
class OpCode:
    """Represents a CIL opcode with all metadata."""

    name: str
    value: int  # 1 or 2-byte opcode value
    size: int  # Size in bytes (1 or 2)
    operand_type: OperandType
    flow_control: FlowControl
    opcode_type: OpCodeType
    stack_pop: StackBehaviour
    stack_push: StackBehaviour

    @property
    def is_prefix(self) -> bool:
        """Check if this is a prefix instruction."""
        return self.opcode_type == OpCodeType.Prefix

    @property
    def has_operand(self) -> bool:
        """Check if instruction has an operand."""
        return self.operand_type != OperandType.InlineNone


class Code(IntEnum):
    """CIL instruction codes (ECMA-335)."""

    # Single-byte opcodes (0x00-0xFF)
    Nop = 0x00
    Break = 0x01
    Ldarg_0 = 0x02
    Ldarg_1 = 0x03
    Ldarg_2 = 0x04
    Ldarg_3 = 0x05
    Ldloc_0 = 0x06
    Ldloc_1 = 0x07
    Ldloc_2 = 0x08
    Ldloc_3 = 0x09
    Stloc_0 = 0x0A
    Stloc_1 = 0x0B
    Stloc_2 = 0x0C
    Stloc_3 = 0x0D
    Ldarg_S = 0x0E
    Ldarga_S = 0x0F
    Starg_S = 0x10
    Ldloc_S = 0x11
    Ldloca_S = 0x12
    Stloc_S = 0x13
    Ldnull = 0x14
    Ldc_I4_M1 = 0x15
    Ldc_I4_0 = 0x16
    Ldc_I4_1 = 0x17
    Ldc_I4_2 = 0x18
    Ldc_I4_3 = 0x19
    Ldc_I4_4 = 0x1A
    Ldc_I4_5 = 0x1B
    Ldc_I4_6 = 0x1C
    Ldc_I4_7 = 0x1D
    Ldc_I4_8 = 0x1E
    Ldc_I4_S = 0x1F
    Ldc_I4 = 0x20
    Ldc_I8 = 0x21
    Ldc_R4 = 0x22
    Ldc_R8 = 0x23
    Dup = 0x25
    Pop = 0x26
    Jmp = 0x27
    Call = 0x28
    Calli = 0x29
    Ret = 0x2A
    Br_S = 0x2B
    Brfalse_S = 0x2C
    Brtrue_S = 0x2D
    Beq_S = 0x2E
    Bge_S = 0x2F
    Bgt_S = 0x30
    Ble_S = 0x31
    Blt_S = 0x32
    Bne_Un_S = 0x33
    Bge_Un_S = 0x34
    Bgt_Un_S = 0x35
    Ble_Un_S = 0x36
    Blt_Un_S = 0x37
    Br = 0x38
    Brfalse = 0x39
    Brtrue = 0x3A
    Beq = 0x3B
    Bge = 0x3C
    Bgt = 0x3D
    Ble = 0x3E
    Blt = 0x3F
    Bne_Un = 0x40
    Bge_Un = 0x41
    Bgt_Un = 0x42
    Ble_Un = 0x43
    Blt_Un = 0x44
    Switch = 0x45
    Ldind_I1 = 0x46
    Ldind_U1 = 0x47
    Ldind_I2 = 0x48
    Ldind_U2 = 0x49
    Ldind_I4 = 0x4A
    Ldind_U4 = 0x4B
    Ldind_I8 = 0x4C
    Ldind_I = 0x4D
    Ldind_R4 = 0x4E
    Ldind_R8 = 0x4F
    Ldind_Ref = 0x50
    Stind_Ref = 0x51
    Stind_I1 = 0x52
    Stind_I2 = 0x53
    Stind_I4 = 0x54
    Stind_I8 = 0x55
    Stind_R4 = 0x56
    Stind_R8 = 0x57
    Add = 0x58
    Sub = 0x59
    Mul = 0x5A
    Div = 0x5B
    Div_Un = 0x5C
    Rem = 0x5D
    Rem_Un = 0x5E
    And = 0x5F
    Or = 0x60
    Xor = 0x61
    Shl = 0x62
    Shr = 0x63
    Shr_Un = 0x64
    Neg = 0x65
    Not = 0x66
    Conv_I1 = 0x67
    Conv_I2 = 0x68
    Conv_I4 = 0x69
    Conv_I8 = 0x6A
    Conv_R4 = 0x6B
    Conv_R8 = 0x6C
    Conv_U4 = 0x6D
    Conv_U8 = 0x6E
    Callvirt = 0x6F
    Cpobj = 0x70
    Ldobj = 0x71
    Ldstr = 0x72
    Newobj = 0x73
    Castclass = 0x74
    Isinst = 0x75
    Conv_R_Un = 0x76
    Unbox = 0x79
    Throw = 0x7A
    Ldfld = 0x7B
    Ldflda = 0x7C
    Stfld = 0x7D
    Ldsfld = 0x7E
    Ldsflda = 0x7F
    Stsfld = 0x80
    Stobj = 0x81
    Conv_Ovf_I1_Un = 0x82
    Conv_Ovf_I2_Un = 0x83
    Conv_Ovf_I4_Un = 0x84
    Conv_Ovf_I8_Un = 0x85
    Conv_Ovf_U1_Un = 0x86
    Conv_Ovf_U2_Un = 0x87
    Conv_Ovf_U4_Un = 0x88
    Conv_Ovf_U8_Un = 0x89
    Conv_Ovf_I_Un = 0x8A
    Conv_Ovf_U_Un = 0x8B
    Box = 0x8C
    Newarr = 0x8D
    Ldlen = 0x8E
    Ldelema = 0x8F
    Ldelem_I1 = 0x90
    Ldelem_U1 = 0x91
    Ldelem_I2 = 0x92
    Ldelem_U2 = 0x93
    Ldelem_I4 = 0x94
    Ldelem_U4 = 0x95
    Ldelem_I8 = 0x96
    Ldelem_I = 0x97
    Ldelem_R4 = 0x98
    Ldelem_R8 = 0x99
    Ldelem_Ref = 0x9A
    Stelem_I = 0x9B
    Stelem_I1 = 0x9C
    Stelem_I2 = 0x9D
    Stelem_I4 = 0x9E
    Stelem_I8 = 0x9F
    Stelem_R4 = 0xA0
    Stelem_R8 = 0xA1
    Stelem_Ref = 0xA2
    Ldelem = 0xA3
    Stelem = 0xA4
    Unbox_Any = 0xA5
    Conv_Ovf_I1 = 0xB3
    Conv_Ovf_U1 = 0xB4
    Conv_Ovf_I2 = 0xB5
    Conv_Ovf_U2 = 0xB6
    Conv_Ovf_I4 = 0xB7
    Conv_Ovf_U4 = 0xB8
    Conv_Ovf_I8 = 0xB9
    Conv_Ovf_U8 = 0xBA
    Refanyval = 0xC2
    Ckfinite = 0xC3
    Mkrefany = 0xC6
    Ldtoken = 0xD0
    Conv_U2 = 0xD1
    Conv_U1 = 0xD2
    Conv_I = 0xD3
    Conv_Ovf_I = 0xD4
    Conv_Ovf_U = 0xD5
    Add_Ovf = 0xD6
    Add_Ovf_Un = 0xD7
    Mul_Ovf = 0xD8
    Mul_Ovf_Un = 0xD9
    Sub_Ovf = 0xDA
    Sub_Ovf_Un = 0xDB
    Endfinally = 0xDC
    Leave = 0xDD
    Leave_S = 0xDE
    Stind_I = 0xDF
    Conv_U = 0xE0

    # Two-byte opcodes (0xFE prefixed)
    Arglist = 0xFE00
    Ceq = 0xFE01
    Cgt = 0xFE02
    Cgt_Un = 0xFE03
    Clt = 0xFE04
    Clt_Un = 0xFE05
    Ldftn = 0xFE06
    Ldvirtftn = 0xFE07
    Ldarg = 0xFE09
    Ldarga = 0xFE0A
    Starg = 0xFE0B
    Ldloc = 0xFE0C
    Ldloca = 0xFE0D
    Stloc = 0xFE0E
    Localloc = 0xFE0F
    Endfilter = 0xFE11
    Unaligned = 0xFE12
    Volatile = 0xFE13
    Tail = 0xFE14
    Initobj = 0xFE15
    Constrained = 0xFE16
    Cpblk = 0xFE17
    Initblk = 0xFE18
    No = 0xFE19
    Rethrow = 0xFE1A
    Sizeof = 0xFE1C
    Refanytype = 0xFE1D
    Readonly = 0xFE1E


# Complete OpCode definitions based on ECMA-335
class OpCodes:
    """All CIL opcodes with complete metadata."""

    # Single-byte opcodes
    Nop = OpCode(
        "nop",
        Code.Nop,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Break = OpCode(
        "break",
        Code.Break,
        1,
        OperandType.InlineNone,
        FlowControl.Break,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Ldarg_0 = OpCode(
        "ldarg.0",
        Code.Ldarg_0,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldarg_1 = OpCode(
        "ldarg.1",
        Code.Ldarg_1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldarg_2 = OpCode(
        "ldarg.2",
        Code.Ldarg_2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldarg_3 = OpCode(
        "ldarg.3",
        Code.Ldarg_3,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldloc_0 = OpCode(
        "ldloc.0",
        Code.Ldloc_0,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldloc_1 = OpCode(
        "ldloc.1",
        Code.Ldloc_1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldloc_2 = OpCode(
        "ldloc.2",
        Code.Ldloc_2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldloc_3 = OpCode(
        "ldloc.3",
        Code.Ldloc_3,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Stloc_0 = OpCode(
        "stloc.0",
        Code.Stloc_0,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Stloc_1 = OpCode(
        "stloc.1",
        Code.Stloc_1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Stloc_2 = OpCode(
        "stloc.2",
        Code.Stloc_2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Stloc_3 = OpCode(
        "stloc.3",
        Code.Stloc_3,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Ldarg_S = OpCode(
        "ldarg.s",
        Code.Ldarg_S,
        1,
        OperandType.ShortInlineVar,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldarga_S = OpCode(
        "ldarga.s",
        Code.Ldarga_S,
        1,
        OperandType.ShortInlineVar,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Starg_S = OpCode(
        "starg.s",
        Code.Starg_S,
        1,
        OperandType.ShortInlineVar,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Ldloc_S = OpCode(
        "ldloc.s",
        Code.Ldloc_S,
        1,
        OperandType.ShortInlineVar,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldloca_S = OpCode(
        "ldloca.s",
        Code.Ldloca_S,
        1,
        OperandType.ShortInlineVar,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Stloc_S = OpCode(
        "stloc.s",
        Code.Stloc_S,
        1,
        OperandType.ShortInlineVar,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Ldnull = OpCode(
        "ldnull",
        Code.Ldnull,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushref,
    )
    Ldc_I4_M1 = OpCode(
        "ldc.i4.m1",
        Code.Ldc_I4_M1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_0 = OpCode(
        "ldc.i4.0",
        Code.Ldc_I4_0,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_1 = OpCode(
        "ldc.i4.1",
        Code.Ldc_I4_1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_2 = OpCode(
        "ldc.i4.2",
        Code.Ldc_I4_2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_3 = OpCode(
        "ldc.i4.3",
        Code.Ldc_I4_3,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_4 = OpCode(
        "ldc.i4.4",
        Code.Ldc_I4_4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_5 = OpCode(
        "ldc.i4.5",
        Code.Ldc_I4_5,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_6 = OpCode(
        "ldc.i4.6",
        Code.Ldc_I4_6,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_7 = OpCode(
        "ldc.i4.7",
        Code.Ldc_I4_7,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_8 = OpCode(
        "ldc.i4.8",
        Code.Ldc_I4_8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4_S = OpCode(
        "ldc.i4.s",
        Code.Ldc_I4_S,
        1,
        OperandType.ShortInlineI,
        FlowControl.Next,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I4 = OpCode(
        "ldc.i4",
        Code.Ldc_I4,
        1,
        OperandType.InlineI,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldc_I8 = OpCode(
        "ldc.i8",
        Code.Ldc_I8,
        1,
        OperandType.InlineI8,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi8,
    )
    Ldc_R4 = OpCode(
        "ldc.r4",
        Code.Ldc_R4,
        1,
        OperandType.ShortInlineR,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushr4,
    )
    Ldc_R8 = OpCode(
        "ldc.r8",
        Code.Ldc_R8,
        1,
        OperandType.InlineR,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushr8,
    )
    Dup = OpCode(
        "dup",
        Code.Dup,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Push1_push1,
    )
    Pop = OpCode(
        "pop",
        Code.Pop,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Jmp = OpCode(
        "jmp",
        Code.Jmp,
        1,
        OperandType.InlineMethod,
        FlowControl.Call,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Call = OpCode(
        "call",
        Code.Call,
        1,
        OperandType.InlineMethod,
        FlowControl.Call,
        OpCodeType.Primitive,
        StackBehaviour.Varpop,
        StackBehaviour.Varpush,
    )
    Calli = OpCode(
        "calli",
        Code.Calli,
        1,
        OperandType.InlineSig,
        FlowControl.Call,
        OpCodeType.Primitive,
        StackBehaviour.Varpop,
        StackBehaviour.Varpush,
    )
    Ret = OpCode(
        "ret",
        Code.Ret,
        1,
        OperandType.InlineNone,
        FlowControl.Return,
        OpCodeType.Primitive,
        StackBehaviour.Varpop,
        StackBehaviour.Push0,
    )
    Br_S = OpCode(
        "br.s",
        Code.Br_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Brfalse_S = OpCode(
        "brfalse.s",
        Code.Brfalse_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Popi,
        StackBehaviour.Push0,
    )
    Brtrue_S = OpCode(
        "brtrue.s",
        Code.Brtrue_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Popi,
        StackBehaviour.Push0,
    )
    Beq_S = OpCode(
        "beq.s",
        Code.Beq_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bge_S = OpCode(
        "bge.s",
        Code.Bge_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bgt_S = OpCode(
        "bgt.s",
        Code.Bgt_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Ble_S = OpCode(
        "ble.s",
        Code.Ble_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Blt_S = OpCode(
        "blt.s",
        Code.Blt_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bne_Un_S = OpCode(
        "bne.un.s",
        Code.Bne_Un_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bge_Un_S = OpCode(
        "bge.un.s",
        Code.Bge_Un_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bgt_Un_S = OpCode(
        "bgt.un.s",
        Code.Bgt_Un_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Ble_Un_S = OpCode(
        "ble.un.s",
        Code.Ble_Un_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Blt_Un_S = OpCode(
        "blt.un.s",
        Code.Blt_Un_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Br = OpCode(
        "br",
        Code.Br,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Branch,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Brfalse = OpCode(
        "brfalse",
        Code.Brfalse,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Push0,
    )
    Brtrue = OpCode(
        "brtrue",
        Code.Brtrue,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Push0,
    )
    Beq = OpCode(
        "beq",
        Code.Beq,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bge = OpCode(
        "bge",
        Code.Bge,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bgt = OpCode(
        "bgt",
        Code.Bgt,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Ble = OpCode(
        "ble",
        Code.Ble,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Blt = OpCode(
        "blt",
        Code.Blt,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bne_Un = OpCode(
        "bne.un",
        Code.Bne_Un,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bge_Un = OpCode(
        "bge.un",
        Code.Bge_Un,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Bgt_Un = OpCode(
        "bgt.un",
        Code.Bgt_Un,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Ble_Un = OpCode(
        "ble.un",
        Code.Ble_Un,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Blt_Un = OpCode(
        "blt.un",
        Code.Blt_Un,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Cond_Branch,
        OpCodeType.Macro,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push0,
    )
    Switch = OpCode(
        "switch",
        Code.Switch,
        1,
        OperandType.InlineSwitch,
        FlowControl.Cond_Branch,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Push0,
    )
    Ldind_I1 = OpCode(
        "ldind.i1",
        Code.Ldind_I1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Ldind_U1 = OpCode(
        "ldind.u1",
        Code.Ldind_U1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Ldind_I2 = OpCode(
        "ldind.i2",
        Code.Ldind_I2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Ldind_U2 = OpCode(
        "ldind.u2",
        Code.Ldind_U2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Ldind_I4 = OpCode(
        "ldind.i4",
        Code.Ldind_I4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Ldind_U4 = OpCode(
        "ldind.u4",
        Code.Ldind_U4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Ldind_I8 = OpCode(
        "ldind.i8",
        Code.Ldind_I8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi8,
    )
    Ldind_I = OpCode(
        "ldind.i",
        Code.Ldind_I,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Ldind_R4 = OpCode(
        "ldind.r4",
        Code.Ldind_R4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushr4,
    )
    Ldind_R8 = OpCode(
        "ldind.r8",
        Code.Ldind_R8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushr8,
    )
    Ldind_Ref = OpCode(
        "ldind.ref",
        Code.Ldind_Ref,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushref,
    )
    Stind_Ref = OpCode(
        "stind.ref",
        Code.Stind_Ref,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_pop1,
        StackBehaviour.Push0,
    )
    Stind_I1 = OpCode(
        "stind.i1",
        Code.Stind_I1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_popi,
        StackBehaviour.Push0,
    )
    Stind_I2 = OpCode(
        "stind.i2",
        Code.Stind_I2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_popi,
        StackBehaviour.Push0,
    )
    Stind_I4 = OpCode(
        "stind.i4",
        Code.Stind_I4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_popi,
        StackBehaviour.Push0,
    )
    Stind_I8 = OpCode(
        "stind.i8",
        Code.Stind_I8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_popi8,
        StackBehaviour.Push0,
    )
    Stind_R4 = OpCode(
        "stind.r4",
        Code.Stind_R4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_popr4,
        StackBehaviour.Push0,
    )
    Stind_R8 = OpCode(
        "stind.r8",
        Code.Stind_R8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_popr8,
        StackBehaviour.Push0,
    )
    Add = OpCode(
        "add",
        Code.Add,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Sub = OpCode(
        "sub",
        Code.Sub,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Mul = OpCode(
        "mul",
        Code.Mul,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Div = OpCode(
        "div",
        Code.Div,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Div_Un = OpCode(
        "div.un",
        Code.Div_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Rem = OpCode(
        "rem",
        Code.Rem,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Rem_Un = OpCode(
        "rem.un",
        Code.Rem_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    And = OpCode(
        "and",
        Code.And,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Or = OpCode(
        "or",
        Code.Or,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Xor = OpCode(
        "xor",
        Code.Xor,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Shl = OpCode(
        "shl",
        Code.Shl,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Shr = OpCode(
        "shr",
        Code.Shr,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Shr_Un = OpCode(
        "shr.un",
        Code.Shr_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Neg = OpCode(
        "neg",
        Code.Neg,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Push1,
    )
    Not = OpCode(
        "not",
        Code.Not,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Push1,
    )
    Conv_I1 = OpCode(
        "conv.i1",
        Code.Conv_I1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_I2 = OpCode(
        "conv.i2",
        Code.Conv_I2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_I4 = OpCode(
        "conv.i4",
        Code.Conv_I4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_I8 = OpCode(
        "conv.i8",
        Code.Conv_I8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi8,
    )
    Conv_R4 = OpCode(
        "conv.r4",
        Code.Conv_R4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushr4,
    )
    Conv_R8 = OpCode(
        "conv.r8",
        Code.Conv_R8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushr8,
    )
    Conv_U4 = OpCode(
        "conv.u4",
        Code.Conv_U4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_U8 = OpCode(
        "conv.u8",
        Code.Conv_U8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi8,
    )
    Callvirt = OpCode(
        "callvirt",
        Code.Callvirt,
        1,
        OperandType.InlineMethod,
        FlowControl.Call,
        OpCodeType.Objmodel,
        StackBehaviour.Varpop,
        StackBehaviour.Varpush,
    )
    Cpobj = OpCode(
        "cpobj",
        Code.Cpobj,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popi_popi,
        StackBehaviour.Push0,
    )
    Ldobj = OpCode(
        "ldobj",
        Code.Ldobj,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popi,
        StackBehaviour.Push1,
    )
    Ldstr = OpCode(
        "ldstr",
        Code.Ldstr,
        1,
        OperandType.InlineString,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Pop0,
        StackBehaviour.Pushref,
    )
    Newobj = OpCode(
        "newobj",
        Code.Newobj,
        1,
        OperandType.InlineMethod,
        FlowControl.Call,
        OpCodeType.Objmodel,
        StackBehaviour.Varpop,
        StackBehaviour.Pushref,
    )
    Castclass = OpCode(
        "castclass",
        Code.Castclass,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref,
        StackBehaviour.Pushref,
    )
    Isinst = OpCode(
        "isinst",
        Code.Isinst,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref,
        StackBehaviour.Pushref,
    )
    Conv_R_Un = OpCode(
        "conv.r.un",
        Code.Conv_R_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushr8,
    )
    Unbox = OpCode(
        "unbox",
        Code.Unbox,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popref,
        StackBehaviour.Pushi,
    )
    Throw = OpCode(
        "throw",
        Code.Throw,
        1,
        OperandType.InlineNone,
        FlowControl.Throw,
        OpCodeType.Objmodel,
        StackBehaviour.Popref,
        StackBehaviour.Push0,
    )
    Ldfld = OpCode(
        "ldfld",
        Code.Ldfld,
        1,
        OperandType.InlineField,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref,
        StackBehaviour.Push1,
    )
    Ldflda = OpCode(
        "ldflda",
        Code.Ldflda,
        1,
        OperandType.InlineField,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref,
        StackBehaviour.Pushi,
    )
    Stfld = OpCode(
        "stfld",
        Code.Stfld,
        1,
        OperandType.InlineField,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_pop1,
        StackBehaviour.Push0,
    )
    Ldsfld = OpCode(
        "ldsfld",
        Code.Ldsfld,
        1,
        OperandType.InlineField,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldsflda = OpCode(
        "ldsflda",
        Code.Ldsflda,
        1,
        OperandType.InlineField,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Stsfld = OpCode(
        "stsfld",
        Code.Stsfld,
        1,
        OperandType.InlineField,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Stobj = OpCode(
        "stobj",
        Code.Stobj,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_pop1,
        StackBehaviour.Push0,
    )
    Conv_Ovf_I1_Un = OpCode(
        "conv.ovf.i1.un",
        Code.Conv_Ovf_I1_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_I2_Un = OpCode(
        "conv.ovf.i2.un",
        Code.Conv_Ovf_I2_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_I4_Un = OpCode(
        "conv.ovf.i4.un",
        Code.Conv_Ovf_I4_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_I8_Un = OpCode(
        "conv.ovf.i8.un",
        Code.Conv_Ovf_I8_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi8,
    )
    Conv_Ovf_U1_Un = OpCode(
        "conv.ovf.u1.un",
        Code.Conv_Ovf_U1_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U2_Un = OpCode(
        "conv.ovf.u2.un",
        Code.Conv_Ovf_U2_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U4_Un = OpCode(
        "conv.ovf.u4.un",
        Code.Conv_Ovf_U4_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U8_Un = OpCode(
        "conv.ovf.u8.un",
        Code.Conv_Ovf_U8_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi8,
    )
    Conv_Ovf_I_Un = OpCode(
        "conv.ovf.i.un",
        Code.Conv_Ovf_I_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U_Un = OpCode(
        "conv.ovf.u.un",
        Code.Conv_Ovf_U_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Box = OpCode(
        "box",
        Code.Box,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushref,
    )
    Newarr = OpCode(
        "newarr",
        Code.Newarr,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popi,
        StackBehaviour.Pushref,
    )
    Ldlen = OpCode(
        "ldlen",
        Code.Ldlen,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref,
        StackBehaviour.Pushi,
    )
    Ldelema = OpCode(
        "ldelema",
        Code.Ldelema,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_I1 = OpCode(
        "ldelem.i1",
        Code.Ldelem_I1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_U1 = OpCode(
        "ldelem.u1",
        Code.Ldelem_U1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_I2 = OpCode(
        "ldelem.i2",
        Code.Ldelem_I2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_U2 = OpCode(
        "ldelem.u2",
        Code.Ldelem_U2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_I4 = OpCode(
        "ldelem.i4",
        Code.Ldelem_I4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_U4 = OpCode(
        "ldelem.u4",
        Code.Ldelem_U4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_I8 = OpCode(
        "ldelem.i8",
        Code.Ldelem_I8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi8,
    )
    Ldelem_I = OpCode(
        "ldelem.i",
        Code.Ldelem_I,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushi,
    )
    Ldelem_R4 = OpCode(
        "ldelem.r4",
        Code.Ldelem_R4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushr4,
    )
    Ldelem_R8 = OpCode(
        "ldelem.r8",
        Code.Ldelem_R8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushr8,
    )
    Ldelem_Ref = OpCode(
        "ldelem.ref",
        Code.Ldelem_Ref,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Pushref,
    )
    Stelem_I = OpCode(
        "stelem.i",
        Code.Stelem_I,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popi,
        StackBehaviour.Push0,
    )
    Stelem_I1 = OpCode(
        "stelem.i1",
        Code.Stelem_I1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popi,
        StackBehaviour.Push0,
    )
    Stelem_I2 = OpCode(
        "stelem.i2",
        Code.Stelem_I2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popi,
        StackBehaviour.Push0,
    )
    Stelem_I4 = OpCode(
        "stelem.i4",
        Code.Stelem_I4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popi,
        StackBehaviour.Push0,
    )
    Stelem_I8 = OpCode(
        "stelem.i8",
        Code.Stelem_I8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popi8,
        StackBehaviour.Push0,
    )
    Stelem_R4 = OpCode(
        "stelem.r4",
        Code.Stelem_R4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popr4,
        StackBehaviour.Push0,
    )
    Stelem_R8 = OpCode(
        "stelem.r8",
        Code.Stelem_R8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popr8,
        StackBehaviour.Push0,
    )
    Stelem_Ref = OpCode(
        "stelem.ref",
        Code.Stelem_Ref,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popref,
        StackBehaviour.Push0,
    )
    Ldelem = OpCode(
        "ldelem",
        Code.Ldelem,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi,
        StackBehaviour.Push1,
    )
    Stelem = OpCode(
        "stelem",
        Code.Stelem,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref_popi_popi,
        StackBehaviour.Push0,
    )
    Unbox_Any = OpCode(
        "unbox.any",
        Code.Unbox_Any,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popref,
        StackBehaviour.Push1,
    )
    Conv_Ovf_I1 = OpCode(
        "conv.ovf.i1",
        Code.Conv_Ovf_I1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U1 = OpCode(
        "conv.ovf.u1",
        Code.Conv_Ovf_U1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_I2 = OpCode(
        "conv.ovf.i2",
        Code.Conv_Ovf_I2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U2 = OpCode(
        "conv.ovf.u2",
        Code.Conv_Ovf_U2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_I4 = OpCode(
        "conv.ovf.i4",
        Code.Conv_Ovf_I4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U4 = OpCode(
        "conv.ovf.u4",
        Code.Conv_Ovf_U4,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_I8 = OpCode(
        "conv.ovf.i8",
        Code.Conv_Ovf_I8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi8,
    )
    Conv_Ovf_U8 = OpCode(
        "conv.ovf.u8",
        Code.Conv_Ovf_U8,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi8,
    )
    Refanyval = OpCode(
        "refanyval",
        Code.Refanyval,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Ckfinite = OpCode(
        "ckfinite",
        Code.Ckfinite,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushr8,
    )
    Mkrefany = OpCode(
        "mkrefany",
        Code.Mkrefany,
        1,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Push1,
    )
    Ldtoken = OpCode(
        "ldtoken",
        Code.Ldtoken,
        1,
        OperandType.InlineTok,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Conv_U2 = OpCode(
        "conv.u2",
        Code.Conv_U2,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_U1 = OpCode(
        "conv.u1",
        Code.Conv_U1,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_I = OpCode(
        "conv.i",
        Code.Conv_I,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_I = OpCode(
        "conv.ovf.i",
        Code.Conv_Ovf_I,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Conv_Ovf_U = OpCode(
        "conv.ovf.u",
        Code.Conv_Ovf_U,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Add_Ovf = OpCode(
        "add.ovf",
        Code.Add_Ovf,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Add_Ovf_Un = OpCode(
        "add.ovf.un",
        Code.Add_Ovf_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Mul_Ovf = OpCode(
        "mul.ovf",
        Code.Mul_Ovf,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Mul_Ovf_Un = OpCode(
        "mul.ovf.un",
        Code.Mul_Ovf_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Sub_Ovf = OpCode(
        "sub.ovf",
        Code.Sub_Ovf,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Sub_Ovf_Un = OpCode(
        "sub.ovf.un",
        Code.Sub_Ovf_Un,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Push1,
    )
    Endfinally = OpCode(
        "endfinally",
        Code.Endfinally,
        1,
        OperandType.InlineNone,
        FlowControl.Return,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Leave = OpCode(
        "leave",
        Code.Leave,
        1,
        OperandType.InlineBrTarget,
        FlowControl.Branch,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Leave_S = OpCode(
        "leave.s",
        Code.Leave_S,
        1,
        OperandType.ShortInlineBrTarget,
        FlowControl.Branch,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Stind_I = OpCode(
        "stind.i",
        Code.Stind_I,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi_popi,
        StackBehaviour.Push0,
    )
    Conv_U = OpCode(
        "conv.u",
        Code.Conv_U,
        1,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )

    # Two-byte opcodes (0xFE prefix)
    Arglist = OpCode(
        "arglist",
        Code.Arglist,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ceq = OpCode(
        "ceq",
        Code.Ceq,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Pushi,
    )
    Cgt = OpCode(
        "cgt",
        Code.Cgt,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Pushi,
    )
    Cgt_Un = OpCode(
        "cgt.un",
        Code.Cgt_Un,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Pushi,
    )
    Clt = OpCode(
        "clt",
        Code.Clt,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Pushi,
    )
    Clt_Un = OpCode(
        "clt.un",
        Code.Clt_Un,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1_pop1,
        StackBehaviour.Pushi,
    )
    Ldftn = OpCode(
        "ldftn",
        Code.Ldftn,
        2,
        OperandType.InlineMethod,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Ldvirtftn = OpCode(
        "ldvirtftn",
        Code.Ldvirtftn,
        2,
        OperandType.InlineMethod,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popref,
        StackBehaviour.Pushi,
    )
    Ldarg = OpCode(
        "ldarg",
        Code.Ldarg,
        2,
        OperandType.InlineVar,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldarga = OpCode(
        "ldarga",
        Code.Ldarga,
        2,
        OperandType.InlineVar,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Starg = OpCode(
        "starg",
        Code.Starg,
        2,
        OperandType.InlineVar,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Ldloc = OpCode(
        "ldloc",
        Code.Ldloc,
        2,
        OperandType.InlineVar,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Push1,
    )
    Ldloca = OpCode(
        "ldloca",
        Code.Ldloca,
        2,
        OperandType.InlineVar,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Stloc = OpCode(
        "stloc",
        Code.Stloc,
        2,
        OperandType.InlineVar,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Push0,
    )
    Localloc = OpCode(
        "localloc",
        Code.Localloc,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Pushi,
    )
    Endfilter = OpCode(
        "endfilter",
        Code.Endfilter,
        2,
        OperandType.InlineNone,
        FlowControl.Return,
        OpCodeType.Primitive,
        StackBehaviour.Popi,
        StackBehaviour.Push0,
    )
    Unaligned = OpCode(
        "unaligned.",
        Code.Unaligned,
        2,
        OperandType.ShortInlineI,
        FlowControl.Meta,
        OpCodeType.Prefix,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Volatile = OpCode(
        "volatile.",
        Code.Volatile,
        2,
        OperandType.InlineNone,
        FlowControl.Meta,
        OpCodeType.Prefix,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Tail = OpCode(
        "tail.",
        Code.Tail,
        2,
        OperandType.InlineNone,
        FlowControl.Meta,
        OpCodeType.Prefix,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Initobj = OpCode(
        "initobj",
        Code.Initobj,
        2,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Objmodel,
        StackBehaviour.Popi,
        StackBehaviour.Push0,
    )
    Constrained = OpCode(
        "constrained.",
        Code.Constrained,
        2,
        OperandType.InlineType,
        FlowControl.Meta,
        OpCodeType.Prefix,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Cpblk = OpCode(
        "cpblk",
        Code.Cpblk,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popref_popi_popi,
        StackBehaviour.Push0,
    )
    Initblk = OpCode(
        "initblk",
        Code.Initblk,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Popref_popi_popi,
        StackBehaviour.Push0,
    )
    No = OpCode(
        "no.",
        Code.No,
        2,
        OperandType.ShortInlineI,
        FlowControl.Meta,
        OpCodeType.Prefix,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Rethrow = OpCode(
        "rethrow",
        Code.Rethrow,
        2,
        OperandType.InlineNone,
        FlowControl.Throw,
        OpCodeType.Objmodel,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )
    Sizeof = OpCode(
        "sizeof",
        Code.Sizeof,
        2,
        OperandType.InlineType,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop0,
        StackBehaviour.Pushi,
    )
    Refanytype = OpCode(
        "refanytype",
        Code.Refanytype,
        2,
        OperandType.InlineNone,
        FlowControl.Next,
        OpCodeType.Primitive,
        StackBehaviour.Pop1,
        StackBehaviour.Pushi,
    )
    Readonly = OpCode(
        "readonly.",
        Code.Readonly,
        2,
        OperandType.InlineNone,
        FlowControl.Meta,
        OpCodeType.Prefix,
        StackBehaviour.Pop0,
        StackBehaviour.Push0,
    )

    # Create lookup tables
    _single_byte_opcodes = {}
    _two_byte_opcodes = {}

    @classmethod
    def initialize(cls) -> None:
        """Initialize opcode lookup tables."""
        if cls._single_byte_opcodes:
            return  # Already initialized

        # Build single-byte opcode lookup
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, OpCode):
                if attr.size == 1:
                    cls._single_byte_opcodes[attr.value] = attr
                elif attr.size == 2:
                    cls._two_byte_opcodes[attr.value & 0xFF] = attr

    @classmethod
    def get_opcode(cls, value: int) -> Optional[OpCode]:
        """Get an opcode by its numeric value."""
        cls.initialize()

        # Handle two-byte opcodes (0xFE prefix)
        if value > 0xFF:
            return cls._two_byte_opcodes.get(value & 0xFF)
        else:
            return cls._single_byte_opcodes.get(value)

    @classmethod
    def get_all_opcodes(cls) -> list[OpCode]:
        """Get all opcodes."""
        cls.initialize()
        opcodes = []
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, OpCode):
                opcodes.append(attr)
        return sorted(opcodes, key=lambda op: op.value)


# Initialize the lookup tables
OpCodes.initialize()
