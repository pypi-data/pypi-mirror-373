from enum import IntEnum


class ErrorCode(IntEnum):
    """Enumerates all DLMS error codes.
    https://www.gurux.fi/Gurux.DLMS.ErrorCodes
    """
    DISCONNECT_MODE = -4

    RECEIVE_NOT_READY = -3

    REJECTED = -2

    UNACCEPTABLE_FRAME = -1

    OK = 0

    HARDWARE_FAULT = 1

    TEMPORARY_FAILURE = 2

    READ_WRITE_DENIED = 3

    UNDEFINED_OBJECT = 4

    INCONSISTENT_CLASS = 9

    UNAVAILABLE_OBJECT = 11

    UNMATCHED_TYPE = 12

    ACCESS_VIOLATED = 13

    DATA_BLOCK_UNAVAILABLE = 14

    LONG_GET_OR_READ_ABORTED = 15

    NO_LONG_GET_OR_READ_IN_PROGRESS = 16

    LONG_SET_OR_WRITE_ABORTED = 17

    NO_LONG_SET_OR_WRITE_IN_PROGRESS = 18

    DATA_BLOCK_NUMBER_INVALID = 19

    OTHER_REASON = 250
