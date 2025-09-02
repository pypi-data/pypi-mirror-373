from enum import IntEnum


class LoadDataSet(IntEnum):
    """LoadDataSet describes load dataset errors."""
    OTHER = 0
    PRIMITIVE_OUT_OF_SEQUENCE = 1
    NOT_LOADABLE = 2
    DATASET_SIZE_TOO_LARGE = 3
    NOT_AWAITED_SEGMENT = 4
    INTERPRETATION_FAILURE = 5
    STORAGE_FAILURE = 6
    DATASET_NOT_READY = 7
