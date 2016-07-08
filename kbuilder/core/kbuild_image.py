"""Provide an enumeration for kbuild images. Each architecture has
   a kbuild image associated with it. This module helps to link
   architures with their respective kbuild image.
   """

from enum import Enum

from kbuilder.core.arch import Arch


class KbuildImage(Enum):
    """Provide an enumeration for kbuild images."""

    arm = 'zImage'
    arm64 = 'Image.gz-dtb'
    x86 = 'bzImage'
