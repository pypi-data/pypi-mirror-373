from __future__ import print_function
from DLMS_SPODES.enums import ConfirmedServiceError, XDLMSAPDU, ReadResponse
from ..FCS16 import get_fcs16
from . import GXDLMSSettings
from .GXByteBuffer import GXByteBuffer
from .internal._GXCommon import _GXCommon
from .enums import RequestTypes, Priority, ServiceClass
from .enums import StateError, ExceptionServiceError, Security
from .GXDLMSConfirmedServiceError import GXDLMSConfirmedServiceError
from .MBusEncryptionMode import MBusEncryptionMode
from .MBusCommand import MBusCommand


class GXDLMS:
    """ GXDLMS implements methods to communicate with DLMS/COSEM metering devices. """

    _CIPHERING_HEADER_SIZE = 7 + 12 + 3
    _data_TYPE_OFFSET = 0xFF0000

    @classmethod
    def getInvokeIDPriority(cls, settings: GXDLMSSettings) -> int:
        value = 0
        if settings.priority == Priority.HIGH:
            value |= 0x80
        if settings.serviceClass == ServiceClass.CONFIRMED:
            value |= 0x40
        value |= settings.invokeId
        return value

    @classmethod
    def getLongInvokeIDPriority(cls, settings: GXDLMSSettings) -> int:
        """ Generates Invoke ID and priority. DLMS settings. Invoke ID and priority. """
        value = 0
        if settings.priority == Priority.HIGH:
            value = 0x80000000
        if settings.serviceClass == ServiceClass.CONFIRMED:
            value |= 0x40000000
        value |= int((settings.getLongInvokeID() & 0xFFFFFF))
        settings.setLongInvokeID(settings.getLongInvokeID() + 1)
        return value

    @classmethod
    def multipleBlocks(cls, p, reply, ciphering):
        """
        Check is all_ data fit to one data block.

        @param p
        LN parameters.
        @param reply
        Generated reply.
        """

        #  Check is all_ data fit to one message if data is given.
        len_ = 0
        if p.data:
            if isinstance(p.data, bytes):
                len_ = len(p.data)
            else:
                len_ = len(p.data) - p.data.position
        if p.attributeDescriptor:
            len_ += p.attributeDescriptor.size
        if ciphering:
            len_ += cls._CIPHERING_HEADER_SIZE
        if not p.settings.is_multiple_block():
            #  Add command type and invoke and priority.
            p.multipleBlocks = 2 + len(reply) + len_ > p.settings.maxPduSize
        if p.multipleBlocks:
            #  Add command type and invoke and priority.
            p.lastBlock = not 8 + len(reply) + len_ > p.settings.maxPduSize
        if p.lastBlock:
            #  Add command type and invoke and priority.
            p.lastBlock = not 8 + len(reply) + len_ > p.settings.maxPduSize

    @classmethod
    def appendMultipleSNBlocks(cls, p, reply):
        ciphering = p.settings.cipher and p.settings.cipher.security != Security.NONE
        hSize = len(reply) + 3
        if p.command == XDLMSAPDU.WRITE_REQUEST or p.command == XDLMSAPDU.READ_REQUEST:
            hSize += 1 + _GXCommon.getObjectCountSizeInBytes(p.getCount())
        maxSize = p.settings.maxPduSize - hSize
        if ciphering:
            maxSize -= cls._CIPHERING_HEADER_SIZE
        maxSize -= _GXCommon.getObjectCountSizeInBytes(maxSize)
        if reply.data.size - reply.data.position > maxSize:
            reply.setUInt8(0)
        else:
            reply.setUInt8(1)
            maxSize = reply.data.size - reply.data.position
        reply.setUInt16(p.blockIndex)
        if p.command == XDLMSAPDU.WRITE_REQUEST:
            p.setBlockIndex(p.blockIndex + 1)
            _GXCommon.setObjectCount(p.getCount(), reply)
            reply.setUInt8(DataType.OCTET_STRING)
        elif p.command == XDLMSAPDU.READ_REQUEST:
            p.setBlockIndex(p.blockIndex + 1)
        _GXCommon.setObjectCount(maxSize, reply)
        return maxSize

    @classmethod
    def getAddress(cls, value, size):
        if size < 2 and value < 0x80:
            return int((value << 1 | 1))
        if size < 4 and value < 0x4000:
            return int(((value & 0x3F80) << 2 | (value & 0x7F) << 1 | 1))
        if value < 0x10000000:
            return int(((value & 0xFE00000) << 4 | (value & 0x1FC000) << 3 | (value & 0x3F80) << 2 | (value & 0x7F) << 1 | 1))
        raise ValueError("Invalid address.")

    @classmethod
    def getAddressBytes(cls, value, size):
        tmp = cls.getAddress(value, size)
        bb = GXByteBuffer()
        if size == 1 or tmp < 0x100:
            bb.setUInt8(tmp)
        elif size == 2 or tmp < 0x10000:
            bb.setUInt16(tmp)
        elif size == 4 or tmp < 0x100000000:
            bb.setUInt32(tmp)
        else:
            raise ValueError("Invalid address type.")
        return bb.array()

    @classmethod
    def getWrapperFrame(cls, settings, command, data):
        bb = GXByteBuffer()
        bb.setUInt16(1)
        if settings.isServer:
            bb.setUInt16(settings.serverAddress)
            if settings.PushClientAddress != 0 and command in (XDLMSAPDU.DATA_NOTIFICATION, XDLMSAPDU.EVENT_NOTIFICATION_REQUEST):
                bb.setUInt16(settings.pushClientAddress)
            else:
                bb.setUInt16(settings.clientAddress)
        else:
            bb.setUInt16(settings.clientAddress)
            bb.setUInt16(settings.serverAddress)
        if data is None:
            bb.setUInt16(0)
        else:
            bb.setUInt16(len(data))
            bb.set(data)
        if settings.isServer:
            if len(data) == data.position:
                data.clear()
            else:
                data.move(data.position, 0, len(data) - data.position)
                data.position = 0
        return bb.array()

    @classmethod
    def getHdlcFrame(cls, settings, frame_, data):
        # pylint: disable=protected-access
        bb = GXByteBuffer()
        frameSize = 0
        len1 = 0
        primaryAddress = None
        secondaryAddress = None
        if settings.isServer:
            if frame_ == 0x13 and settings.pushClientAddress != 0:
                primaryAddress = cls.getAddressBytes(settings.pushClientAddress, 1)
            else:
                primaryAddress = cls.getAddressBytes(settings.clientAddress, 1)
            secondaryAddress = cls.getAddressBytes(settings.serverAddress, settings.serverAddressSize)
        else:
            primaryAddress = cls.getAddressBytes(settings.serverAddress, settings.serverAddressSize)
            secondaryAddress = cls.getAddressBytes(settings.clientAddress, 1)
        bb.setUInt8(_GXCommon.HDLC_FRAME_START_END)
        frameSize = settings.limits.maxInfoTX
        if data and data.position == 0:
            frameSize -= 3
        if not data:
            len1 = 0
            bb.setUInt8(0xA0)
        elif len(data) - data.position <= frameSize:
            len1 = len(data) - data.position
            bb.setUInt8(0xA0 | (((len(secondaryAddress) + len(primaryAddress) + len1) >> 8) & 0x7))
        else:
            len1 = frameSize
            bb.setUInt8(0xA8 | (((len(secondaryAddress) + len(primaryAddress) + len1) >> 8) & 0x7))
        if len1 == 0:
            bb.setUInt8(5 + len(secondaryAddress) + len(primaryAddress) + len1)
        else:
            bb.setUInt8(7 + len(secondaryAddress) + len(primaryAddress) + len1)
        bb.set(primaryAddress)
        bb.set(secondaryAddress)
        if frame_ == 0:
            bb.setUInt8(settings.getNextSend(True))
        else:
            bb.setUInt8(frame_)
        crc = get_fcs16(bb._data, 1, bb.size - 1)
        bb.setUInt16(crc)
        if len1 != 0:
            bb.set(data, data.position, len1)
            crc = get_fcs16(bb._data, 1, len(bb) - 1)
            bb.setUInt16(crc)
        bb.setUInt8(_GXCommon.HDLC_FRAME_START_END)
        if settings.isServer:
            if data:
                if len(data) == data.position:
                    data.clear()
                else:
                    data.move(data.position, 0, len(data) - data.position)
                    data.position = 0
        return bb.array()

    @classmethod
    def getMBusData(cls, settings, buff, data):
        len_ = buff.getUInt8()
        if len(buff) < len_ - 1:
            data.complete = (False)
            buff.position = buff.position - 1
        else:
            if len(buff) < len_:
                len_ -= 1
            data.packetLength = len_
            data.complete = True
            cmd = buff.getUInt8()
            manufacturerID = buff.getUInt16()
            man = _GXCommon.decryptManufacturer(manufacturerID)
            #id =
            buff.getUInt32()
            meterVersion = buff.getUInt8()
            type_ = buff.getUInt8()
            ci = buff.getUInt8()
            #frameId =
            buff.getUInt8()
            #state =
            buff.getUInt8()
            configurationWord = buff.getUInt16()
            encryption = MBusEncryptionMode(configurationWord & 7)
            settings.clientAddress = buff.getUInt8()
            settings.serverAddress = buff.getUInt8()

    @classmethod
    def isMBusData(cls, buff):
        if len(buff) - buff.position < 2:
            return False
        cmd = buff.getUInt8(buff.position + 1)
        return cmd in (MBusCommand.SND_NR, MBusCommand.SND_UD2, MBusCommand.RSP_UD)

    @classmethod
    def handleReadResponse(cls, settings, reply, index):
        data = reply.data
        pos = 0
        cnt = reply.getTotalCount()
        first = cnt == 0 or reply.commandType == ReadResponse.DATA_BLOCK_RESULT
        if first:
            cnt = _GXCommon.getObjectCount(reply.data)
            reply.totalCount = cnt
        type_ = 0
        # values = None
        if cnt != 1:
            #Parse data after all data is received when readlist is used.
            if reply.isMoreData():
                cls.getDataFromBlock(reply.data, 0)
                return False
            if not first:
                reply.data.position = 0
                first = True
            # values = list()
            # if isinstance(reply.value, list):
            #     values.append(reply.value)
            reply.value = None
        while pos != cnt:
            if first:
                type_ = data.getUInt8()
                reply.commandType = type_
            else:
                type_ = reply.commandType
            match type_:
                case ReadResponse.DATA:
                    reply.error = 0
                    if cnt == 1:
                        cls.getDataFromBlock(reply.data, 0)
                    else:
                        reply.readPosition = data.position
                        cls.getValueFromData(settings, reply)
                        data.position = reply.readPosition
                        # values.append(reply.value)
                        # reply.value = None
                case ReadResponse.DATA_ACCESS_ERROR:
                    reply.error = data.getUInt8()
                case ReadResponse.DATA_BLOCK_RESULT:
                    reply.error = 0
                    data = reply.data
                    lastBlock = data.getUInt8()
                    number = data.getUInt16()
                    blockLength = _GXCommon.getObjectCount(data)
                    if lastBlock == 0:
                        reply.moreData = (RequestTypes(reply.moreData | RequestTypes.DATABLOCK))
                    else:
                        reply.moreData = (RequestTypes(reply.moreData & ~RequestTypes.DATABLOCK))
                    if number != 1 and settings.blockIndex == 1:
                        settings.setBlockIndex(number)
                    expectedIndex = settings.blockIndex
                    if number != expectedIndex:
                        raise Exception("Invalid Block number. It is " + number + " and it should be " + expectedIndex + ".")
                    if (reply.moreData & RequestTypes.FRAME) != 0:
                        cls.getDataFromBlock(data, index)
                        return False
                    if blockLength != data.size - data.position:
                        raise ValueError("Invalid block length.")
                    reply.command = None
                    cls.getDataFromBlock(reply.data, index)
                    reply.setTotalCount(0)
                    if reply.getMoreData() == RequestTypes.NONE:
                        settings.resetBlockIndex()
                    return True
                case ReadResponse.BLOCK_NUMBER:
                    number = data.getUInt16()
                    if number != settings.blockIndex:
                        raise Exception("Invalid Block number. It is " + number + " and it should be " + settings.blockIndex + ".")
                    settings.increaseBlockIndex()
                    reply.moreData = (RequestTypes(reply.moreData | RequestTypes.DATABLOCK))
                case _:
                    raise Exception("HandleReadResponse failed. Invalid tag.")
            pos += 1
        # if values:
        #     reply.value = values
        return cnt == 1

    @classmethod
    def errorCodeToString(cls, type_, value):
        if type_ == TranslatorOutputType.STANDARD_XML:
            return TranslatorStandardTags.errorCodeToString(value)
        return TranslatorSimpleTags.errorCodeToString(value)

    @classmethod
    def handleDataNotification(cls, settings, reply):
        data = reply.data
        start = data.position - 1
        invokeId = data.getUInt32()
        reply.time = None
        len_ = data.getUInt8()
        tmp = None
        if len_ != 0:
            tmp = bytearray(len_)
            data.get(tmp)
            dt = DataType.DATETIME
            if len_ == 4:
                dt = DataType.TIME
            elif len_ == 5:
                dt = DataType.DATE
            info = _GXDataInfo()
            info.type_ = dt
            reply.time = _GXCommon.getData(settings, GXByteBuffer(tmp), info)
        cls.getDataFromBlock(reply.data, start)
        cls.getValueFromData(settings, reply)

    @classmethod
    def handleGetResponseWithList(cls, settings, reply):
        cnt = _GXCommon.getObjectCount(reply.data)
        # values = list([None] * cnt)
        pos = 0
        while pos != cnt:
            ch = reply.data.getUInt8()
            if ch != 0:
                reply.error = reply.data.getUInt8()
            else:
                reply.readPosition = reply.data.position
                cls.getValueFromData(settings, reply)
                reply.data.position = reply.readPosition
                # if values:
                #     values[pos] = reply.value
                # reply.value = None
            pos += 1
        # reply.value = values

    @classmethod
    def handleExceptionResponse(cls, data):
        raise Exception(StateError(data.data.getUInt8() - 1), ExceptionServiceError(data.data.getUInt8() - 1))

    @classmethod
    def handleConfirmedServiceError(cls, data):
        service = ConfirmedServiceError(data.data.getUInt8())
        type_ = data.data.getUInt8()
        raise GXDLMSConfirmedServiceError(service, type_, data.data.getUInt8())

    @classmethod
    def getValueFromData(cls, settings, reply):
        data = reply.data
        info = _GXDataInfo()
        if isinstance(reply.value, list):
            info.type_ = DataType.ARRAY
            info.count = reply.totalCount
            info.index = reply.getCount()
        index = data.position
        data.position = reply.readPosition
        try:
            value = _GXCommon.getData(settings, data, info)
            if value is not None:
                if not isinstance(value, list):
                    reply.valueType = DataType(info.type_)
                    reply.value = value
                    reply.totalCount = 0
                    reply.readPosition = data.position
                else:
                    if value:
                        if reply.value is None:
                            reply.value = value
                        else:
                            list_ = list()
                            list_ += reply.value
                            list_ += value
                            reply.value = list_
                    reply.readPosition = data.position
                    reply.totalCount = info.count
            elif info.complete and reply.command == XDLMSAPDU.DATA_NOTIFICATION:
                reply.readPosition = data.position
        finally:
            data.position = index
        if reply.command != XDLMSAPDU.DATA_NOTIFICATION and info.complete and reply.moreData == RequestTypes.NONE:
            if settings:
                settings.resetBlockIndex()
            data.position = 0

    @classmethod
    def getDataFromBlock(cls, data: GXByteBuffer, index: int):
        # pylint: disable=protected-access
        if len(data) == data.position:
            data.clear()
            return 0
        len_ = data.position - index
        data._data[data.position - len_:data.position] = data._data[data.position: len(data)]
        data.position = data.position - len_
        data.size = len(data) - len_
        return len
