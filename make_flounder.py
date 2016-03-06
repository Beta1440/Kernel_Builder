#!/usr/bin/env python3.5
import os
import re
from subprocess import getoutput
from termcolor import colored

# Set colors
WARNING_COLOR = 'orange'
INFORMATION_COLOR = 'blue'
HIGHLIGHT_COLOR = 'yellow'
SUCCESS_COLOR = 'green'
FAILURE_COLOR = 'red'

# The root of the kernel
KERNEL_ROOT_DIR = os.getcwd()

# This dirctory should contain the necessary tools for creating the kernel
RESOURSES_DIR = os.path.join(KERNEL_ROOT_DIR, 'build', 'resources')

# The directory to export the package zip
DEF_EXPORT_DIR = os.path.join(KERNEL_ROOT_DIR, '..', 'output')

TOOLCHAIN_DIR = os.path.join(KERNEL_ROOT_DIR, '..', 'toolchains')
DEFCONFIG = 'sublime_defconfig'

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
def get_kernel_version(kernel_defconfig):
    with open(kernel_defconfig, 'r') as defconfig:
        local_version = 'CONFIG_LOCALVERSION='
        for line in defconfig:
            if line.startswith(local_version):
                # return the part of the statment after the CONFIG_LOCALVERSION
                return line[len(local_version) + 2 : -2]


# Take in a list of dir entries and return an array of valid toolchain roots
def get_valid_toolchains(toolchains):
    valid_toolchains = []
    for toolchain in toolchains:
        if os.path.isdir(toolchain.path):
            cross_compiler_prefix = get_cross_compile(toolchain.name)
            if cross_compiler_prefix:
                possible_gcc = get_cross_compile(toolchain.name) + 'gcc'
                if os.path.isfile(possible_gcc):
                    valid_toolchains.append(toolchain.path)
                    print(colored('Toolchain located:', SUCCESS_COLOR),
                          colored(toolchain.name, HIGHLIGHT_COLOR))

    if not valid_toolchains:
        print(colored('No toolchains could be located in {}'.format(TOOLCHAIN_DIR)))

    return sorted(valid_toolchains)

# Take an array of valid toolchain roots and select toolchains to use
def select_toolchains(toolchains):
    if len(toolchains) == 1:
        return toolchains

    counter = 1
    toolchain_tuples = []
    for toolchain in toolchains:
        toolchain_root = os.path.basename(toolchain)
        print(colored('{}) {}'.format(counter, toolchain_root),
                      INFORMATION_COLOR))
        toolchain_tuples.append((counter, toolchain_root))
        counter += 1

    selected_toolchains = []
    toolchain_numbers = input('Enter numbers separated by spaces: ')
    toolchains_to_select = [int(tc) for tc in toolchain_numbers.split()]
    for (index, toolchain) in toolchain_tuples:
        if index in toolchains_to_select:
            selected_toolchains.append(toolchain)

    return selected_toolchains


# Get the gcc version of the cross compiler
def get_gcc_version(cross_compile):
    GET_GCC = 'gcc -dumpversion'
    return getoutput(cross_compile + GET_GCC)

# Get the CROSS_COMPILE variable used by the make scripts to compile the kernel
def get_cross_compile(toolchain):
    toolchain_binaries_dir = os.path.join(TOOLCHAIN_DIR, toolchain, 'bin')
    binaries = os.scandir(toolchain_binaries_dir)
    for binary in binaries:
        if binary.name.startswith('aarch64') and binary.name.endswith('gcc'):
            return binary.path[:-3]

# Get information from a toolchain
def get_toolchain_info(toolchain):
    cross_compiler_prefix = get_cross_compile(toolchain)
    gcc_version = get_gcc_version(cross_compiler_prefix)
    gcc_type = 'ubertc'

    return {'cross_compiler_prefix': cross_compiler_prefix,
            'gcc_version': gcc_version,
            'gcc_type' : gcc_type}

# Get a set of variables which describe the kernel
def get_kernel_info(defconfig, toolchain_info):
    defconfig_path = os.path.join(KERNEL_ROOT_DIR,'arch', ARCH, 'configs', defconfig)
    kernel_version = get_kernel_version(defconfig_path)
    kernel_id = '{}-{}-{}'.format(kernel_version,
                                      toolchain_info['gcc_type'],
                                      toolchain_info['gcc_version'])
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


# Make the default configuration file
def make_defconfig(defconfig):
    print(colored('making:', INFORMATION_COLOR),
          colored(defconfig, HIGHLIGHT_COLOR))
    os.system('make {}'.format(defconfig))

# Remove old build files included the previous Z_IMAGE
def clean_build_enviornment():
    print(colored('cleaning the build enviornment', INFORMATION_COLOR))
    os.system('make clean')
    if os.path.isfile(Z_IMAGE):
        os.remove(Z_IMAGE)

