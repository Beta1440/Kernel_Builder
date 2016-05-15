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
from os import path
from subprocess import getoutput
from typing import Iterable, List

from messages import alert, highlight, info, success


class Toolchain:
    """Store relevant info of a toolchain."""

    binary_file_prefixes = {'arm64': 'aarch64', 'arm': 'arm-eabi'}

    def __init__(self, root: str, serial_number: int, arch: str='arm64') -> None:
        """Initialize a new Toolchain.

        Keyword arguments:
        root -- the root directory of the toolchain
        serial_number -- a unique identification number of the toolchain
        arch -- the target architecture of the Toolchain (default 'arm64')
        """
        self.root = root
        self.name = path.basename(root)
        self.serial_number = serial_number
        self.arch = arch
        self.compiler_prefix = self.find_compiler_prefix()

    def find_binaries(self) -> Iterable:
        """Return an Iterable of binaries in the toolchain's bin folder."""
        binaries_dir = path.join(self.root, 'bin')
        if path.isdir(binaries_dir):
            return os.scandir(binaries_dir)
        else:
            return None

    def set_as_active(self):
        """Set this self as the active toolchain to compile with."""
        os.putenv('CROSS_COMPILE', self.compiler_prefix)

    def find_compiler_prefix(self) -> str:
        """Return the prefix of all binaries of this."""
        def is_gcc_binary(binary, prefix: str) -> bool:
            name = binary.name
            return name.startswith(prefix) and name.endswith('gcc')

        binaries = self.find_binaries()

        if binaries:
            for entry in binaries:
                prefix = Toolchain.binary_file_prefixes[self.arch]
                if is_gcc_binary(entry, prefix):
                    compiler_prefix = entry.path[:-3]
                    return compiler_prefix


def scandir(toolchain_dir: str, target_arch: str='') -> List[Toolchain]:
    """Get all the valid the toolchains in a directory.

    A toolchain is valid if it has a gcc executable in its "bin/" directory

    Keyword arguments:
    toolchain_dir -- the directory to look for toolchains
    """
    entries = os.scandir(toolchain_dir)
    toolchains = []
    serial_number = 1

    if not target_arch:
        target_arch = 'arm64'

    for entry in entries:
        toolchain = Toolchain(entry.path, serial_number, arch=target_arch)

        if (toolchain.compiler_prefix):
            toolchains.append(toolchain)
            print(success('Toolchain located: '), highlight(toolchain.name))
            serial_number += 1

    if not toolchains:
        print('{} no {} toolchains detected in {}'.format((alert('Error:')),
              highlight(target_arch), highlight(toolchain_dir)))

    return toolchains


def select(toolchains: List[Toolchain]) -> List[Toolchain]:
    """Select which toolchains to use in compiling the kernel.

    The kernel will be compiled once with each toolchain selected.
    If only one toolchain is available, then it will be automatically selected.

    Keyword arguments:
    toolchains -- the list of toolchains to select from
    """
    if len(toolchains) <= 1:
        return toolchains

    for toolchain in toolchains:
        print(info('{}) {}'.format(toolchain.serial_number, toolchain.name)))

    toolchain_numbers = input('Enter numbers separated by spaces: ')
    chosen_numbers = [int(num) for num in toolchain_numbers.split()]
    return filter(lambda x: x.serial_number in chosen_numbers, toolchains)
