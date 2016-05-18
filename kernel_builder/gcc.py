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
from typing import Iterable, List

from messages import alert, highlight, info, success


class Toolchain(object):
    """Store relevant info of a toolchain."""

    compiler_prefixes = {'aarch64': 'arm64', 'arm-eabi': 'arm'}

    def __init__(self, root: str, serial_number: int) -> None:
        """Initialize a new Toolchain.

        Keyword arguments:
        root -- the root directory of the toolchain
        serial_number -- a unique identification number of the toolchain
        """
        self.root = root
        self._name = path.basename(root)
        self._serial_number = serial_number
        self._compiler_prefix = self.find_compiler_prefix()
        self._target_arch = self.find_target_arch()

    @property
    def name(self):
        """The name of this."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def serial_number(self):
        """The serial number of this."""
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    @property
    def target_arch(self):
        """The target architecture of this compiler."""
        return self._target_arch

    @target_arch.setter
    def target_arch(self, value):
        """The target architecture of this compiler."""
        self._target_arch = value

    @property
    def compiler_prefix(self):
        """The prefix of all binaries of this."""
        return self._compiler_prefix

    @compiler_prefix.setter
    def compiler_prefix(self, value):
        """The prefix of all binaries of this."""
        self._compiler_prefix = value

    def set_as_active(self):
        """Set this self as the active toolchain to compile with."""
        os.putenv('CROSS_COMPILE', self.compiler_prefix)

    def find_compiler_prefix(self) -> str:
        """Return the prefix of all binaries of this."""
        def find_binaries() -> Iterable:
            """Return an Iterable of binaries in the toolchain's bin folder."""
            binaries_dir = path.join(self.root, 'bin')
            if path.isdir(binaries_dir):
                return os.scandir(binaries_dir)
            else:
                return None

        def is_gcc_binary(binary_name: str) -> bool:
            return binary_name.endswith('gcc')

        binaries = find_binaries()

        if binaries:
            for entry in binaries:
                if is_gcc_binary(entry.name):
                    compiler_prefix = entry.path[:-3]
                    return compiler_prefix

    def find_target_arch(self) -> str:
        """Determine the target architecture of the toolchain."""
        prefix = path.basename(self.compiler_prefix)
        for arch_prefix in iter(Toolchain.compiler_prefixes):
            if prefix.startswith(arch_prefix):
                target_arch = Toolchain.compiler_prefixes[arch_prefix]
                return target_arch

    def _is_valid(self, target_arch: str=None) -> bool:
        is_toolchain = bool(self.compiler_prefix)
        correct_arch = not target_arch or self.target_arch == target_arch
        return is_toolchain and correct_arch


def scandir(toolchain_dir: str, target_arch: str='') -> List[Toolchain]:
    """Get all the valid the toolchains in a directory.

    A toolchain is valid if it has a gcc executable in its "bin/" directory

    Keyword arguments:
    toolchain_dir -- the directory to look for toolchains
    target_arch -- the architecture to get toolchains for
    """
    entries = os.scandir(toolchain_dir)
    toolchains = []
    serial_number = 1

    for entry in entries:
        toolchain = Toolchain(entry.path, serial_number)
        if (toolchain._is_valid(target_arch)):
            toolchains.append(toolchain)
            print(success('Toolchain located: '), highlight(toolchain.name))
            serial_number += 1

    if not toolchains:
        print('{} no {} toolchains detected in {}'.format((alert('Error:')),
              highlight(target_arch), highlight(toolchain_dir)))

    return sorted(toolchains, key=lambda toolchain: toolchain.name)


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
        print(info('{}) {}'.format(toolchains.index(toolchain) + 1,
                                   toolchain.name)))

    numbers = input('Enter numbers separated by spaces: ')
    chosen_numbers = [int(num) for num in numbers.split()]
    selected_toolchains = []
    for number in chosen_numbers:
        selected_toolchains.append(toolchains[number - 1])

    return selected_toolchains
