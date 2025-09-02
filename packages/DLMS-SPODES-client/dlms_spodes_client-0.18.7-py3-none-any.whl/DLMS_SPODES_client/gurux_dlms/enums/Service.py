from enum import IntEnum


class Service(IntEnum):
    """Service describes service errors."""
    #pylint: disable=too-few-public-methods
    # Other error.
    OTHER = 0
    # PDU size is wrong.
    PDU_SIZE = 1
    # Service is unsupported.
    UNSUPPORTED = 2

    @classmethod
    def valueofString(cls, value):
        return Service[value.upper()]
