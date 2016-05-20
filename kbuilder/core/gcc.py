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
from typing import Iterable, List

from unipath.path import Path

from kbuilder.core.messages import alert, highlight, info, success


class Toolchain(object):
    """Store relevant info of a toolchain."""

    compiler_prefixes = {'aarch64': 'arm64', 'arm-eabi': 'arm'}

    def __init__(self, root: str) -> None:
        """Initialize a new Toolchain.

        Keyword arguments:
        root -- the root directory of the toolchain
        """
        self.root = Path(root)
        self._name = self.root.name
        self._compiler_prefix = Path(self.find_compiler_prefix())
        self._target_arch = self.find_target_arch()

    def __str__(self) -> str:
        """Return the name of the toolchain's root directory."""
        return self.name

    def __nonzero__(self) -> bool:
        """Return whether the toolchain is valid.

        A toolchain needs a 'bin' directory to be valid.
        """
        return self.root.isdir() and Path(self.root, 'bin').isdir()

    @property
    def name(self):
        """The name of this."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

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
            binaries_dir = Path(self.root, 'bin')
            if binaries_dir.isdir():
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
        prefix = self.compiler_prefix.name
        for arch_prefix in iter(Toolchain.compiler_prefixes):
            if prefix.startswith(arch_prefix):
                target_arch = Toolchain.compiler_prefixes[arch_prefix]
                return target_arch


def scandir(toolchain_dir: str, target_arch: str='') -> List[Toolchain]:
    """Get all the valid the toolchains in a directory.

    A toolchain is valid if it has a gcc executable in its "bin/" directory

    Keyword arguments:
    toolchain_dir -- the directory to look for toolchains
    target_arch -- the architecture to get toolchains for
    """
    entries = os.scandir(toolchain_dir)
    toolchains = []

    for entry in entries:
        toolchain = Toolchain(entry.path)
        if toolchain and (not target_arch or
                          toolchain.target_arch == target_arch):
            toolchains.append(toolchain)

    if not toolchains:
        print('{} no {} toolchains detected in {}'.format((alert('Error:')),
              highlight(target_arch), highlight(toolchain_dir)))

    toolchain_names = [highlight(toolchain) for toolchain in toolchains]
    print(success('Toolchains located: '), ', '.join(toolchain_names))
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

    for index, toolchain in enumerate(toolchains):
        name = highlight(toolchain.name)
        print(info('{}) {}'.format(index + 1, name)))

    numbers = input('Enter numbers separated by spaces: ')
    chosen_numbers = [int(num) for num in numbers.split()]
    selected_toolchains = []
    for number in chosen_numbers:
        selected_toolchains.append(toolchains[number - 1])

    return selected_toolchains
