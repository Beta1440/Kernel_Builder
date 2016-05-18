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

from os import getenv
from kernel import find_kernel_root

from unipath.path import Path

# The root of the kernel
KERNEL_ROOT_DIR = find_kernel_root()

# This dirctory should contain the necessary tools for creating the kernel
RESOURSES_DIR = Path(KERNEL_ROOT_DIR, 'resources').resolve()

# The directory to export the package zip
DEF_EXPORT_DIR = Path(KERNEL_ROOT_DIR, '..', 'output').resolve()

TOOLCHAIN_DIR = Path(KERNEL_ROOT_DIR, '..', 'toolchains').resolve()

SUBLIME_N9_EXPORT_DIR = Path(getenv('SUBLIME_N9_EXPORT_DIR'))

# Directory for build logs
BUILD_LOG_DIR = Path(DEF_EXPORT_DIR, 'build_logs')

# The absolute path to the kernel image file
KBUILD_IMAGE = Path(KERNEL_ROOT_DIR, 'arch', 'arm64', 'boot', 'Image.gz-dtb')
