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
    SUBLIME_N9_EXPORT_DIR, BUILD_LOG_DIR, KBUILD_IMAGE)

RAMDISK_IMG = 'ramdisk.img'

# Set the kernel version by reading the default configuration file
def get_kernel_version():
    return getoutput('make kernelrelease')[8:]


# Get a set of variables which describe the kernel
def get_kernel_info(toolchain):
    kernel_version = get_kernel_version()
    kernel_id = '{}-{}'.format(kernel_version, toolchain.name)
    kernel_zip_id = kernel_id + '.zip'
    kernel_boot_img_id = kernel_id + '.img'
    kernel_build_log = os.path.join(BUILD_LOG_DIR,
                                    '{}-log.txt'.format(kernel_id))
    kernel_info = {'version' : kernel_version,
                   'id' : kernel_id,
                   'zip_id' : kernel_zip_id,
                   'boot_img_id' : kernel_boot_img_id,
                   'build_log' : kernel_build_log}
    return kernel_info


def make_defconfig(defconfig: str='defconfig') -> None:
    """Create a default configuration file."""
    print(info('making:'), highlight(defconfig))
    call('make ' + defconfig, shell=True)

def clean_build_enviornment() -> None:
    """Remove old kernel files."""
    print(info('cleaning the build enviornment'))
    run('make archclean', shell = True)

def make_kernel(kernel_info, toolchain) -> None:
    """Compile the kernel.

    Compile the kernel with a given toolchain. The amount of jobs to run "make"
    is equal to the amount of CPU's available on the host computer. The output
    of the "make" command will be redirected to a build log file

    Keyword arguments:
    kernel_info -- Dictionary containing information for compiling the kernel
    toolchain -- the toolchain to compile the kernel with

    """
    THREADS = os.cpu_count()
    clean_build_enviornment()
    if not os.path.isfile('.config'):
        # Make sure the last defconfig is used
        print(info('Recreating last defconfig'))
        run('make oldconfig', shell=True)

    compile_info = 'compiling {} with {}'.format(
        kernel_info['version'],
        toolchain.name)
    print(info(compile_info))
    # redirect the output to the build log file
    if not os.path.isdir(BUILD_LOG_DIR):
        os.mkdir(BUILD_LOG_DIR)
    try:
        check_call('make -j{} > {} 2>&1'.format(THREADS, kernel_info['build_log']),
                   shell=True)
        print(success(kernel_info['version'] + ' compiled'))

    except:
        print(alert('{} failed to compile'.format(kernel_info['version'])))

    finally:
        print(info('the build log is located at ' + kernel_info['build_log']))


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

def export_file(file_export : str, kernel_info : Dict[str, str]) -> None:
    """Send a file to the export directory.

    Keyword arguments:
    file_export -- the file to export
    kernel_info -- a dictionary containing the kernel's version
    """
    kernel_file = os.path.join(RESOURSES_DIR, file_export)
    base_export_dir = get_export_dir()
    final_export_dir = os.path.join(base_export_dir,
                                    kernel_info['version'][-5:], '')
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
    for toolchain in toolchains:
        try:
            os.putenv('CROSS_COMPILE', toolchain.compiler_prefix)
            kernel_info = get_kernel_info(toolchain)

            if regenerate_defconfig:
                make_defconfig()
                regenerate_defconfig = False

            start_time = get_current_time()
            if not os.path.isdir(DEF_EXPORT_DIR):
                os.mkdir(DEF_EXPORT_DIR)

            make_kernel(kernel_info, toolchain)
            zip_ota_package(kernel_info['zip_id'], KBUILD_IMAGE)
            export_file(kernel_info['zip_id'], kernel_info)

        except KeyboardInterrupt:
            print_time(get_time_since(start_time))
            exit()

        finally:
            print_time(get_time_since(start_time))

if __name__ == '__main__':
    main()
