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

"""Provide an interface for make commands"""

import os
import subprocess as sp
from subprocess import CompletedProcess


def make(build_target: str, *, jobs: int=os.cpu_count()) -> CompletedProcess:
    """Execute make in the shell and return a CompletedProcess object.

    A CalledProcessError exeception will be thrown if the return code is not 0.

    Positional arguments:
    build_target --  the target to build.

    Keyword arguments:
    jobs -- the amount of jobs to build with (default os.cpu_count()).
    """
    command = 'make -j{} {}'.format(jobs, build_target)
    return sp.check_call(command, shell=True)


def make_output(build_target: str, *, jobs: int=os.cpu_count()) -> str:
    """Execute make in the shell and return the output as a string.

    A CalledProcessError exeception will be thrown if the return code is not 0.

    Positional arguments:
    build_target --  the target to build.

    Keyword arguments:
    jobs -- the amount of jobs to build with (default os.cpu_count()).
    """
    command = 'make -j{} {}'.format(jobs, build_target)
    return sp.check_output(command, shell=True, universal_newlines=True)
