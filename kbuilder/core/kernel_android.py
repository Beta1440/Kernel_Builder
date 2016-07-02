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

"""Provide an interface for android kernels."""

import os
from typing import Iterable, Tuple
import shutil
from subprocess import check_call

from cached_property import cached_property
from unipath import Path

from kbuilder.core.arch import Arch, UnsupportedArch
from kbuilder.core.gcc import Toolchain
from kbuilder.core.kernel import Kernel
import kbuilder.core.make as mk


class AndroidKernel(Kernel):
    """Provide an interface for android kernels"""

    def __init__(self, root: str, arch: Arch, *,
                 defconfig: str='defconfig') -> None:
        """Initialze a new Kernel.

        Keyword arguments:
        root -- the root directory of the kernel
        defconfig -- the defconfig file to use in building the kernel.
        """
        Kernel.__init__(root)
        self.version = self._find_kernel_version()
        self.version_numbers = self.version[-5:]
        self._defconfig = defconfig
        self._arch = arch
        self._kbuild_image = "TODO"

    @property
    def defconfig(self):
        """The default configuration file of the kernel."""
        return self._defconfig

    @cached_property
    def version(self):
        return self._find_kernel_version()

    @cached_property
    def version_numbers(self):
        """The kernel version in MAJOR.MINOR.PATCH format."""
        return self._find_kernel_version()[:-5]

    @cached_property
    def kbuild_image(self):
        """The path to the compressed kernel image."""
        return self.kbuild_image_abs_path(self.arch, self.kbuild_image)

    def _find_kernel_version(self) -> str:
        """Return what the version of the kernel is."""
        with self:
            output = mk.make_output('kernelrelease').rstrip()
            lines = output.split('\n')
            kernelrelease = lines[-1]
            return kernelrelease[8:]

    def _find_kbuild_image_name(self):
        if self.arch == Arch.arm:
            return 'zImage'
        elif self.arch == Arch.arm64:
            return 'Image.gz-dtb'
        elif self.arch == Arch.x86:
            return 'bzImage'
        else:
            raise UnsupportedArch

    def release_version(self, extra_version: str=None) -> str:
        """Get the kernel version with the toolchain name appended.

        Arguments:
        extension -- the extension to add to this.
        """
        if extra_version:
            return '{0.version}-{1}'.format(self, extra_version)
        else:
            return self.version

    def make_defconfig(self) -> None:
        """Make the default configuration file."""
        mk.make(self.defconfig)

    def build_kbuild_image(self, *, toolchain: Toolchain,
                           build_log_dir: str=None) -> Tuple[Path, str]:
        """Build the kernel kbuild.

        Return the path of the absolute path of kbuild image if the build is
        successful.
        Keyword arguments:
        toolchain -- the toolchain to use in building the kernel
        defconfig -- the default configuration file (default '')
        build_log_dir --  the directory of the build log file
        """
        kernel_release_version = self.release_version(toolchain.name)
        Path(build_log_dir).mkdir()
        build_log = Path(build_log_dir, kernel_release_version + '-log.txt')

        print('compiling {0.version} with {1.name}'.format(self, toolchain))
        output = mk.make_output('all')
        build_log.write_file(output)
        return self.kbuild_image, kernel_release_version

    def build_kbuild_images(self, toolchains: Iterable[Toolchain],
                            build_log_dir: str=None) -> Tuple[Path, str]:
        """Build multiple kbuild images the kernel.

        Return the path of the absolute path of kbuild image if the build is
        successful.
        Keyword arguments:
        toolchain -- the toolchain to use in building the kernel
        defconfig -- the default configuration file (default '')
        build_log_dir --  the directory of the build log file
        """
        for toolchain in toolchains:
            yield self.build(toolchain, build_log_dir)

    def make_boot_img(self, name: str, ramdisk: str='ramdisk.img'):
        """Create a boot.img file that can be install via fastboot.

        Keyword arguments:
        name -- the name of the output file
        kbuild_image -- the kernel image to include in the boot.img file
        ramdisk -- the ramdisk image to include in the boot.img file
        """
        args = '--output {} --kernel {} --ramdisk {}'.format(name,
                                                             self.kbuild_image,
                                                             ramdisk)
        check_call('mkbootimg ' + args, shell=True)

    def zip_ota_package(self, name: str, base_dir: str=os.getcwd()) -> str:
        """Create a zip package that can be installed via recovery.

        Return the path to the zip file created
        Keyword arguments:
        name -- the name of the zip file to create
        base_dir -- the directory whose contents should be zipped (default cwd)
        """
        return shutil.make_archive(name, 'zip', base_dir)
