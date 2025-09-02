from enum import IntEnum


class HardwareResource(IntEnum):
    """Hardware resource describes hardware errors."""
    OTHER = 0
    MEMORY_UNAVAILABLE = 1
    PROCESSOR_RESOURCE_UNAVAILABLE = 2
    MASS_STORAGE_UNAVAILABLE = 3
    OTHER_RESOURCE_UNAVAILABLE = 4
