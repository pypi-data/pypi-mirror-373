from dataclasses import dataclass
from DLMS_SPODES.enums import VariableAccessSpecification
from . import GXDLMSSettings, GXByteBuffer
from .enums.Command import Command


@dataclass
class GXDLMSSNParameters:
    settings: GXDLMSSettings
    command: Command
    count: int
    requestType: VariableAccessSpecification
    attributeDescriptor: GXByteBuffer
    data: GXByteBuffer | None

    def __post_init__(self):
        self.blockIndex = self.settings.blockIndex
        self.multipleBlocks = False
        """ Are there more data to send or more data to receive. """
        self.time = None
        """ Send date and time. This is used in Data notification messages. """
