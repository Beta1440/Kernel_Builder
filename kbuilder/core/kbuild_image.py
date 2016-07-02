"""Provide an enumeration for kbuild images. Each architecture has
   a kbuild image associated with it. This module helps to link
   architures with their respective kbuild image.
   """

from enum import Enum

from kbuilder.core.arch import Arch


class Kbuild_Image(Enum):
    """Provide an enumeration for kbuild images."""

    Arch.arm = 'zImage'
    Arch.arm64 = 'Image.gz-dtb'
    Arch.x86 = 'bzImage'
