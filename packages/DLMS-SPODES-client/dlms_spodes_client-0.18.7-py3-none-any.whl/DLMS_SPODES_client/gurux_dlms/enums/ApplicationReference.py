from enum import IntEnum


class ApplicationReference(IntEnum):
    """
    Application reference describes application errors.
    """
    OTHER = 0
    TIME_ELAPSED = 1
    APPLICATION_UNREACHABLE = 2
    APPLICATION_REFERENCE_INVALID = 3
    APPLICATION_CONTEXT_UNSUPPORTED = 4
    PROVIDER_COMMUNICATION_ERROR = 5
    DECIPHERING_ERROR = 6
