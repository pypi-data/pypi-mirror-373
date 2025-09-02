from enum import IntEnum


class VdeStateError(IntEnum):
    """VdeState error describes Vde state errors."""
    OTHER = 0
    NO_DLMS_CONTEXT = 1
    LOADING_DATASET = 2
    STATUS_NO_CHANGE = 3
    STATUS_INOPERABLE = 4
