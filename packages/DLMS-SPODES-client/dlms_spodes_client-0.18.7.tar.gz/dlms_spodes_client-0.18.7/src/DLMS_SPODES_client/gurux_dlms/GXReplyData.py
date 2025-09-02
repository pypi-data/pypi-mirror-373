from DLMS_SPODES.types import cdt
from DLMS_SPODES.enums import XDLMSAPDU
from .GXByteBuffer import GXByteBuffer
from .enums import RequestTypes
from .GXDLMSException import GXDLMSException


class GXReplyData:
    value_type: cdt.CommonDataTypes
    command: XDLMSAPDU | None
    #
    #      Constructor.
    #
    #      @param more
    #                 Is more data available.
    #      @param cmd
    #                 Received command.
    #      @param buff
    #                 Received data.
    #      @param forComplete
    #                 Is frame complete.
    #      @param err
    #                 Received error ID.
    # pylint: disable=too-many-arguments
    def __init__(self,
                 more=RequestTypes.NONE,
                 cmd=None,
                 buff=None,
                 forComplete=False,
                 err=0):
        # Is more data available.
        self.moreData = more
        # Received command.
        self.command = cmd
        # Received data.
        self.data = buff
        if not self.data:
            self.data = GXByteBuffer()
        # Is frame complete.
        self.complete = forComplete
        # Received error.
        self.error = err
        self.value = None
        # Is received frame echo.
        self.echo = False
        # Received command type.
        self.commandType = 0
        # HDLC frame ID.
        self.frameId = 0
        # Read value.
        self.dataValue = None
        # Expected count of element in the array.
        self.totalCount = 0
        # Last read position.  This is used in peek to solve how far data
        # is read.
        self.readPosition = 0
        # Packet length.
        self.packetLength = 0
        # Try get value.
        self.peek = False
        # Cipher index is position where data is decrypted.
        self.cipherIndex = 0
        # Invoke ID.
        self.invokeId = 0
        # GBT block number.
        self.blockNumber = 0
        # GBT block number ACK.
        self.blockNumberAck = 0
        # Is GBT streaming in use.
        self.streaming = False
        # GBT Window size.  This is for internal use.
        self.windowSize = 0
        # Client address of the notification message.  Notification
        # message sets
        # this.
        self.clientAddress = 0
        self.serverAddress = 0
        """ Server address of the notification message.  Notification message sets this. """
        # Gateway information.
        self.gateway = None

    def clear(self):
        """" Reset data values to default. """
        self.moreData = RequestTypes.NONE
        self.command = None
        self.commandType = 0
        self.data.capacity = 0
        self.complete = False
        self.error = 0
        self.totalCount = 0
        self.dataValue = None
        self.readPosition = 0
        self.packetLength = 0
        self.cipherIndex = 0
        self.invokeId = 0
        self.value = None

    def isMoreData(self):
        """ Is more data available. """
        return self.moreData != RequestTypes.NONE and self.error == 0

    def isNotify(self):
        """ Is notify message. """
        return self.command == XDLMSAPDU.EVENT_NOTIFICATION_REQUEST or self.command == XDLMSAPDU.DATA_NOTIFICATION or self.command == XDLMSAPDU.INFORMATION_REPORT_REQUEST

    def isComplete(self):
        """  Is frame complete. Returns true if frame is complete or false if bytes is missing."""
        return self.complete

    def getError(self):
        """ Get Received error.  Value is zero if no error has occurred. Received error."""
        return self.error

    def getErrorMessage(self):
        return GXDLMSException.getDescription(self.error)

    def getTotalCount(self):
        """ Get total count of element in the array.  If this method is used peek must be set true."""
        return self.totalCount

    def getCount(self):
        """  Get count of read elements.  If this method is used peek must be set true."""
        if isinstance(self.dataValue, list):
            return len(self.dataValue)
        return 0

    def isStreaming(self):
        """ Is GBT streaming. """
        return self.streaming and (self.blockNumberAck * self.windowSize) + 1 > self.blockNumber

    def __str__(self):
       if self.data is None:
            return ""
       return str(self.data)
