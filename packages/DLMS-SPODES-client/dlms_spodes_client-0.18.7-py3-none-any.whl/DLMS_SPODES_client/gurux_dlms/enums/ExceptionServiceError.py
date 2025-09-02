from enum import IntEnum


class ExceptionServiceError(IntEnum):
    """DLMS service errors."""
    #pylint: disable=too-few-public-methods

    OPERATION_NOT_POSSIBLE = 1

    SERVICE_NOT_SUPPORTED = 2

    OTHER_REASON = 3
