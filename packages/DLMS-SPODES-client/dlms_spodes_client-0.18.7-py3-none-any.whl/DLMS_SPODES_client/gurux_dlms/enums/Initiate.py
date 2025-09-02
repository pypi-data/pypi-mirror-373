from enum import IntEnum


class Initiate(IntEnum):
    """Initiate describes onitiate errors."""
    OTHER = 0
    DLMS_VERSION_TOO_LOW = 1
    INCOMPATIBLE_CONFORMANCE = 2
    PDU_SIZE_TOO_SHORT = 3
    REFUSED_BY_THE_VDE_HANDLER = 4
