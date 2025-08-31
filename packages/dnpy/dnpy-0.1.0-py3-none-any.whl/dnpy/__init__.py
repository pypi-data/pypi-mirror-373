"""
dnpy - A Python library for reading and writing .NET assemblies.

This package provides tools for parsing, modifying, and writing PE/NET binaries
with a clean, type-safe Python API.
"""

from .model.module import Module

__version__ = "0.1.0"
__all__ = ["Module"]
