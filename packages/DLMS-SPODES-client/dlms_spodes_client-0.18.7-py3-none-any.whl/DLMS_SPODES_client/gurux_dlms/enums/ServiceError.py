from enum import IntEnum


class ServiceError(IntEnum):
    """DLMS service errors """
    OPERATION_NOT_POSSIBLE = 1
    SERVICE_NOT_SUPPORTED = 2
    OTHER_REASON = 3
