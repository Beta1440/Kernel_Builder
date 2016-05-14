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
import re
from subprocess import call, check_call, getoutput, run

from typing import Dict, List

from gcc import Toolchain, get_toolchains, select_toolchains
from messages import alert, highlight, success, info
from directories import (KERNEL_ROOT_DIR, DEF_EXPORT_DIR, TOOLCHAIN_DIR,
    SUBLIME_N9_EXPORT_DIR, BUILD_LOG_DIR, KBUILD_IMAGE, RESOURSES_DIR)
from kernel import Kernel, make

RAMDISK_IMG = 'ramdisk.img'


def make_defconfig(defconfig: str='defconfig') -> None:
    """Create a default configuration file."""
    print(info('making:'), highlight(defconfig))
    make(defconfig)


def make_boot_img(name : str, kbuild_image : str, ramdisk : str) -> None:
    """Create a boot.img file that can be install via fastboot

    Keyword arguments:
    name -- the name of the output file
    kbuild_image -- the compressed kernel image to include in the boot.img file
    ramdisk -- the ramdisk image to include in the boot.img file
    """
    previous_directory = os.getcwd()
    os.chdir(RESOURSES_DIR)
    run(['mkbootimg', '--output', name, '--kernel', kbuild_image,
         '--ramdisk', ramdisk], shell=True)
    os.chdir(previous_directory)


def zip_ota_package(name: str, kbuild_image: str) -> str:
    """Create a zip package that can be installed via recovery

    Return the path to the zip file created
    Keyword arguments:
    name -- the name of the zip file to create
    kbuild_image -- the path to the compressed kernel image
    """
    try:
        previous_directory = os.getcwd()
        check_call('cp {} {}'.format(kbuild_image, RESOURSES_DIR + '/boot'), shell=True)
        os.chdir(RESOURSES_DIR)
        check_call('zip {0} META-INF {1} config {1} boot {1}'.format(name, '-r'),
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
    kernel_info -- a dictionary containing the kernel's version
    """
    kernel_file = os.path.join(RESOURSES_DIR, file_export)
    base_export_dir = get_export_dir()
    final_export_dir = os.path.join(base_export_dir, kernel_version_number, '')
    if not os.path.isdir(final_export_dir):
        os.mkdir(final_export_dir)

    run('mv {} {}'.format(kernel_file, final_export_dir), shell=True)
    exported_file = os.path.join(final_export_dir, file_export)
    if os.path.isfile(exported_file):
        print(success('{} exported to {}'.format(file_export,
                                                 final_export_dir)))
    else:
        print(alert('{} could not be exported to {}'.format(file_export,
                                                            final_export_dir)))


# Get the current time
def get_current_time():
    return int(getoutput('echo $(date +"%s")'))


# get the difference for the current time and the time set earlier
def get_time_since(start_time):
    date_end = get_current_time()
    return date_end - start_time


def print_time(time) -> None:
    """Print the duration of the given time.

    Keyword arguments:
    time -- the time to print out"""
    minutes = highlight(str(time // 60))
    seconds = highlight(str(time % 60))
    print('Time passed: {} minute(s) and {} seconds'.format(minutes, seconds))


def main():
    toolchains = get_toolchains(TOOLCHAIN_DIR)
    toolchains = select_toolchains(toolchains)
    regenerate_defconfig = True
    kernel = Kernel(KERNEL_ROOT_DIR)
    for toolchain in toolchains:
        try:
            os.putenv('CROSS_COMPILE', toolchain.compiler_prefix)

            if regenerate_defconfig:
                make_defconfig()
                regenerate_defconfig = False

            start_time = get_current_time()
            if not os.path.isdir(DEF_EXPORT_DIR):
                os.mkdir(DEF_EXPORT_DIR)

            kernel.build(toolchain)
            full_version = kernel.get_full_version(toolchain)
            zip_ota_package(full_version + '.zip', KBUILD_IMAGE)
            export_file(full_version + '.zip', kernel.version_numbers)

        except KeyboardInterrupt:
            exit()

        finally:
            print_time(get_time_since(start_time))

if __name__ == '__main__':
    main()
