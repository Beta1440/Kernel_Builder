"""Provide an enumeration for computer architectures."""

from enum import Enum


class Arch(Enum):
    """Provide an enumeration for computer architectures."""

    arm = 1
    arm64 = 2
    x86 = 3


class ArchError(ValueError):
    """Raise when a function receives an Arch it does not support."""

    pass
