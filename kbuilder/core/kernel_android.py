#     Copyright (C) 2016 Dela Anthonio <dell.anthonio@gmail.com>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Provide a kernel interface for android kernels."""

import os
import shutil
from subprocess import check_call

from kbuilder.core.kernel import Kernel
from unipath import Path


class AndroidKernel(Kernel):
    """Provide a kernel interface for android kernels.

    Android kernels are usually compiled for one particular architecture.
    The same defconfig file is used every time. Additionally, android has two
    main build targets: an over-the-air (OTA) package and boot.img. This class
    facilitates building the main android build targets."""

    @property
    def version_numbers(self):
        """The kernel version in MAJOR.MINOR.PATCH format."""
        return self.version[-5:]

    def make_boot_img(self, ramdisk: str='ramdisk.img'):
        """Create a boot.img file that can be install via fastboot.

        Keyword arguments:
            ramdisk -- the ramdisk image to include in the boot.img file
        """
        output = '--output {}'.format(self.release_version)
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
        archive_path = Path(output_dir, self.release_version)
        return shutil.make_archive(archive_path, 'zip', source_dir)
