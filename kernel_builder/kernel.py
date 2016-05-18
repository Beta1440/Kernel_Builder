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

from typing import Any, Optional
from unipath.path import Path

from gcc import Toolchain
from messages import alert, highlight, info, success

KERNEL_DIRS = ['arch', 'crypto', 'Documentation', 'drivers', 'include',
               'scripts', 'tools']


def temp_visit(path_name: str) -> Optional[Any]:
    """Temporarily visit a path and perform some actions."""
    def func_wrapper(func):
        def arg_wrapper(*args, **kwargs):
            orig_path = os.getcwd()
            os.chdir(path_name)
            output = func(*args, **kwargs)
            os.chdir(orig_path)
            return output
        return arg_wrapper
    return func_wrapper


def find_kernel_root(path_name: str='') -> Path:
    """Find the root of the kernel directory.

    Recursively search for the root of the kernel directory. The search
    continues the kernel root is found or the system root directory is reached.
    If the system root directory is reached, then 'None' is returned.
    Otherwise, the path of the kernel root directory is returned.
    Keyword arguments
    path_name -- the name of the path to begin search in (default '')
    """
    def is_kernel_root(path: Path) -> bool:
        entries = os.scandir(path)
        entry_names = [entry.name for entry in entries]
        for dir in KERNEL_DIRS:
            if dir not in entry_names:
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


def make(targets: str, jobs: int=os.cpu_count(),
         string_output: bool=True, log_file: str=None) -> CompletedProcess:
    """Execute make in the shell and return a CompletedProcess object.

    A CalledProcessError exeception will be thrown if the return code is not 0.
    Keyword arguments:
    jobs -- the amount of jobs to build with (default os.cpu_count())
    string_output -- If true, the stdout of the CompletedProcess will be a
        string. Otherwise, the stdout will be a bytes (default True).
    log_file -- The output of the terminal is redirected to this path (default None).
    """
    command = 'make -j{} {}'.format(jobs, targets)
    if log_file:
        command += ' > {} 2>&1'.format(log_file)
    return run(command, shell=True, stdout=PIPE,
               universal_newlines=string_output, check=True)


def clean(toolchain: Toolchain, full_clean: bool=True) -> None:
    """Remove old kernel files."""
    print(info('cleaning the build enviornment'))
    toolchain.set_as_active()
    if full_clean:
        make('clean')
    else:
        make('archclean')


class Kernel(object):
    """store info for a kernel."""

    def __init__(self, root: str, arch: str='arm64') -> None:
        """Initialze a new Kernel.

        Keyword arguments:
        root -- the root directory of the kernel
        arch -- the architure of the kernel (default 'arm64')
        """
        self.arch = arch
        self.root = root
        self.version = self._find_kernel_verion()
        self.version_numbers = self.version[-5:]

    def _find_kernel_verion(self):
        @temp_visit(self.root)
        def _find_verion(command='kernelrelease'):
            return make(command).stdout.rstrip()[8:]
        return _find_verion()

    def get_full_version(self, toolchain: Toolchain) -> str:
        """Get the kernel version with the toolchain name appended.

        Keyword arguments:
        toolchain -- the toolchain to use
        """
        return '{}-{}'.format(self.version, toolchain.name)

    def build(self, toolchain: Toolchain, defconfig: str='',
              build_log_dir: str='') -> Path:
        """Build the kernel.

        Return the path of the absolute path of kbuild image if the build is
        successful.
        Keyword arguments:
        toolchain -- the toolchain to use in building the kernel
        defconfig -- the default configuration file (default '')
        build_log_dir --  the directory of the build log file
        """
        toolchain.set_as_active()

        if defconfig:
            print(info('making: '), highlight(defconfig))
            make(defconfig)

        full_version = self.get_full_version(toolchain)

        compile_info = 'compiling {} with {}'.format(self.version,
                                                     toolchain.name)
        print(info(compile_info))

        Path(build_log_dir).mkdir()

        build_log = Path(build_log_dir, full_version + '-log.txt')
        try:
            make('all', log_file=build_log).stdout
            print(success(full_version + ' compiled'))
            kbuild_image_path = Path(self.root, 'arch', toolchain.target_arch,
                                     'boot', 'Image.gz-dtb')
            return kbuild_image_path

        except:
            print(alert('{} failed to compile'.format(full_version)))
            exit()

        finally:
            print(info('the build log is located at ' + build_log))
