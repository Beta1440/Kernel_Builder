"""GNU make invocation.

This module facilitates invoking the GNU make shell command.

Example:
    .. code-block:: python
        from kbuilder.core.make import make

        make('all', jobs=8)
"""

import os
from subprocess import check_call, check_output, CompletedProcess


def make(recipe: str, *, jobs: int=os.cpu_count()) -> CompletedProcess:
    """Execute a make recipe in the shell.

    Args:
        recipe: Recipe to invoke.
        jobs: Amount of threads to invoke recipe (default os.cpu_count()).

    Raises:
          A CalledProcessError if the recipe is unsuccessful.

    Returns:
          A CompletedProcess object.
    """
    command = _format_make_command(recipe, jobs=jobs)
    return check_call(command, shell=True)


def make_output(recipe: str, *, jobs: int=os.cpu_count()) -> str:
    """Execute a make recipe in the shell and return output.

    Args:
        recipe: Recipe to invoke.
        jobs: Amount of threads to invoke recipe (default os.cpu_count()).

    Raises:
          A CalledProcessError if the recipe is unsuccessful.

    Returns:
          Output of make with trailing whitespace trimmed.
    """
    command = _format_make_command(recipe, jobs=jobs)
    return check_output(command, shell=True, universal_newlines=True).rstrip()


def make_output_last_line(*args, **kwargs) -> str:
    """Execute a make recipe in the shell and return output.

    Args:
        recipe: Recipe to invoke.
        jobs: Amount of threads to invoke recipe (default os.cpu_count()).

    Raises:
          A CalledProcessError if the recipe is unsuccessful.

    Returns:
          Last line of output of make with trailing whitespace trimmed.
    """
    return last_line(make_output(*args, **kwargs))

    def last_line(output: str) -> str:
        return output.split('\n')[-1]


def _format_make_command(recipe: str, *, jobs: int) -> str:
    return 'make {} -j{}'.format(recipe, jobs)
