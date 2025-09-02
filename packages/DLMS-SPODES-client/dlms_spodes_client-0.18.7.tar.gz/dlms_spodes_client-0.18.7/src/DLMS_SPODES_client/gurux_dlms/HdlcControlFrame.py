from enum import IntEnum


class HdlcControlFrame(IntEnum):
    """HDLC control frame types."""
    RECEIVE_READY = 0
    RECEIVE_NOT_READY = 1
    REJECT = 2
    SELECTIVE_REJECT = 3
