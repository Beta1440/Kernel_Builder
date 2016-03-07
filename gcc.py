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
