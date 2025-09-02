from enum import IntFlag


class TraceLevel(IntFlag):
    ###Specifies trace levels.###
    #pylint: disable=too-few-public-methods

    OFF = 0x0
    ###Output no tracing and debugging messages.###

    ERROR = 0x1
    ###Output error-handling messages.###

    WARNING = 0x2
    ###Output warnings and error-handling messages.###

    INFO = 0x4
    ###Output informational messages, warnings, and error-handling messages.###

    VERBOSE = 0x8
    ###Output all debugging and tracing messages.###
