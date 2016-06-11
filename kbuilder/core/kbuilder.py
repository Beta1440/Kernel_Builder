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
import kbuilder.core.make as mk
from kbuilder.core.messages import alert, highlight, success

VERSION = '{0}.{1}'.format(*sys.version_info[:2])

if VERSION < '3.5':
    print(alert('Python 3.5+ is required'))
    exit()


# The root of the kernel
KERNEL_ROOT_DIR = str(Kernel.find_root(os.getcwd()))
print(KERNEL_ROOT_DIR)

# This dirctory should contain the necessary tools for creating the kernel
RESOURSES_DIR = Path(KERNEL_ROOT_DIR, 'android', 'ota')

# The directory to export the package zip
DEF_EXPORT_DIR = Path(KERNEL_ROOT_DIR, '..', 'output').norm()

TOOLCHAIN_DIR = Path(KERNEL_ROOT_DIR, '..', 'toolchains').norm()

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
def build(kernel: Kernel, toolchains: Iterable[Toolchain],
          defconfig: str='defconfig', export_dir: str=None,
          ota_package_dir: str=None, build_log_dir: str=None) -> None:
    """Build the kernel with the given toolchains."""
    print('making: ' + highlight(defconfig))
    mk.make(defconfig)
    for toolchain in toolchains:
        with toolchain:
            kernel.arch_clean()
            kbuild_image, kernel_release = kernel.build(toolchain, build_log_dir)

            if ota_package_dir:
                shutil.copy(kbuild_image, ota_package_dir + '/boot')
                ota_package_path = Path(str(export_dir), kernel_release)
                zip_ota_package(ota_package_path, ota_package_dir)

def main():
    """Build the kernel with the selected toolchains."""
    toolchains = gcc.scandir(TOOLCHAIN_DIR)
    toolchains = gcc.select(toolchains)
    with Kernel(KERNEL_ROOT_DIR) as kernel:
        export_path = Path(get_export_dir(), kernel.version_numbers)
        DEF_EXPORT_DIR.mkdir(parents=True)
        build(kernel, toolchains, defconfig='defconfig', export_dir=export_path,
              ota_package_dir=RESOURSES_DIR, build_log_dir=BUILD_LOG_DIR)


if __name__ == '__main__':
    main()
