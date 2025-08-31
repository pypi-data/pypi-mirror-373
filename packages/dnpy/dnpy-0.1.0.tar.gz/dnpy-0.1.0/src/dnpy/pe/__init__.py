"""
PE/COFF parsing module.

Handles PE parsing using pefile and adds .NET-specific functionality.
"""

from .pe_wrapper import NETHeader, DotNetPE

__all__ = [
    "DotNetPE",
    "NETHeader",
]
