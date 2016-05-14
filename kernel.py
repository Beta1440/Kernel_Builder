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

from os import cpu_count, mkdir
from os.path import isdir, isfile, join
from subprocess import check_call, getoutput

from directories import BUILD_LOG_DIR, KERNEL_ROOT_DIR
from gcc import Toolchain
from messages import alert, highlight, info, success


def make(targets: str, jobs: int=cpu_count()) -> None:
    """Execute make in the shell"""
    check_call('make -j{} {}'.format(jobs, targets), shell=True)

def clean() -> None:
    """Remove old kernel files."""
    print(info('cleaning the build enviornment'))
    make('archclean')

class Kernel:
    """store info for a kerrnel"""
    def __init__(self, root: str, arch: str='arm64') -> None:
        self.version = getoutput('make kernelrelease')[8:]
        self.version_numbers = self.version[-5:]
        self.arch = arch
        self.root = root

    def get_full_version(self, toolchain: Toolchain):
        return '{}-{}'.format(self.version, toolchain.name)

    def build(self, toolchain: Toolchain):
        full_version = self.get_full_version(toolchain)
        build_log = join(BUILD_LOG_DIR,'{}-log.txt'.format(full_version))
        clean()
        if not isfile('.config'):
            # Make sure the last defconfig is used
            print(info('Recreating last defconfig'))
            make('oldconfig')

        compile_info = 'compiling {} with {}'.format(self.version,
            toolchain.name)
        print(info(compile_info))
        # redirect the output to the build log file
        if not isdir(BUILD_LOG_DIR):
            mkdir(BUILD_LOG_DIR)
        try:
            make('> {} 2>&1'.format(build_log))
            print(success(full_version + ' compiled'))

        except:
            print(alert('{} failed to compile'.format(full_version)))

        finally:
            print(info('the build log is located at ' + build_log))
