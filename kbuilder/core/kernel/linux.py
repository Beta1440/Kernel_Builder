import os
from pathlib import Path
from typing import Optional

from cached_property import cached_property

from kbuilder.core.arch import Arch
from kbuilder.core.make import Makefile


class LinuxKernel(object):
    """A high level interface for the Linux Kernel.

    Provides access to attributes and common operations of the Linux Kernel.
    """
    kbuild_image_name = {Arch.arm: 'zImage',
                         Arch.arm64: 'Image.gz-dtb',
                         Arch.x86: 'bzImage'}

    required_dirs = ['arch',
                     'crypto',
                     'Documentation',
                     'drivers',
                     'include',
                     'scripts',
                     'tools']

    def __init__(self, root: str, *, arch: Arch=None,
                 defconfig: str='defconfig') -> None:
        """Initialze a new Kernel.

        Args:
            root: kernel root directory.
            arch: kernel architecture.
            defconfig: default configuration file.
        """
        self._root = Path(root)
        self._extra_version = None
        self._defconfig = defconfig
        self._arch = arch
        self.makefile = Makefile(root)

    @property
    def root(self):
        """The absolute path of the kernel root."""
        return self._root

    @property
    def name(self):
        """The name of the kernel root directory."""
        return self.root.name

    @cached_property
    def linux_version(self):
        """The Linux version of the kernel."""
        return self.makefile.make_output_last_line('kernelversion')

    @cached_property
    def release_version(self):
        """Linux kernel version with the local version appended."""
        return self.makefile.make_output_last_line('kernelrelease')

    @cached_property
    def local_version(self):
        """The local version of the kernel.

        The local version is defined in the kernel defconfig file.
        """
        return self.release_version[len(self.linux_version) + 1:]

    @property
    def extra_version(self):
        """An optional version to append to the end of the kernel version."""
        return self._extra_version

    @extra_version.setter
    def extra_version(self, version: str):
        """Set extra_version."""
        self._extra_version = version

    @property
    def custom_release(self):
        """A custom kernel release.

        Append extraversion to the kernel release.
        """
        if self.extra_version:
            return '{0.release_version}-{0.extra_version}'.format(self)
        return self.release_version

    @property
    def arch(self):
        """The architecture of the kernel."""
        return self._arch

    @property
    def defconfig(self):
        """The default configuration file.

        The defconfig file specifies which modules to build for the kernel."""
        return self._defconfig

    @cached_property
    def kbuild_image(self):
        """The absolute path to the compressed kernel image."""
        kbuild_image = LinuxKernel.kbuild_image_name[self.arch]
        return self.root / 'arch' / self.arch.name / 'boot' / kbuild_image

    def __enter__(self):
        """Change the current directory the kernel root."""
        self._prev_dir = Path.cwd()
        os.chdir(self.root)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Revert the current directory to the original directory."""
        os.chdir(self._prev_dir)
        return False

    @staticmethod
    def find_root(kernel_sub_directory: str) -> Path:
        """Locate the root of the kernel directory.

        The search must begin inside a sub directory of the kernel root.
        The search continues until the kernel root is found or the system root
        directory is reached.

        Args:
            kernel_sub_directory: Path to begin search.

        Returns:
            Absolute path of the kernel root directory.

        Raises:
            FileNotFoundError if the kernel root could not be located.
        """
        def is_kernel_root(path: Path) -> bool:
            path_dirs = [file.name for file in os.scandir(path)]
            return all(dir in path_dirs for dir in LinuxKernel.required_dirs)

        def is_system_root(path: Path) -> bool:
            return path == Path('/')

        path = Path(kernel_sub_directory)

        while not is_system_root(path):
            if is_kernel_root(path):
                return path
            path = path.parent

        raise FileNotFoundError('Kernel root could not be located')

    def arch_clean(self) -> None:
        """Remove compiled kernel files in the arch directory.

        This form of cleaning is useful for rebuilding the kernel with the same
        Toolchain, since only files that were changed will be recompiled.
        """
        with self:
            self.makefile.make('archclean')

    def clean(self) -> None:
        """Remove all compiled kernel files.

        This form of cleaning is useful when switching the toolchain to build
        kernel since all files need to be recompiled.
        """
        with self:
            self.makefile.make('clean')

    def make_defconfig(self) -> None:
        """Make the default configuration file."""
        with self:
            self.makefile.make(self.defconfig)

    def prepare(self) -> None:
        "Prepare the build environment."
        with self:
            self.makefile.make('prepare')

    def build_kbuild_image(self, log_dir: Optional[str]=None) -> None:
        """Make the kernel kbuild image.

       Args:
            log_dir: Directory of the build log file.
                The output of the compiler will be redirected
                to a file in this directory .

        Raises:
            CalledProcessError: If The target fails to build.
        """
        with self:
            Path(log_dir).mkdir(exist_ok=True)
            build_log = Path(log_dir, self.custom_release + '-log.txt')
            output = self.makefile.make_output('all')
            build_log.write_text(output)
