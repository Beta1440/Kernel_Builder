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

from typing import Iterable

class Toolchain:
    'Store relevant info of a toolchain'
    binary_file_prefixes = {'arm64':'aarch64', 'arm':'arm-eabi'}

    def __init__(self, root : str, serial_number : int, arch : str) -> None:
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
        return scandir(binaries_dir)

    def get_compiler_prefix(self) -> str:

        def is_gcc_binary(binary, prefix : str) -> bool:
            name = binary.name
            return name.startswith(prefix) and name.endswith('gcc')

        for entry in self.get_binaries():
                prefix = Toolchain.binary_file_prefixes[self.arch]
                if is_gcc_binary(entry, prefix):
                    compiler_prefix = entry.path[:-3]
                    return compiler_prefix
