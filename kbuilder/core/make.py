"""GNU make invocation.

This module facilitates invoking the GNU make shell command.


Example:
    .. code-block:: python
        from kbuilder.core.make import make

        make('all', jobs=8)
"""
from unipath.path import Path

import os
from subprocess import check_call, check_output, CompletedProcess


class Makefile(object):
    """GNU makefile.

    Properties:
        path: the default path to invoke make command
    """
    def __init__(self, path: Path):
        self.path = path
        self._prev_path = None

    def __enter__(self):
        """Change the current directory the kernel root."""
        self._prev_path = Path(os.getcwd())
        self.path.chdir()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Revert the current directory to the original directory."""
        self._prev_path.chdir()
        return False

    def __bool__(self):
        """Check if the path property is set"""
        return bool(self.path)

    def make(self, *args, **kwargs):
        return make(*args, directory=self.path, **kwargs)

    def make_output(self, *args, **kwargs) -> str:
        return make_output(*args, directory=self.path, **kwargs)

    def make_output_last_line(self, *args, **kwargs) -> str:
        return make_output_last_line(*args, directory=self.path, **kwargs)


def make(recipe: str, *, jobs: int=os.cpu_count(), directory:  str='.', **kwargs) -> CompletedProcess:
    """Execute a make recipe in the shell.

    Args:
        recipe: Recipe to invoke.
        jobs: Amount of threads to invoke recipe (default os.cpu_count()).
        directory: The directory to invoke the make command.

    Raises:
          A CalledProcessError if the recipe is unsuccessful.

    Returns:
          A CompletedProcess object.
    """
    command = _format_make_command(recipe, jobs=jobs, directory=directory, **kwargs)
    return check_call(command, shell=True)


def make_output(recipe: str, *, jobs: int=os.cpu_count(), directory:  str='.', **kwargs) -> str:
    """Execute a make recipe in the shell and return output.

    Args:
        recipe: Recipe to invoke.
        jobs: Amount of threads to invoke recipe (default os.cpu_count()).
        directory: The directory to invoke the make command.

    Raises:
          A CalledProcessError if the recipe is unsuccessful.

    Returns:
          Output of make with trailing whitespace trimmed.
    """
    command = _format_make_command(recipe, jobs=jobs, directory=directory, **kwargs)
    return check_output(command, shell=True, universal_newlines=True).rstrip()


def make_output_last_line(*args, **kwargs) -> str:
    """Execute a make recipe in the shell and return output.

    Args:
        refer to make_output()

    Raises:
          A CalledProcessError if the recipe is unsuccessful.

    Returns:
          Last line of output of make with trailing whitespace trimmed.
    """
    return make_output(*args, **kwargs).split('\n')[-1]


def _format_make_command(recipe: str, *, jobs: int, directory:  str) -> str:
    return 'make {} -j{} -C {} --quiet'.format(recipe, jobs, directory)
