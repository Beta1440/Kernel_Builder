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
import sys
from subprocess import check_call

import arrow

from directories import (DEF_EXPORT_DIR, KBUILD_IMAGE, KERNEL_ROOT_DIR,
                         RESOURSES_DIR, SUBLIME_N9_EXPORT_DIR, TOOLCHAIN_DIR)
from gcc import get_toolchains, select_toolchains
from kernel import Kernel, make
from messages import alert, highlight, info, success

VERSION = '{0}.{1}'.format(*sys.version_info[:2])

if VERSION < '3.5':
    print(alert('Python 3.5+ is required'))
    exit()


def make_defconfig(defconfig: str='defconfig') -> None:
    """Create a default configuration file."""
    print(info('making:'), highlight(defconfig))
    make(defconfig)


def make_boot_img(name: str, kbuild_image: str, ramdisk: str='ramdisk.img'):
    """Create a boot.img file that can be install via fastboot.

    Keyword arguments:
    name -- the name of the output file
    kbuild_image -- the compressed kernel image to include in the boot.img file
    ramdisk -- the ramdisk image to include in the boot.img file
    """
    previous_directory = os.getcwd()
    os.chdir(RESOURSES_DIR)
    args = '--output {} --kernel {} --ramdisk '.format(name, kbuild_image,
                                                       ramdisk)
    check_call('mkbootimg ' + args, shell=True)
    os.chdir(previous_directory)


def zip_ota_package(name: str, kbuild_image: str) -> str:
    """Create a zip package that can be installed via recovery.

    Return the path to the zip file created
    Keyword arguments:
    name -- the name of the zip file to create
    kbuild_image -- the path to the compressed kernel image
    """
    try:
        previous_directory = os.getcwd()
        check_call('cp {} {}'.format(kbuild_image, RESOURSES_DIR + '/boot'),
                   shell=True)
        os.chdir(RESOURSES_DIR)
        check_call('zip {0} META-INF -r config -r boot -r'.format(name),
                   shell=True)
        print(success('ota package successfully created'))
        return os.path.abspath(name)
    except:
        print(alert('ota package could not be created'))

    finally:
        os.chdir(previous_directory)


# Determine the directory to export the kernel file
# If SUBLIME_N9_EXPORT_DIR is not specified, then the output folder
# will be set as the export directory
def get_export_dir():
    if SUBLIME_N9_EXPORT_DIR:
        return SUBLIME_N9_EXPORT_DIR
    else:
        return DEF_EXPORT_DIR


def export_file(file_export: str, kernel_version_number: int) -> None:
    """Send a file to the export directory.

    Keyword arguments:
    file_export -- the file to export
    kernel_version_number -- the version number of the kernel
    """
    kernel_file = os.path.join(RESOURSES_DIR, file_export)
    base_export_dir = get_export_dir()
    final_export_dir = os.path.join(base_export_dir, kernel_version_number, '')
    if not os.path.isdir(final_export_dir):
        os.mkdir(final_export_dir)

    check_call('mv {} {}'.format(kernel_file, final_export_dir), shell=True)
    exported_file = os.path.join(final_export_dir, file_export)
    if os.path.isfile(exported_file):
        print(success('{} exported to {}'.format(file_export,
                                                 final_export_dir)))
    else:
        print(alert('{} could not be exported to {}'.format(file_export,
                                                            final_export_dir)))


def print_time_delta(start_time: int, end_time: int) -> None:
    """Print the duration of the given time.

    Keyword arguments:
    start_time -- the timestamp of the start time
    end_time -- the timestamp of the end time
    """
    time_delta = end_time - start_time
    minutes = highlight(time_delta // 60)
    seconds = highlight(time_delta % 60)
    print('Time passed: {} minute(s) and {} seconds'.format(minutes, seconds))


def main():
    toolchains = get_toolchains(TOOLCHAIN_DIR)
    toolchains = select_toolchains(toolchains)
    regenerate_defconfig = True
    kernel = Kernel(KERNEL_ROOT_DIR)
    for toolchain in toolchains:
        try:
            toolchain.set_as_active()

            if regenerate_defconfig:
                make_defconfig()
                regenerate_defconfig = False

            start_time = arrow.utcnow().timestamp
            if not os.path.isdir(DEF_EXPORT_DIR):
                os.mkdir(DEF_EXPORT_DIR)

            kernel.build(toolchain)
            full_version = kernel.get_full_version(toolchain)
            zip_ota_package(full_version + '.zip', KBUILD_IMAGE)
            export_file(full_version + '.zip', kernel.version_numbers)

        except KeyboardInterrupt:
            exit()

        finally:
            end_time = arrow.utcnow().timestamp
            print_time_delta(start_time, end_time)


if __name__ == '__main__':
    main()