# build the kernel
def make_kernel(kernel_info, toolchain_info):
    THREADS = os.cpu_count()
    clean_build_enviornment()
    if not os.path.isfile('.config'):
        # Make sure the last defconfig is used
        print(colored('Recreating last defconfig', INFORMATION_COLOR))
        os.system('make oldconfig')

    compile_info = 'compiling {} with {} {}'.format(
        kernel_info['version'],
        toolchain_info['gcc_type'],
        toolchain_info['gcc_version'])
    print(colored(compile_info, INFORMATION_COLOR))
    # redirect the output to the build log file
    if not os.path.isdir(BUILD_LOG_DIR):
        os.mkdir(BUILD_LOG_DIR)
    os.system('make -j{} > {} 2>&1'.format(THREADS, kernel_info['build_log']))

    if os.path.isfile(Z_IMAGE):
        success('{} compiled'.format(kernel_info['version']))
    else:
        failure('{} failed to compile'.format(kernel_info['version']))
        print(colored('the build log is located at {}'.format(
            kernel_info['build_log']), INFORMATION_COLOR))


# make a boot img that can be installed via fastboot
def make_boot_img(name):
    previous_directory = os.getcwd()
    os.chdir(RESOURSES_DIR)
    os.system('mkbootimg --output {} --kernel {} --ramdisk {}'.format(name,
                                                                      Z_IMAGE,
                                                                      RAMDISK))
    os.chdir(previous_directory)


# Create a ZIP package that can be installed via recovery
def make_zip(zip_id):
    if os.path.isfile(Z_IMAGE):
        previous_directory = os.getcwd()
        os.system('cp {} {}'.format(Z_IMAGE, RESOURSES_DIR + '/boot'))
        os.chdir(RESOURSES_DIR)
        os.system('zip {} {} -r {} -r {} -r'.format(zip_id,
                                                    'META-INF', 'config',
                                                    'boot'))
        success('zip successfully created')

        # return to the original directories if other kernels
        # need to be built
        os.chdir(previous_directory)
    else:
        failure('zip could not be created')

# Determine the directory to export the kernel file
# If SUBLIME_N9_EXPORT_DIR is not specified, then the output folder
# will be set as the export directory
def get_export_dir():
    if SUBLIME_N9_EXPORT_DIR:
        return SUBLIME_N9_EXPORT_DIR
    else:
        return DEF_EXPORT_DIR

# send a file to the export directory
def export_file(file_export, kernel_info):
    kernel_file = os.path.join(RESOURSES_DIR, file_export)
    base_export_dir = get_export_dir()
    final_export_dir = os.path.join(base_export_dir,
                                    kernel_info['version'][-5:], '')
    if not os.path.isdir(final_export_dir):
        os.mkdir(final_export_dir)

    os.system('mv {} {}'.format(kernel_file, final_export_dir))
    exported_file = os.path.join(final_export_dir, file_export)
    if os.path.isfile(exported_file):
        success('{} exported to {}'.format(file_export, final_export_dir))
    else:
        failure('{} could not be exported to {}'.format(file_export,
                                                        final_export_dir))


# Indicate when a process is successful
def success(success_text):
    print('{0}\n{1}\n{0}'.format(colored('-' * len(success_text),
                                         SUCCESS_COLOR),
                            colored(success_text, SUCCESS_COLOR)))

# Indicate when a process has failed
def failure(failure_text):
    length = len(failure_text)
    print('{0}\n{1}\n{0}'.format(colored('-' * length, FAILURE_COLOR),
                            colored(failure_text, FAILURE_COLOR)))


# Get the current time
def get_current_time():
    return int(getoutput('echo $(date +"%s")'))


# get the difference for the current time and the time set earlier
def get_time_since(start_time):
    date_end = get_current_time()
    return date_end - start_time


# Print the amount of time that has passed
def print_time(time):
    minutes = colored(str(time // 60), HIGHLIGHT_COLOR)
    seconds = colored(str(time % 60), HIGHLIGHT_COLOR)
    print('Time passed: {} minute(s) and {} seconds'.format(minutes, seconds))


def main():
    valid_toolchains = get_valid_toolchains(os.scandir(TOOLCHAIN_DIR))
    make_defconfig(DEFCONFIG)
    toolchains = select_toolchains(valid_toolchains)
    for toolchain in toolchains:
        start_time = get_current_time()
        toolchain_info = get_toolchain_info(toolchain)
        os.environ['CROSS_COMPILE'] = toolchain_info['cross_compiler_prefix']
        kernel_info = get_kernel_info(DEFCONFIG, toolchain_info)
        if not os.path.isdir(DEF_EXPORT_DIR):
            os.mkdir(DEF_EXPORT_DIR)

        success('Ready to go')
        make_kernel(kernel_info, toolchain_info)
        make_zip(kernel_info['zip_id'])
        export_file(kernel_info['zip_id'], kernel_info)

        print_time(get_time_since(start_time))

if __name__ == '__main__':
    main()
