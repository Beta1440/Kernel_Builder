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
