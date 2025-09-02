from enum import IntEnum


class CountType(IntEnum):
    """
    Enumerate values that are add to counted GMAC.
    """

    # Total packet is created.
    PACKET = -1

    # Counted Tag is added.
    TAG = 0x1

    # Data is added.
    DATA = 0x2
