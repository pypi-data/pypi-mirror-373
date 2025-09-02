from enum import IntFlag


class RequestTypes(IntFlag):
    """ RequestTypes enumerates the replies of the server to a client's request, indicating the request type."""
    NONE = 0
    DATABLOCK = 1
    FRAME = 2
    GBT = 4
