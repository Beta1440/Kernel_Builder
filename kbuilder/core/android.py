"""Core Android abstractions."""

import os
import shutil
from subprocess import check_call
from typing import Optional

from unipath import Path

from kbuilder.core.linux import LinuxKernel


class AndroidKernel(LinuxKernel):
    """Provide a kernel interface for android kernels.

    Android kernels are usually compiled for one particular architecture.
    The same defconfig file is used every time. Additionally, android has two
    main build targets: an over-the-air (OTA) package and boot.img. This class
    facilitates building the main android build targets."""

    @property
    def version_numbers(self):
        """The kernel version in MAJOR.MINOR.PATCH format."""
        return self.local_version[-5:]

    @property
    def custom_release(self):
        """The local kernel version.

        If extraversion is defined, then it will be contatened to the kernel release.
        """
        if self.extra_version:
            return '{0.local_version}-{0.extra_version}'.format(self)
        return self.local_version

    def make_boot_img(self, ramdisk: str='ramdisk.img'):
        """Create a boot.img file that can be install via fastboot.

        Keyword arguments:
            ramdisk -- the ramdisk image to include in the boot.img file
        """
        output = '--output {}'.format(self.custom_release)
        kernel = '--kernel {}'.format(self.kbuild_image)
        ramdisk = '--ramdisk {}'.format(ramdisk)
        check_call('mkbootimg {} {} {}'.format(output, kernel, ramdisk), shell=True)

    def make_ota_package(self, *, kbuild_image_dir: Optional[Path]="",
                         output_dir: Path, source_dir: Path=Path.cwd()) -> Path:
        """Create an Over the Air (OTA) package that can be installed via recovery.

        Keyword Args:
            output_dir: Where the otapackage will be stored
            source_dir: The directory to be zipped (default cwd)
            kbuild_image_dir: Optional path to to copy kbuild image into; relative to source_dir

        Returns:
            the path to the zip file created.
        """
        if kbuild_image_dir:
            shutil.copy(self.kbuild_image.as_posix(), (source_dir / kbuild_image_dir).as_posix())
        archive_path = output_dir / self.custom_release.lower()
        archive_name = archive_path.as_posix()
        return Path(shutil.make_archive(archive_name, 'zip', source_dir))
