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

import os
import logging
import sys

from cached_property import cached_property
from subprocess import CalledProcessError, CompletedProcess
from typing import Iterable, Tuple, Optional
from unipath.path import Path

from kbuilder.core.arch import Arch
from kbuilder.core.gcc import Toolchain
import kbuilder.core.make as mk
from kbuilder.core.messages import alert, highlight, success

KERNEL_DIRS = ['arch', 'crypto', 'Documentation', 'drivers', 'include',
               'scripts', 'tools']


class Kernel(object):
    """store info for a kernel."""
    def __init__(self, root: str) -> None:
        """Initialze a new Kernel.

        Keyword arguments:
        root -- the root directory of the kernel
        """
        self._root = Path(root)
        self.version_numbers = self.version[-5:]

    @property
    def root(self):
        """The absolute path of the kernel root"""
        return self._root

    @property
    def name(self):
        """The name of the kernel root"""
        return self.root.name

    @cached_property
    def version(self):
        """The local kernel version in the defconfig file."""
        return self._find_kernel_version()

    def _find_kernel_verion(self):
        with self:
            output = mk.make_output('kernelrelease').rstrip()
            lines = output.split('\n')
            kernelrelease = lines[-1]
            return kernelrelease[8:]

    def __enter__(self):
        self._prev_dir = Path(os.getcwd())
        self.root.chdir()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._prev_dir.chdir()
        return False

    def release_version(self, *, suffix: Optional[str]=None) -> str:
        """Get the kernel version with the toolchain name appended.

        Arguments:
        extension -- the extension to add to this.
        """
        if suffix:
            return '{0.version}-{1}'.format(self, suffix)
        else:
            return self.version

    @staticmethod
    def find_root(initial_path: str) -> Path:
        """Find the root of the kernel directory.

        Search for the root of a kernel directory starting at a given directory.
        The search continues until the kernel root is found or the system root
        directory is reached. If the system root directory is reached, then
        'None' is returned. Otherwise, the path of the kernel root directory is
        returned.
        Arguments
        initial_path -- the path to begin search
        """
        def is_kernel_root(path: Path) -> bool:
            """Check if the current path is the root directory of a kernel."""
            files_in_dir = [file.name for file in os.scandir(path)]
            return all(kernel_dir in files_in_dir for kernel_dir in KERNEL_DIRS)

        def walk_to_root(path: Path) -> Path:
            """Search for the root of the kernel directory."""
            system_root = Path('/')
            if is_kernel_root(path):
                return path
            elif path == system_root:
                return None
            else:
                return walk_to_root(path.parent)

        return walk_to_root(Path(initial_path))

    @staticmethod
    def arch_clean() -> CompletedProcess:
        """Remove compiled kernel files in the arch directory.

        This form of cleaning is useful for rebuilding the kernel with the same
        Toolchain, since only files that were changed will be compiled.
        Keyword arguements
        """
        print('Performing an arch clean')
        return mk.make('archclean')

    @staticmethod
    def clean() -> CompletedProcess:
        """Remove all compiled kernel files.

        This form of cleaning is useful when switching the toolchain to build
        kernel since all files need to be recompiled.
        Keyword arguements
        """
        print('Removing all compiled files')
        return mk.make('clean')

    def kbuild_image_abs_path(self, arch: Arch, kbuild_image: str) -> Path:
        """Return the absolute path to the kbuild image of the kernel.

        The kbuild image is a compressed kernel image that if produced
        after the kernel if compiled.
        Arguements:
        arch -- the architecture being compiled.
        kbuild_image -- the name of the kbuild image file.
        """
        return self.root.child('arch', arch.name, 'boot', kbuild_image)

    def build_kbuild_image(self, toolchain: Toolchain,
                           log_dir: Optional[str]=None) -> Tuple[Path, str]:
        """Build the kernel kbuild.

        Return the path of the absolute path of kbuild image if the build is
        successful.
        Positional arguments:
        Keyword arguments:
        toolchain -- the toolchain to use in building the kernel
        log_dir --  the directory of the build log file
        """
        kernel_release_version = self.release_version(suffix=toolchain.name)
        Path(log_dir).mkdir()
        build_log = Path(log_dir, kernel_release_version + '-log.txt')

        print('compiling {0.version} with {1.name}'.format(self, toolchain))
        output = mk.make_output('all')
        build_log.write_file(output)
        return self.kbuild_image, kernel_release_version
