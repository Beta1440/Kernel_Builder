"""Provide a kernel interface for android kernels."""

import os
import shutil
from subprocess import check_call
from kbuilder.core.make import make_output

from kbuilder.kernel.kernel_linux import LinuxKernel
from unipath import Path


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

    def make_ota_package(self, *, output_dir: str,
                         source_dir: str=os.getcwd()) -> str:
        """Create an Over the Air (OTA) package that can be installed via recovery.

        Keyword arguments:
            extra_version -- appended to the name of the zip archive
            source_dir -- the directory to be zipped (default cwd)

        Returns:
            the path to the zip file created.
        """
        archive_path = Path(output_dir, self.custom_release)
        return shutil.make_archive(archive_path, 'zip', source_dir)
