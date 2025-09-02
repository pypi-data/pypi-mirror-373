from enum import IntEnum


class ResponseType(IntEnum):
    """ IS/IEC 62056-53 : 2006 """
    NORMAL = 1
    WITH_DATABLOCK = 2
    WITH_LIST = 3
