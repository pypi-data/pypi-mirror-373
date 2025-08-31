"""
Assembly definition and reference.
"""

from dataclasses import dataclass
from enum import IntFlag

from ..metadata.tokens import Token

__all__ = [
    "AssemblyAttributes",
    "Assembly",
    "AssemblyRef",
]


class AssemblyAttributes(IntFlag):
    """Assembly attributes (ECMA-335 II.23.1.2)."""

    PublicKey = 0x0001
    Retargetable = 0x0100
    WindowsRuntime = 0x0200
    DisableJITcompileOptimizer = 0x4000
    EnableJITcompileTracking = 0x8000


@dataclass(slots=True)
class Assembly:
    """Assembly definition (ECMA-335 II.22.2)."""

    token: Token
    hash_alg_id: int
    major_version: int
    minor_version: int
    build_number: int
    revision_number: int
    flags: AssemblyAttributes
    public_key: bytes | None
    name: str
    culture: str

    @property
    def version(self) -> str:
        """Get version string."""
        return f"{self.major_version}.{self.minor_version}.{self.build_number}.{self.revision_number}"

    @property
    def has_public_key(self) -> bool:
        """Check if assembly has a public key."""
        return bool(self.flags & AssemblyAttributes.PublicKey)


@dataclass(frozen=True, slots=True)
class AssemblyRef:
    """Assembly reference (ECMA-335 II.22.5)."""

    token: Token
    major_version: int
    minor_version: int
    build_number: int
    revision_number: int
    flags: AssemblyAttributes
    public_key_or_token: bytes | None
    name: str
    culture: str
    hash_value: bytes | None

    @property
    def version(self) -> str:
        """Get version string."""
        return f"{self.major_version}.{self.minor_version}.{self.build_number}.{self.revision_number}"
