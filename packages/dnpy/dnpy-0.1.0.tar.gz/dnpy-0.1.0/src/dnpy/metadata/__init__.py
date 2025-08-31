"""
NET metadata parsing module.

Handles .NET headers, metadata streams, tables, and signatures.
"""

from .il import CilBody, Instruction
from .metadata import MetadataRoot, TableHeap
from .opcodes import OpCode, OpCodes
from .streams import BlobHeap, GuidHeap, StringsHeap, UserStringHeap
from .tokens import Token, TokenType

__all__ = [
    "MetadataRoot",
    "TableHeap",
    "StringsHeap",
    "UserStringHeap",
    "BlobHeap",
    "GuidHeap",
    "Token",
    "TokenType",
    "CilBody",
    "Instruction",
    "OpCode",
    "OpCodes",
]
