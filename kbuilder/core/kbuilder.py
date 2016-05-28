#!/usr/bin/env python3
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
import shutil
import sys
from subprocess import CalledProcessError, check_call

import arrow
from typing import Iterable
from unipath import Path

from kbuilder.core import gcc
from kbuilder.core.gcc import Toolchain
from kbuilder.core.kernel import Kernel
from kbuilder.core.messages import alert, highlight, success

VERSION = '{0}.{1}'.format(*sys.version_info[:2])

if VERSION < '3.5':
    print(alert('Python 3.5+ is required'))
    exit()


# The root of the kernel
KERNEL_ROOT_DIR = Kernel.find_root()

# This dirctory should contain the necessary tools for creating the kernel
RESOURSES_DIR = Path(KERNEL_ROOT_DIR, 'android', 'ota').resolve()

# The directory to export the package zip
DEF_EXPORT_DIR = Path(KERNEL_ROOT_DIR, '..', 'output').resolve()

TOOLCHAIN_DIR = Path(KERNEL_ROOT_DIR, '..', 'toolchains').resolve()

SUBLIME_N9_EXPORT_DIR = Path(os.getenv('SUBLIME_N9_EXPORT_DIR'))

# Directory for build logs
BUILD_LOG_DIR = Path(DEF_EXPORT_DIR, 'build_logs')


def make_boot_img(name: str, kbuild_image: str, ramdisk: str='ramdisk.img'):
    """Create a boot.img file that can be install via fastboot.

    Keyword arguments:
    name -- the name of the output file
    kbuild_image -- the compressed kernel image to include in the boot.img file
    ramdisk -- the ramdisk image to include in the boot.img file
    """
    previous_directory = os.getcwd()
    os.chdir(RESOURSES_DIR)
    args = '--output {} --kernel {} --ramdisk {}'.format(name, kbuild_image,
                                                         ramdisk)
    check_call('mkbootimg ' + args, shell=True)
    os.chdir(previous_directory)


def zip_ota_package(name: str, base_dir: str=os.getcwd()) -> str:
    """Create a zip package that can be installed via recovery.

    Return the path to the zip file created
    Keyword arguments:
    name -- the name of the zip file to create
    base_dir -- the directory whose contents should be zipped (default cwd)
    """
    output = shutil.make_archive(name, 'zip', base_dir)
    print(success('ota package created'))
    return output


def get_export_dir() -> str:
    """Return the directory to export the kernel."""
    if SUBLIME_N9_EXPORT_DIR:
        return SUBLIME_N9_EXPORT_DIR
    else:
        return DEF_EXPORT_DIR


def export_file(file_export: str, export_dir: str) -> None:
    """Send a file to the export directory.

    Keyword arguments:
    file_export -- the absolute path of the file to export
    export_dir -- the directory to export the file
    """
    file_path = Path(file_export)
    Path(export_dir).mkdir()
    check_call('mv {} {}'.format(file_path, export_dir), shell=True)
    print(success('{} exported to {}'.format(file_path.name, export_dir)))


def time_delta(func) -> None:
    """Time how long it takes to run a function."""
    def args_wrapper(*args, **kw_args):
        start_time = arrow.utcnow().timestamp
        func(*args, **kw_args)
        end_time = arrow.utcnow().timestamp
        time_delta = end_time - start_time
        minutes = highlight(time_delta // 60)
        seconds = highlight(time_delta % 60)
        print('Time passed: {} minute(s) and {} second(s)'.format(minutes,
                                                                  seconds))
    return args_wrapper


@time_delta
def build(kernel: Kernel, toolchains: Iterable[Toolchain], export_dir: str=None,
          ota_package_dir: str=None, build_log_dir: str=None) -> None:
    """Build the kernel with the given toolchains."""
    regenerate_defconfig = True
    kbuild_image = None
    clean = None
    if len(toolchains) > 1:
        clean = kernel.clean
    else:
        clean = kernel.arch_clean
    for toolchain in toolchains:
        clean(toolchain)
        if regenerate_defconfig:
            kbuild_image = kernel.build(toolchain, 'defconfig', build_log_dir)
            regenerate_defconfig = False

        else:
            kbuild_image = kernel.build(toolchain, build_log_dir)

        if ota_package_dir:
            shutil.copy(kbuild_image, ota_package_dir + '/boot')
            full_version = kernel.get_full_version(toolchain)
            zip_ota_package(Path(export_dir, full_version), ota_package_dir)


def main():
    """Build the kernel with the selected toolchains."""
    toolchains = gcc.scandir(TOOLCHAIN_DIR)
    toolchains = gcc.select(toolchains)
    kernel_root_dir = KERNEL_ROOT_DIR
    kernel_root_dir.chdir()
    kernel = Kernel(kernel_root_dir)
    export_dir = Path(get_export_dir(), kernel.version_numbers)
    try:
        DEF_EXPORT_DIR.mkdir()
        build(kernel, toolchains, export_dir,
              ota_package_dir=RESOURSES_DIR, build_log_dir=BUILD_LOG_DIR)

    except KeyboardInterrupt:
        print(alert('Exiting due to KeyboardInterrupt'))
        exit()


if __name__ == '__main__':
    main()
