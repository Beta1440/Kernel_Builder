import os
from pathlib import Path
from typing import Iterable, List, Optional

from kbuilder.core.arch import Arch


class Toolchain(object):
    """Store relevant info of a toolchain."""

    compiler_prefixes = {'aarch64': Arch.arm64, 'arm-eabi': Arch.arm}

    def __init__(self, root: str) -> None:
        """Initialize a new Toolchain.

        Keyword arguments:
        root -- the root directory of the toolchain
        """
        self.root = Path(root)
        self._name = self.root.name
        self._compiler_prefix = Path(self.find_compiler_prefix())
        self._target_arch = self._find_target_arch()

    def __str__(self) -> str:
        """Return the name of the toolchain's root directory."""
        return self.name

    def __nonzero__(self) -> bool:
        """Return whether the toolchain is valid.

        A toolchain needs a 'bin' directory to be valid.
        """
        return self.root.isdir() and Path(self.root, 'bin').isdir()

    def __enter__(self):
        """Set this self as the toolchain to compile targets."""
        self.set_as_active()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Do not supresses any errors.

        Positional arguments:
        exc_type -- the type of exception
        exc_val -- the value of the exception
        exc_tb -- the traceback of the exception
        """
        return False

    @property
    def name(self):
        """The name of this."""
        return self._name

    @property
    def target_arch(self):
        """The target architecture of this compiler."""
        return self._target_arch

    @property
    def compiler_prefix(self):
        """The prefix of all binaries of this."""
        return self._compiler_prefix

    def find_compiler_prefix(self) -> str:
        """Return the prefix of all binaries of this."""

        def find_binaries() -> Iterable:
            """Return an Iterable of binaries in the toolchain's bin folder."""
            try:
                return os.scandir(self.root / 'bin')
            except:
                pass

        def is_gcc_binary(binary_name: str) -> bool:
            return binary_name.endswith('gcc')

        binaries = find_binaries()

        if not binaries:
            return ""

        for entry in binaries:
            if is_gcc_binary(entry.name):
                compiler_prefix = entry.path[:-3]
                return compiler_prefix

    @staticmethod
    def find(toolchains: Iterable, target_name: str) -> List:
        """Search for a toolchain with a given root directory.

        Args:
            toolchains: Iterable of toolchains to search thourgh.
            target_arch: Target architecture of toolchains to search for.
            target_name: Name of the toolchain root directory.

        Returns:
            The first toolchain the given name.
                return None if no toolchain could be located.
        """
        for toolchain in toolchains:
            if toolchain.name == target_name:
                return toolchain

    def _find_target_arch(self) -> Arch:
        """Determine the target architecture of the toolchain."""
        prefix = self.compiler_prefix.name
        for arch_prefix in iter(Toolchain.compiler_prefixes):
            if prefix.startswith(arch_prefix):
                target_arch = Toolchain.compiler_prefixes[arch_prefix]
                return target_arch

    def set_as_active(self):
        """Set this self as the active toolchain to compile with."""
        os.putenv('CROSS_COMPILE', self.compiler_prefix)
        os.putenv('SUBARCH', self.target_arch.name)


def scandir(toolchain_dir: str, target_arch: Optional[Arch] = None) -> List:
    """Return a list of toolchains located in a directory.

    A toolchain is considered valid if it has a gcc executable in its
     'bin' directory.

    Positional arguments:
    toolchain_dir -- the directory to look for toolchains.

    Keyword arguments:
    target_arch -- the target architecture of toolchains to search for.
        If empty, then toolchains of any architecture may be returned
        otherwise only toolchains with the matching architecture will be
        returned (default None).
    """

    def valid_arch():
        return not target_arch or toolchain.target_arch == target_arch

    toolchains = []
    entries = sorted(os.scandir(toolchain_dir), key=lambda x: x.name)

    for entry in entries:
        toolchain = Toolchain(entry.path)
        if toolchain and valid_arch():
            toolchains.append(toolchain)
    return toolchains


def prompt(toolchains: List) -> Iterable:
    """Return an Iterator of toolchains from a list of toolchains.

    Each toolchain will be printed with its position in the list.
    The positions begin at 1 and are printed next to the toolchain.
    Then the client will be prompted to enter in a series of numbers.
    An Iterable containing toolchains with the matching positions from the
    input will be returned. If only one toolchain is in the list,
    then it will be automatically selected.

    Positional arguments:
    toolchains -- the list of toolchains to select from
    """
    if len(toolchains) <= 1:
        return toolchains

    for index, toolchain in enumerate(toolchains, 1):
        print('{}) {}'.format(index, toolchain))

    numbers = input('Enter numbers separated by spaces: ')
    chosen_numbers = [int(x) for x in numbers.split()]
    for number in chosen_numbers:
        yield toolchains[number - 1]


def prompt_one(toolchains: List) -> Toolchain:
    """Select a toolchain from a list of toolchains.

    Each toolchain will be printed with its position in the list.
    The positions begin at 1 and are printed next to the toolchain.
    Then the client will be prompted to enter in the corresponding position.
    of the desired toolchain. An Iterable containing toolchains with the
    matching positions from the input will be returned.

    Positional arguments:
    toolchains -- the list of toolchains to select from.
    """
    for index, toolchain in enumerate(toolchains, 1):
        print('{}) {}'.format(index, toolchain))

    number = input('Enter a single number: ')
    return toolchains[int(number) - 1]


def prompt_from_scandir(toolchain_dir: str, *,
                        target_arch: Optional[Arch] = None) -> Iterable:
    """Select a toolchain from a directory of toolchains.

    Positional arguments:
        toolchain_dir -- directory to search for toolchain

    Keyword arguements:
        target_arch -- architecture of toolchains to search for (Default None).

    Returns:
        An iterator of the selected toolchains.
    """
    return prompt(scandir(toolchain_dir, target_arch))
