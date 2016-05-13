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

from os import scandir, path
from subprocess import getoutput
from messages import alert, highlight, success, info
from typing import Iterable, List

class Toolchain:
    'Store relevant info of a toolchain'
    binary_file_prefixes = {'arm64':'aarch64', 'arm':'arm-eabi'}

    def __init__(self, root: str, serial_number: int, arch: str='arm64') -> None:
        self.root = root
        self.name = path.basename(root)
        self.serial_number = serial_number
        self.arch = arch
        self.compiler_prefix = self.get_compiler_prefix()
        try:
            self.version = getoutput(self.compiler_prefix + 'gcc -dumpversion')
        except:
            self.version = 'unknown'

    def get_binaries(self) -> Iterable:
        binaries_dir = path.join(self.root, 'bin')
        if path.isdir(binaries_dir):
            return scandir(binaries_dir)
        else:
            return None

    def get_compiler_prefix(self) -> str:

        def is_gcc_binary(binary, prefix : str) -> bool:
            name = binary.name
            return name.startswith(prefix) and name.endswith('gcc')

        binaries = self.get_binaries()

        if binaries:
            for entry in binaries:
                prefix = Toolchain.binary_file_prefixes[self.arch]
                if is_gcc_binary(entry, prefix):
                    compiler_prefix = entry.path[:-3]
                    return compiler_prefix


def get_toolchains(toolchain_dir : str) -> List[Toolchain]:
    """Get all the valid the toolchains in a directory.

    A toolchain is valid if it has a gcc executable in its "bin/" directory

    Keyword arguments:
    toolchain_dir -- the directory to look for toolchains
    """
    entries = scandir(toolchain_dir)
    toolchains = []
    serial_number = 1
    for entry in entries:
        toolchain = Toolchain(entry.path, serial_number)
        if(toolchain.compiler_prefix):
            toolchains.append(toolchain)
            print(success('Toolchain located: '), highlight(toolchain.name))
            serial_number += 1

    return toolchains


def select_toolchains(toolchains : List[Toolchain]) -> List[Toolchain]:
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
