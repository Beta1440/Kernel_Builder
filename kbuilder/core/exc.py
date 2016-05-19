"""Kernel Builder exception classes."""

class KbuilderError(Exception):
    """Generic errors."""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg

class KbuilderConfigError(KbuilderError):
    """Config related errors."""
    pass

class KbuilderRuntimeError(KbuilderError):
    """Generic runtime errors."""
    pass

class KbuilderArgumentError(KbuilderError):
    """Argument related errors."""
    pass
