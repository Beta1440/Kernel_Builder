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
from subprocess import CompletedProcess, PIPE, run

from unipath.path import Path

from kbuilder.core.gcc import Toolchain
from kbuilder.core.messages import alert, success

KERNEL_DIRS = ['arch', 'crypto', 'Documentation', 'drivers', 'include',
               'scripts', 'tools']


def make(targets: str, jobs: int=os.cpu_count(),
         string_output: bool=True) -> CompletedProcess:
    """Execute make in the shell and return a CompletedProcess object.

    A CalledProcessError exeception will be thrown if the return code is not 0.
    Keyword arguments:
    jobs -- the amount of jobs to build with (default os.cpu_count())
    string_output -- If true, the stdout of the CompletedProcess will be a
        string. Otherwise, the stdout will be a bytes (default True).
    """
    command = 'make -j{} {}'.format(jobs, targets)
    return run(command, shell=True, stdout=PIPE,
               universal_newlines=string_output, check=True)


class Kernel(object):
    """store info for a kernel."""
    def __init__(self, root: str) -> None:
        """Initialze a new Kernel.

        Keyword arguments:
        root -- the root directory of the kernel
        """
        self.root = Path(root)
        self.name = self.root.name
        self.version = self._find_kernel_verion()
        self.version_numbers = self.version[-5:]

    def _find_kernel_verion(self):
        with self:
            output = make('kernelrelease').stdout.rstrip()
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

    def get_full_version(self, toolchain: Toolchain) -> str:
        """Get the kernel version with the toolchain name appended.

        Keyword arguments:
        toolchain -- the toolchain to use
        """
        return '{}-{}'.format(self.version, toolchain.name)

    @staticmethod
    def find_root(path_name: str='') -> Path:
        """Find the root of the kernel directory.

        Recursively search for the root of the kernel directory. The search
        continues the kernel root is found or the system root directory is reached.
        If the system root directory is reached, then 'None' is returned.
        Otherwise, the path of the kernel root directory is returned.
        Keyword arguments
        path_name -- the name of the path to begin search in (default '')
        """
        def is_kernel_root(path: Path) -> bool:
            path_files = [file.name for file in os.scandir(path)]
            for dir in KERNEL_DIRS:
                if dir not in path_files:
                    return False
            return True

        def _find_kernel_root(path: Path=Path(os.getcwd())) -> Path:
            if is_kernel_root(path):
                return path
            elif path == Path('/'):
                return None
            else:
                return _find_kernel_root(path.parent)

        if path_name:
            return _find_kernel_root(Path(path_name))
        else:
            return _find_kernel_root()

    @staticmethod
    def arch_clean() -> CompletedProcess:
        """Remove compiled kernel files in the arch directory.

        This form of cleaning is useful for rebuilding the kernel with the same
        Toolchain, since only files that were changed will be compiled.
        Keyword arguements
        """
        print('Performing an arch clean')
        return make('archclean')

    @staticmethod
    def clean() -> CompletedProcess:
        """Remove all compiled kernel files.

        This form of cleaning is useful when switching the toolchain to build
        kernel since all files need to be recompiled.
        Keyword arguements
        """
        print('Removing all compiled files')
        return make('clean')

    def build(self, toolchain: Toolchain, build_log_dir: str=None) -> Path:
        """Build the kernel.

        Return the path of the absolute path of kbuild image if the build is
        successful.
        Keyword arguments:
        toolchain -- the toolchain to use in building the kernel
        defconfig -- the default configuration file (default '')
        build_log_dir --  the directory of the build log file
        """
        full_version = self.get_full_version(toolchain)
        Path(build_log_dir).mkdir()
        build_log = Path(build_log_dir, full_version + '-log.txt')

        try:
            print('compiling {0.version} with {1.name}'.format(self, toolchain))
            output = make('all').stdout
            build_log.write_file(output)
            print(success(full_version + ' compiled'))
            kbuild_image_path = Path(self.root, 'arch', toolchain.target_arch,
                                     'boot', 'Image.gz-dtb')
            return kbuild_image_path

        except:
            print(alert('{} failed to compile'.format(full_version)))
            exit()

        finally:
            print('the build log is located at ' + build_log)
