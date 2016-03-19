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

from termcolor import colored
from typing import Dict, List

from gcc import Toolchain

def alert(message):
    """Indicate when a process has failed"""
    return colored(message, 'red')

def highlight(message):
    """Highlight useful information"""
    return colored(message, 'yellow')

def success(message):
    """Notify user when a process is successful"""
    return colored(message, 'green')

def info(message):
    """Print general information"""
    return colored(message, 'blue')

# The root of the kernel
KERNEL_ROOT_DIR = os.getcwd()

# This dirctory should contain the necessary tools for creating the kernel
RESOURSES_DIR = os.path.join(KERNEL_ROOT_DIR, 'build', 'resources')

# The directory to export the package zip
DEF_EXPORT_DIR = os.path.join(KERNEL_ROOT_DIR, '..', 'output')

TOOLCHAIN_DIR = os.path.join(KERNEL_ROOT_DIR, '..', 'toolchains')

ARCH = 'arm64'

SUBLIME_N9_EXPORT_DIR = os.getenv('SUBLIME_N9_EXPORT_DIR')

# Directory for build logs
BUILD_LOG_DIR = os.path.join(DEF_EXPORT_DIR, 'build_logs')

# The kernel image file
Z_IMAGE = 'Image.gz-dtb'

# The absolute path to the kernel image file
Z_IMAGE = os.path.join(KERNEL_ROOT_DIR, 'arch', ARCH, 'boot', Z_IMAGE)

RAMDISK_IMG = 'ramdisk.img'

# Set the kernel version by reading the default configuration file
def get_kernel_version():
    return getoutput('make kernelrelease')[8:]


def get_toolchains(toolchain_dir : str) -> List[Toolchain]:
    """Get all the valid the toolchains in a directory.

    A toolchain is valid if it has a gcc executable in its "bin/" directory

    Keyword arguments:
    toolchain_dir -- the directory to look for toolchains
    """
    entries = os.scandir(toolchain_dir)
    toolchains = []
    serial_number = 1
    for entry in entries:
        toolchain = Toolchain(entry.path, serial_number, ARCH)
        if(toolchain.compiler_prefix):
            toolchains.append(toolchain)
            print(success('Toolchain located: '), highlight(toolchain.name))
            serial_number += 1

    return toolchains


def select_toolchains(toolchains : List[Toolchain]) -> List[Toolchain]:
    """Select which toolchains to use in compiling the kernel.

    The kernel will be compiled once with each toolchain selected.
    If only one toolchain is available, then it will be automatically selected.

    Keyword arguments:
    toolchains -- the list of toolchains to select from
    """
    if len(toolchains) <= 1:
        return toolchains

    for toolchain in toolchains:
        print(info('{}) {}'.format(toolchain.serial_number, toolchain.name)))

    selected_toolchains = []
    toolchain_numbers = input('Enter numbers separated by spaces: ')
    toolchains_to_select = [int(tc) for tc in toolchain_numbers.split()]
    for toolchain in toolchains:
        if toolchain.serial_number in toolchains_to_select:
            selected_toolchains.append(toolchain)

    return selected_toolchains


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
    run('make -j{} > {} 2>&1'.format(THREADS, kernel_info['build_log']),
        shell=True)

    if os.path.isfile(Z_IMAGE):
        print(success(kernel_info['version'] + ' compiled'))
    else:
        print(alert('{} failed to compile'.format(kernel_info['version'])))
        print(info('the build log is located at ' + kernel_info['build_log']))


def make_boot_img(name : str, z_image : str, ramdisk : str) -> None:
    """Create a boot.img file that can be install via fastboot

    Keyword arguments:
    name -- the name of the output file
    z_image -- the compressed kernel image to include in the boot.img file
    ramdisk -- the ramdisk image to include in the boot.img file
    """
    previous_directory = os.getcwd()
    os.chdir(RESOURSES_DIR)
    run(['mkbootimg', '--output', name, '--kernel', z_image,
         '--ramdisk', ramdisk], shell=True)
    os.chdir(previous_directory)


def zip_ota_package(name: str) -> str:
    """Create a zip package that can be installed via recovery

    Return the path to the zip file created
    Keyword arguments:
    name -- the name of the zip file to create
    """
    try:
        previous_directory = os.getcwd()
        check_call('cp {} {}'.format(Z_IMAGE, RESOURSES_DIR + '/boot'), shell=True)
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
            zip_ota_package(kernel_info['zip_id'])
            export_file(kernel_info['zip_id'], kernel_info)

        except KeyboardInterrupt:
            print_time(get_time_since(start_time))
            exit()

        finally:
            print_time(get_time_since(start_time))

if __name__ == '__main__':
    main()
