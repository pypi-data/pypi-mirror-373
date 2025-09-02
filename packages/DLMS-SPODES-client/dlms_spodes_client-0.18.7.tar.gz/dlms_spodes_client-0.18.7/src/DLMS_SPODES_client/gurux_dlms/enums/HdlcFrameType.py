from enum import IntEnum


class HdlcFrameType(IntEnum):
    """HDLC frame types."""

    I_FRAME = 0
    S_FRAME = 1
    U_FRAME = 3
