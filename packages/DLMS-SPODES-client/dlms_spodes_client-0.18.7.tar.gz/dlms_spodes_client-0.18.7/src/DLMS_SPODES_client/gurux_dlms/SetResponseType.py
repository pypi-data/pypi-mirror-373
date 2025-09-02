from enum import IntEnum


class SetResponseType(IntEnum):
    """Enumerates Set response types."""
    #
    # Normal set response.
    #
    NORMAL = 1

    #
    # Set response in data blocks.
    #
    DATA_BLOCK = 2

    #
    # Set response in last data block.
    #
    LAST_DATA_BLOCK = 3

    #
    # Set response in last data block with list.
    #
    LAST_DATA_BLOCK_WITH_LIST = 4

    #
    # Set with list response.
    #
    WITH_LIST = 5
