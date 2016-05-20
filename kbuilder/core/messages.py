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

"""A wrapper for termcolor colored objects."""

from termcolor import colored


def alert(message):
    """Indicate when a process has failed."""
    return colored(message, 'red')


def highlight(message):
    """Highlight useful information."""
    return colored(message, 'yellow')


def success(message):
    """Notify user when a process is successful."""
    return colored(message, 'green')
