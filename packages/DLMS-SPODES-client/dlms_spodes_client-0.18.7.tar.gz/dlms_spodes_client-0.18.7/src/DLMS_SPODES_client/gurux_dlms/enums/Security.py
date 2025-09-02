from enum import IntEnum


class Security(IntEnum):
    """Used security model."""
    #pylint: disable=too-few-public-methods
    # Transport security is not used.
    NONE = 0
    # Authentication security is used.
    AUTHENTICATION = 0x10
    # Encryption security is used.
    ENCRYPTION = 0x20
    # Authentication and Encryption security are used.
    AUTHENTICATION_ENCRYPTION = 0x30
