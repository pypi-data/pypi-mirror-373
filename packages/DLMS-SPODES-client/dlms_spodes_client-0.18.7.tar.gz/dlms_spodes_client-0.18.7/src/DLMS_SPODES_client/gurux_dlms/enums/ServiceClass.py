from enum import IntEnum


class ServiceClass(IntEnum):
    """Used service."""
    #pylint: disable=too-few-public-methods

    UN_CONFIRMED = 0
    CONFIRMED = 1
