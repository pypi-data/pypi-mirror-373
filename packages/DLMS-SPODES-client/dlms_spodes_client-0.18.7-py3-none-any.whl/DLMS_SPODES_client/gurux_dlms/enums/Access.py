from enum import IntEnum


class Access(IntEnum):
    """
    Access describes access errors.
    """
    OTHER = 0
    SCOPE_OF_ACCESS_VIOLATED = 1
    OBJECT_ACCESS_INVALID = 2
    HARDWARE_FAULT = 3
    OBJECT_UNAVAILABLE = 4
