from __future__ import print_function
from ..gurux_dlms.GXCiphering import GXCiphering
from .enums import Priority, ServiceClass, Authentication, Standard
from DLMS_SPODES.hdlc.frame import Control
from DLMS_SPODES.enums import Conformance


class GXDLMSSettings:
    """ This class includes DLMS communication settings. """
    ctoSChallenge: bytes | None

    @classmethod
    def getInitialConformance(cls, useLN):
        if useLN:
            return Conformance.BLOCK_TRANSFER_WITH_ACTION | Conformance.BLOCK_TRANSFER_WITH_SET_OR_WRITE | Conformance.BLOCK_TRANSFER_WITH_GET_OR_READ | Conformance.SET | Conformance.SELECTIVE_ACCESS | Conformance.ACTION | Conformance.MULTIPLE_REFERENCES | Conformance.GET
        return Conformance.INFORMATION_REPORT | Conformance.READ | Conformance.UN_CONFIRMED_WRITE | Conformance.WRITE | Conformance.PARAMETERIZED_ACCESS | Conformance.MULTIPLE_REFERENCES

    def __init__(self, isServer: bool):
        self.customChallenges = False
        self.ctoSChallenge = None
        self.stoCChallenge = None
        self.sourceSystemTitle = None
        self.invokeId = 1
        self.longInvokeID = 0x1
        self.priority = Priority.HIGH
        self.serviceClass = ServiceClass.CONFIRMED
        self.clientAddress = 0
        self.serverAddress = 0
        self.pushClientAddress = 0
        self.serverAddressSize = 0
        self.__useLogicalNameReferencing = True
        self.authentication = Authentication.NONE
        self.password = None
        self.kek = None
        self.count = 0
        self.index = 0
        self.targetEphemeralKey = None
        self.dlmsVersion = 6
        """ deprecated """
        self.allowAnonymousAccess = False
        self.maxPduSize = 0xFFFF
        self.maxServerPDUSize = 0xFFFF
        self.startingPacketIndex = 1
        # Gets current block index.
        self.blockIndex = 1
        self.cipher = GXCiphering("ABCDEFGH".encode())
        self.blockNumberAck = 0
        self.protocolVersion = None
        self.isServer = isServer
        self.gateway = None
        self.proposedConformance = GXDLMSSettings.getInitialConformance(self.__useLogicalNameReferencing)
        self.resetFrameSequence()
        self.windowSize = 1
        self.userId = -1
        self.qualityOfService = 0
        """ deprecated """
        self.useUtc2NormalTime = False
        self.standard = Standard.DLMS
        self.negotiatedConformance = Conformance.NONE
        self.receiverFrame = Control.S0_R0  # 0
        self.senderFrame = Control.S0_R0      # 0
        self.command = 0
        self.commandType = 0
        self.useUtc2NormalTime = False

    def setCtoSChallenge(self, value):
        """ Client to Server challenge setter """
        if not self.customChallenges or self.ctoSChallenge is None:
            self.ctoSChallenge = value

    def getStoCChallenge(self):
        """ Server to Client challenge getter """
        return self.stoCChallenge

    def setStoCChallenge(self, value):
        """ Server to Client challenge setter """
        if not self.customChallenges or self.stoCChallenge is None:
            self.stoCChallenge = value

    def resetFrameSequence(self):
        if self.isServer:
            self.senderFrame = Control.S7_R0_PF
            self.receiverFrame = Control.S7_R7_PF
        else:
            self.senderFrame = Control.S7_R7_PF
            self.receiverFrame = Control.S7_R0_PF

    def getNextSend(self, is_first: bool) -> int:
        """  Generates I-frame. Is this first packet. """
        if is_first:
            self.senderFrame = Control.next_receiver_sequence(Control.next_send_sequence(self.senderFrame))
        else:
            self.senderFrame = Control.next_send_sequence(self.senderFrame)
        return self.senderFrame

    def getReceiverReady(self):
        """ Generates Receiver Ready S-frame """
        self.senderFrame = Control.next_receiver_sequence(self.senderFrame | 1)
        return self.senderFrame & 0xF1

    def getKeepAlive(self):
        """ Generates Keep Alive S-frame """
        self.senderFrame = (self.senderFrame | 1)
        return self.senderFrame & 0xF1

    #
    # Gets starting block index in HDLC framing.  Default is One based,
    #      but some
    # meters use Zero based value.  Usually this is not used.
    #
    # Current block index.
    #
    def getStartingPacketIndex(self):
        return self.startingPacketIndex

    #
    # Set starting block index in HDLC framing.  Default is One based,
    #      but some
    # meters use Zero based value.  Usually this is not used.
    #
    # @param value
    # Zero based starting index.
    #
    def setStartingPacketIndex(self, value):
        self.startingPacketIndex = value
        self.resetBlockIndex()

    #
    # Sets current block index.
    #
    # @param value
    # Block index.
    #
    def setBlockIndex(self, value):
        self.blockIndex = value

    #
    # Block number acknowledged in GBT.
    #
    def getBlockNumberAck(self):
        return self.blockNumberAck

    #
    # @param value
    # Block number acknowledged in GBT.
    #
    def setBlockNumberAck(self, value):
        self.blockNumberAck = value

    #
    # Resets block index to default value.
    #
    def resetBlockIndex(self):
        self.blockIndex = self.startingPacketIndex
        self.blockNumberAck = 0

    #
    # Increases block index.
    #
    def increaseBlockIndex(self):
        self.blockIndex += 1

    # Is Logical Name Referencing used.
    # Don't use property. For some reason Python 2.7 doesn't call it in Rasbperry PI.
    def getUseLogicalNameReferencing(self):
        return self.__useLogicalNameReferencing

    # Is Logical Name Referencing used.
    def setUseLogicalNameReferencing(self, value):
        if self.__useLogicalNameReferencing != value:
            self.__useLogicalNameReferencing = value
            self.proposedConformance = GXDLMSSettings.getInitialConformance(self.__useLogicalNameReferencing)

    #
    # @param value
    # update invoke ID.
    #
    def updateInvokeId(self, value):
        #pylint: disable=bad-option-value,redefined-variable-type
        if (value & 0x80) != 0:
            self.priority = Priority.HIGH
        else:
            self.priority = Priority.NORMAL
        if (value & 0x40) != 0:
            self.serviceClass = ServiceClass.CONFIRMED
        else:
            self.serviceClass = ServiceClass.UN_CONFIRMED
        self.invokeId = int((value & 0xF))

    #
    # @param value
    # Invoke ID.
    #
    def setInvokeID(self, value):
        if value > 0xF:
            raise ValueError("Invalid InvokeID")
        self.invokeId = int(value)

    #
    # Invoke ID.
    #
    def getLongInvokeID(self):
        return self.longInvokeID

    #
    # @param value
    # Invoke ID.
    #
    def setLongInvokeID(self, value):
        if value > 0xFFFFFFFF:
            raise ValueError("Invalid InvokeID")
        self.longInvokeID = value

    #
    # Source system title.
    #
    def getSourceSystemTitle(self):
        return self.sourceSystemTitle

    #
    # @param value
    # Source system title.
    #
    def setSourceSystemTitle(self, value):
        if not value or len(value) != 8:
            raise ValueError("Invalid client system title.")
        self.sourceSystemTitle = value

    #
    # Long data count.
    #
    def getCount(self):
        return self.count

    #
    # @param value
    # Data count.
    #
    def setCount(self, value):
        if value < 0:
            raise ValueError("Invalid count.")
        self.count = value

    #
    # @param value
    # Long data index
    #
    def setIndex(self, value):
        if value < 0:
            raise ValueError("Invalid Index.")
        self.index = value

    def is_multiple_block(self) -> bool:
        """ Are there more data to send or more data to receive. !!! instead GXDLMSLNParameters.multipleBlocks """
        return self.count != self.index
