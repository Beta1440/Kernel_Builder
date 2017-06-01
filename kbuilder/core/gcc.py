import os
from pathlib import Path
from typing import Iterable, List, Optional

from kbuilder.core.arch import Arch


class Compiler(object):
    """Store relevant info of a compiler."""

    compiler_prefixes = {'aarch64': Arch.arm64, 'arm-eabi': Arch.arm}

    def __init__(self, root: str) -> None:
        """Initialize a new Compiler.

        Keyword arguments:
        root -- the root directory of the compiler
        """
        self.root = Path(root)
        self._name = self.root.name
        self._compiler_prefix = Path(self.find_compiler_prefix())
        self._target_arch = self._find_target_arch()

    def __str__(self) -> str:
        """Return the name of the compiler's root directory."""
        return self.name

    def __nonzero__(self) -> bool:
        """Return whether the compiler is valid.

        A compiler needs a 'bin' directory to be valid.
        """
        return self.root.isdir() and Path(self.root, 'bin').isdir()

    def __enter__(self):
        """Set this self as the compiler to compile targets."""
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
            """Return an Iterable of binaries in the compiler's bin folder."""
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
    def find(compilers: Iterable, target_name: str) -> List:
        """Search for a compiler with a given root directory.

        Args:
            compilers: Iterable of compilers to search thourgh.
            target_arch: Target architecture of compilers to search for.
            target_name: Name of the compiler root directory.

        Returns:
            The first compiler the given name.
                return None if no compiler could be located.
        """
        for compiler in compilers:
            if compiler.name == target_name:
                return compiler

    def _find_target_arch(self) -> Arch:
        """Determine the target architecture of the compiler."""
        prefix = self.compiler_prefix.name
        for arch_prefix in iter(Compiler.compiler_prefixes):
            if prefix.startswith(arch_prefix):
                target_arch = Compiler.compiler_prefixes[arch_prefix]
                return target_arch

    def set_as_active(self):
        """Set this self as the active compiler to compile with."""
        os.putenv('CROSS_COMPILE', self.compiler_prefix)
        os.putenv('SUBARCH', self.target_arch.name)


def scandir(compiler_dir: str, target_arch: Optional[Arch] = None) -> List:
    """Return a list of compilers located in a directory.

    A compiler is considered valid if it has a gcc executable in its
     'bin' directory.

    Positional arguments:
    compiler_dir -- the directory to look for compilers.

    Keyword arguments:
    target_arch -- the target architecture of compilers to search for.
        If empty, then compilers of any architecture may be returned
        otherwise only compilers with the matching architecture will be
        returned (default None).
    """

    def valid_arch():
        return not target_arch or compiler.target_arch == target_arch

    compilers = []
    entries = sorted(os.scandir(compiler_dir), key=lambda x: x.name)

    for entry in entries:
        compiler = Compiler(entry.path)
        if compiler and valid_arch():
            compilers.append(compiler)
    return compilers


def prompt(compilers: List) -> Iterable:
    """Return an Iterator of compilers from a list of compilers.

    Each compiler will be printed with its position in the list.
    The positions begin at 1 and are printed next to the compiler.
    Then the client will be prompted to enter in a series of numbers.
    An Iterable containing compilers with the matching positions from the
    input will be returned. If only one compiler is in the list,
    then it will be automatically selected.

    Positional arguments:
    compilers -- the list of compilers to select from
    """
    if len(compilers) <= 1:
        return compilers

    for index, compiler in enumerate(compilers, 1):
        print('{}) {}'.format(index, compiler))

    numbers = input('Enter numbers separated by spaces: ')
    chosen_numbers = [int(x) for x in numbers.split()]
    for number in chosen_numbers:
        yield compilers[number - 1]


def prompt_one(compilers: List) -> Compiler:
    """Select a compiler from a list of compilers.

    Each compiler will be printed with its position in the list.
    The positions begin at 1 and are printed next to the compiler.
    Then the client will be prompted to enter in the corresponding position.
    of the desired compiler. An Iterable containing compilers with the
    matching positions from the input will be returned.

    Positional arguments:
    compilers -- the list of compilers to select from.
    """
    for index, compiler in enumerate(compilers, 1):
        print('{}) {}'.format(index, compiler))

    number = input('Enter a single number: ')
    return compilers[int(number) - 1]


def prompt_from_scandir(compiler_dir: str, *,
                        target_arch: Optional[Arch] = None) -> Iterable:
    """Select a compiler from a directory of compilers.

    Positional arguments:
        compiler_dir -- directory to search for compiler

    Keyword arguements:
        target_arch -- architecture of compilers to search for (Default None).

    Returns:
        An iterator of the selected compilers.
    """
    return prompt(scandir(compiler_dir, target_arch))
