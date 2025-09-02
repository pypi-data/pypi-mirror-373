from enum import IntEnum


class MBusCommand(IntEnum):
    """M-Bus command."""
    SND_NR = 0x44
    SND_UD2 = 0x43
    RSP_UD = 0x08
