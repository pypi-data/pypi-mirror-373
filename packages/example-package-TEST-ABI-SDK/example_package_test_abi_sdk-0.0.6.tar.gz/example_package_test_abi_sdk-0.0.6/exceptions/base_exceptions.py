"""
Base SDK exceptions shared across projects.
"""


def print_from_exceptions():
    print("hello from exceptions")


class InvalidCredentialsException(Exception):
    """Raised when API credentials are invalid."""


class SFDCBadRequestException(Exception):
    """Raised when SFDC request is malformed or fails."""


class WrongJobTypeException(Exception):
    """Raised when a job type argument is invalid."""
