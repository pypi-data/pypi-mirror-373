"""
Core data model classes.

Provides the object model for .NET assemblies, types, members, and attributes.
"""

from .assembly import Assembly
from .members import EventDef, FieldDef, MemberRef, MethodDef, PropertyDef
from .module import Module
from .types import TypeDef, TypeRef

__all__ = [
    "Module",
    "Assembly",
    "TypeDef",
    "TypeRef",
    "MethodDef",
    "FieldDef",
    "PropertyDef",
    "EventDef",
    "MemberRef",
]
