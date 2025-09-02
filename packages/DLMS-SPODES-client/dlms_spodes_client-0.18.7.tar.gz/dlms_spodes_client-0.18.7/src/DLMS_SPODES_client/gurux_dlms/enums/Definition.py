from enum import IntEnum


class Definition(IntEnum):
    """Definition describes definition errors."""
    OTHER = 0
    OBJECT_UNDEFINED = 1
    OBJECT_CLASS_INCONSISTENT = 2
    OBJECT_ATTRIBUTE_INCONSISTENT = 3
