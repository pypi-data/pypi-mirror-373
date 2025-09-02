from enum import IntEnum


class Task(IntEnum):
    """Task describes load task errors."""
    OTHER = 0
    NO_REMOTE_CONTROL = 1
    TI_STOPPED = 2
    TI_RUNNING = 3
    TI_UNUSABLE = 4
