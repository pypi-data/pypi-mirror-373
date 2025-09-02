from enum import IntEnum


class StateError(IntEnum):
    """DLMS state errors."""
    SERVICE_NOT_ALLOWED = 1
    SERVICE_UNKNOWN = 2
