import asyncio
from typing_extensions import deprecated
import dataclasses
import time
from abc import ABC, abstractmethod
from functools import cached_property, reduce
from struct import pack
from collections import deque
from itertools import count
from enum import IntEnum, auto, IntFlag
from typing import TextIO, Deque, Any, Callable, Optional
import threading
import datetime
import os
import hashlib
from Cryptodome.Cipher import AES
from DLMS_SPODES_communications import Network, Serial, RS485, BLEKPZ, base
from DLMS_SPODES.cosem_interface_classes import overview
from DLMS_SPODES.cosem_interface_classes.collection import Collection, InterfaceClass, ic, cdt, ut, Data, AssociationLN
from DLMS_SPODES.cosem_interface_classes.security_setup.ver1 import SecuritySuite
from DLMS_SPODES.enums import (
    Transmit, Application, ActionRequest, ReadResponse, ServiceError, AssociationResult, SetRequest, ConfirmedServiceError, AARQapdu, ACSEAPDU, XDLMSAPDU,
    VariableAccessSpecification, AcseServiceUser
)
from DLMS_SPODES.cosem_interface_classes.association_ln import mechanism_id, method
from DLMS_SPODES.cosem_interface_classes.association_ln.authentication_mechanism_name import AuthenticationMechanismName
from DLMS_SPODES.hdlc import frame, sub_layer
from DLMS_SPODES import pdu_enums as pdu, exceptions as exc
from DLMS_SPODES.types.implementations import enums, long_unsigneds, bitstrings, octet_string
from DLMSCommunicationProfile import communication_profile as c_pf, OSI
from .gurux_dlms import GXDLMSSettings, GXByteBuffer, GXReplyData, GXDLMSException
from .gurux_dlms.enums import Security, Standard, BerType, RequestTypes, Service
from .gurux_dlms.GXDLMS import GXDLMS
from .gurux_dlms.GXDLMSLNParameters import GXDLMSLNParameters
from .gurux_dlms.GXDLMSSNParameters import GXDLMSSNParameters
from .gurux_dlms.AesGcmParameter import AesGcmParameter
from .gurux_dlms.GXCiphering import GXCiphering
from .gurux_dlms.GXDLMSConfirmedServiceError import GXDLMSConfirmedServiceError
from .gurux_dlms.GXDLMSChippering import GXDLMSChippering
from .gurux_dlms import CountType
from .gurux_dlms.internal._GXCommon import _GXCommon
from .logger import logger, LogLevel as logL


def copy_with_align(data: bytes, block_size: int = 16) -> bytes:
    """ fill by zeros to full 16 bytes blocks """
    return data + bytes((block_size - len(data) % block_size) % block_size)


TZ = datetime.timezone(datetime.datetime.now() - datetime.datetime.utcnow())
""" os time zone """


def get_os_datetime() -> datetime.datetime:
    """ return os datetime with time zone """
    return datetime.datetime.now(TZ)


def get_os_time() -> str:
    """ return os time with time zone """
    return get_os_datetime().strftime('%H:%M:%S')


class State(ABC):

    @abstractmethod
    def __str__(self):
        """"""


@dataclasses.dataclass
class Text(State):
    value: str

    def __str__(self):
        return self.value


class IDFactory:
    def __init__(self, prefix: str):
        self.count = count()
        self.value = set()
        self.prefix = prefix

    def create(self) -> str:
        id_ = F"{self.prefix}{next(self.count)}"
        """for identification before LDN reading"""
        while True:
            if id_ not in self.value:
                self.register(id_)
                return id_
            else:
                id_ = F"{self.prefix}{next(self.count)}"

    def register(self, id_: str):
        if id_ not in self.value:
            self.value.add(id_)
        else:
            raise ValueError(F"error in register ID={id_}: already exist")

    def remove(self, value: str) -> bool:
        try:
            self.value.remove(value)
            return True
        except KeyError:
            return False


class Client:
    id: str | None
    name: str = "unknown"
    com_profile: c_pf.CommunicationProfile
    __del_cb: Callable[[str], bool] | None
    __universal: bool
    level: OSI
    log_file: TextIO
    media: base.Media | None
    lock: asyncio.Lock
    last_transfer_time: datetime.timedelta | None
    connection_time_release: int
    received_frames: Deque[frame.Frame]
    current_obj: InterfaceClass | None
    reply: GXReplyData
    settings: GXDLMSSettings
    __sap: enums.ClientSAP
    secret: bytes
    SA: frame.Address
    DA: frame.Address
    negotiated_conformance: bitstrings.Conformance
    _objects: Optional[Collection]
    APP_CONTEXT_NAME = cdt.OctetString("60857405080101")
    """AssociationLN.application_context_name a-xdr encode"""
    DEF_DLMS_VER: int = 6
    """DLMS version by default"""
    m_id: mechanism_id.MechanismIdElement
    """None is the AUTO from current association"""
    addr_size: frame.AddressLength
    logging_disable: bool
    state: State

    def __init__(self,
                 SAP: int = 0x10,
                 secret: str | bytes = "",
                 conformance: str = None,
                 addr_size: int = -1,
                 media: base.Media = None,
                 id_: str | int = None,
                 m_id: int = 0,
                 universal: bool = False,
                 del_cb: Callable[[str], bool] = None,
                 com_profile: c_pf.CommunicationProfile = None):
        self.com_profile = c_pf.HDLC() if com_profile is None else com_profile
        """communication profile"""
        self.id = id_
        """for identification before LDN reading"""
        self.__universal = universal
        """matching LDN if True else change server Type"""
        self.__del_cb = del_cb
        """callback to unregister id"""
        self.logging_disable = False
        """turn off logging by default"""
        self._objects = None
        self.__sap = enums.ClientSAP(SAP)
        """Service Access Point. Default <Public>"""
        self.media = Serial(port="COM3") if media is None else media
        """ physical layer """
        if com_profile is None:
            self.com_profile = c_pf.HDLC()
        self.server_SAP = long_unsigneds.ServerSAP(1)
        if isinstance(secret, str):
            self.secret = bytes.fromhex(secret)
        elif isinstance(secret, bytes):
            self.secret = secret
        self.protocol_version = cdt.BitString('1')  # max 8 bit
        """ Protocol Version of the AARQ APDU """
        # TODO: REMOVE IT BULLSHIT
        self.invocationCounter = '0.0.43.1.0.255'
        self.lock = asyncio.Lock()
        """ lock for exchange access to device """
        self.addr_size = frame.AddressLength(addr_size)
        """server address size, -1 is AUTO"""
        self.m_id = mechanism_id.MechanismIdElement(m_id)
        # from AssociationLN.xDLMSinfo
        self.quality_of_service = 0
        self.receive_pdu_size = 0xffff  # max available
        self.proposed_conformance = bitstrings.Conformance(conformance)
        self.negotiated_conformance = self.proposed_conformance.copy()

        self.last_transfer_time = None
        """ decided time transfer from server to client """

        self.connection_time_release = 10
        """ number of second for port release after inactivity """

        self.reply = GXReplyData()
        """ use gurux reply class now """

        self.received_frames = deque()
        """ HDLC frames container from server """

        self.send_frames = deque()
        self.level = OSI.NONE
        """OSI level"""
        self.settings = GXDLMSSettings(False)

        self.current_obj = None
        """ current transferring object. For progress bar now """

        # from Gurux Client
        self.use_protected_release = False
        """  Gurux Client: If protected release is used release is including a ciphered xDLMS Initiate request. """

        self.state = Text("undefined")

    @property
    def objects(self) -> Collection:
        if self._objects is None:
            raise exc.DLMSException("client hasn't objects")
        return self._objects

    def __del__(self):
        if self.__del_cb:
            self.__del_cb(self.id)

    def is_universal(self) -> bool:
        return self.__universal

    def log(self, level: logL, msg: str | State):
        """use logger with level and extra=LDN"""
        if not self.logging_disable:
            logger.log(level=level,
                       msg=str(msg),
                       extra={"id": self._objects.LDN.value.to_str() if (self._objects and self._objects.LDN.value) else F"{self.id}"})
        if level == logL.STATE and isinstance(msg, State):
            self.state = msg

    @property
    def SAP(self) -> enums.ClientSAP:
        return self.__sap

    @SAP.setter
    def SAP(self, value):
        """change SAP if associationLN possible"""
        new_SAP = enums.ClientSAP(value)
        if self._objects is not None:
            self._objects.sap2association(new_SAP)
        else:
            """OK"""
        self.__sap.set(value)

    def get_ass_id(self) -> int:
        """return current Association ID"""
        return int(self.current_association.logical_name.e)

    def get_channel_index(self) -> int:
        """todo: remove in future. get communication channel by media"""
        match self.media:
            case Serial():  return 0
            case RS485():   return 1
            case Network(): return 2
            case BLEKPZ():  return 3
            case _:         raise ValueError(F"can't calculate channel index by media: {self.media}")

    def get_frame(self, read_data: bytearray) -> frame.Frame | None:
        while len(read_data) != 0:
            new_frame = frame.Frame.try_from(read_data)
            self.reply.complete = True
            if new_frame is None:
                self.reply.complete = False
                return None
            if new_frame.is_for_me(self.DA, self.SA):
                self.received_frames.append(new_frame)
                if new_frame.is_segmentation:
                    self.reply.moreData |= RequestTypes.FRAME
                else:
                    self.reply.moreData &= ~RequestTypes.FRAME
                # check control TODO: rewrite it
                if new_frame.control.is_unnumbered():
                    if new_frame.control in (frame.Control.UA_F, frame.Control.SNRM_P):
                        self.settings.resetFrameSequence()
                        return new_frame
                    elif new_frame.control == frame.Control.UI_PF:
                        self.log(logL.WARN, """ TODO: Here Notify handler """)
                    else:
                        self.log(logL.INFO, F'Can\'t processing HDLC Frame: {new_frame.control}')
                elif new_frame.control.is_supervisory():
                    self.settings.receiverFrame = frame.Control.next_receiver_sequence(self.settings.receiverFrame)
                    return new_frame
                elif self.settings.senderFrame.is_info():
                    expected = frame.Control.next_receiver_sequence(frame.Control.next_send_sequence(self.settings.receiverFrame))
                    if new_frame.control == expected:
                        self.settings.receiverFrame = new_frame.control
                        return new_frame
                    else:
                        self.log(logL.INFO, F'Invalid HDLC Frame: {new_frame.control} Expected: {expected}')
                else:
                    expected = frame.Control.next_send_sequence(self.settings.receiverFrame)
                    #  If answer for RR.
                    if new_frame.control == expected:
                        self.settings.receiverFrame = new_frame.control
                        return new_frame
                    else:
                        self.log(logL.INFO, F'Invalid HDLC Frame: {new_frame.control} Expected: {expected}')
                self.log(logL.WARN, F"Drop frame {new_frame}")
            else:
                self.log(logL.WARN, F"ALIEN frame {new_frame}, expect with SA:{self.SA}")
                # FROM GURUX - if new_frame.control == frame.Control.UI_PF:  # search next frame in read_data

    def handleGbt(self):
        index = self.reply.data.position - 1
        self.reply.windowSize = self.settings.windowSize
        bc = self.reply.data.getUInt8()
        self.reply.streaming = (bc & 0x40) != 0
        windowSize = int(bc & 0x3F)
        bn = self.reply.data.getUInt16()
        bna = self.reply.data.getUInt16()
        self.reply.blockNumber = bn
        self.reply.blockNumberAck = bna
        self.settings.blockNumberAck = self.reply.blockNumber
        self.reply.command = None
        len_ = _GXCommon.getObjectCount(self.reply.data)
        if len_ > self.reply.data.size - self.reply.data.position:
            self.reply.complete = False
            return
        GXDLMS.getDataFromBlock(self.reply.data, index)
        if (bc & 0x80) == 0:
            self.reply.moreData = (RequestTypes(self.reply.moreData | RequestTypes.GBT))
        else:
            self.reply.moreData = (RequestTypes(self.reply.moreData & ~RequestTypes.GBT))
            if self.reply.data.size != 0:
                self.reply.data.position = 0
                self.getPdu()
            # if self.reply.data.position != self.reply.data.size and (self.reply.command == XDLMSAPDU.READ_RESPONSE or self.reply.command == XDLMSAPDU.GET_RESPONSE) and (self.reply.moreData == RequestTypes.NONE or self.reply.peek):
            #     self.reply.data.position = 0
                # cls.getValueFromData(settings, self.reply)

    def getPdu(self) -> Any:
        # TODO: make return pdu
        if self.reply.command is None:
            if self.reply.data.size - self.reply.data.position == 0:
                raise ValueError("Invalid PDU")
            index = self.reply.data.position
            self.reply.command = XDLMSAPDU(self.reply.data.getUInt8())
            match self.reply.command:
                case XDLMSAPDU.GET_RESPONSE:
                    response_type: int = self.reply.data.getUInt8()
                    invoke_id_and_priority = self.reply.data.getUInt8()  # TODO: matching with setting params
                    match response_type:
                        case pdu.GetResponse.NORMAL:
                            match self.reply.data.getUInt8():  # Get-Data-Result[0]
                                case 0:    GXDLMS.getDataFromBlock(self.reply.data, 0)
                                case 1:
                                    self.reply.error = pdu.DataAccessResult(self.reply.data.getUInt8())
                                    if self.reply.error != 0:
                                        raise exc.ResultError(self.reply.error)
                                case err:  raise ValueError(F'Got Get-Data-Result[0] {err}, expect 0 or 1')
                            GXDLMS.getDataFromBlock(self.reply.data, 0)
                        case pdu.GetResponse.WITH_DATABLOCK:
                            last_block = self.reply.data.getUInt8()
                            if last_block == 0:
                                self.reply.moreData |= RequestTypes.DATABLOCK
                            else:
                                self.reply.moreData &= ~RequestTypes.DATABLOCK
                            block_number = self.reply.data.getUInt32()
                            if block_number == 0 and self.settings.blockIndex == 1:  # if start block_index == 0
                                self.settings.setBlockIndex(0)
                            if block_number != self.settings.blockIndex:
                                raise ValueError(F"Invalid Block number. It is {block_number} and it should be {self.settings.blockIndex}.")
                            match self.reply.data.getUInt8():  # DataBlock-G.result
                                case 0:
                                    if self.reply.data.position != len(self.reply.data):
                                        block_length = _GXCommon.getObjectCount(self.reply.data)
                                        if (self.reply.moreData & RequestTypes.FRAME) == 0:
                                            if block_length > len(self.reply.data) - self.reply.data.position:
                                                raise ValueError("Invalid block length.")
                                            self.reply.command = None
                                        if block_length == 0:
                                            self.reply.data.size = index
                                        else:
                                            GXDLMS.getDataFromBlock(self.reply.data, index)
                                        if self.reply.moreData == RequestTypes.NONE:
                                            if not self.reply.peek:
                                                self.reply.data.position = 0
                                                self.settings.resetBlockIndex()
                                        if self.reply.moreData == RequestTypes.NONE and self.settings and self.settings.command == XDLMSAPDU.GET_REQUEST \
                                                and self.settings.commandType == pdu.GetResponse.WITH_LIST:
                                            GXDLMS.handleGetResponseWithList(self.settings, self.reply)
                                            return
                                case 1:
                                    self.reply.error = pdu.DataAccessResult(self.reply.data.getUInt8())
                                    if self.reply.error != 0:
                                        raise exc.ResultError(self.reply.error)
                                case err: raise ValueError(F'Got DataBlock-G.result {err}, expect 0 or 1')
                        case pdu.GetResponse.WITH_LIST:
                            GXDLMS.handleGetResponseWithList(self.settings, self.reply)
                            return
                        case err: raise ValueError(F"Got Invalid Get response {err}, expect {', '.join(map(lambda it: F'{it.name} = {it.value}', pdu.GetResponse))}")
                case XDLMSAPDU.READ_RESPONSE:
                    if not GXDLMS.handleReadResponse(self.settings, self.reply, index):
                        return
                case XDLMSAPDU.SET_RESPONSE:
                    response_type: int = self.reply.data.getUInt8()
                    invoke_id_and_priority = self.reply.data.getUInt8()  # TODO: matching with setting params
                    match response_type:
                        case pdu.SetResponse.NORMAL:
                            self.reply.error = pdu.DataAccessResult(self.reply.data.getUInt8())
                            if self.reply.error != 0:
                                raise exc.ResultError(self.reply.error)
                        case pdu.SetResponse.DATABLOCK:
                            block_number = self.reply.data.getUInt32()
                        case pdu.SetResponse.LAST_DATABLOCK:
                            self.reply.error = pdu.DataAccessResult(self.reply.data.getUInt8())
                            if self.reply.error != 0:
                                raise exc.ResultError(self.reply.error)
                            block_number = self.reply.data.getUInt32()
                        case pdu.SetResponse.LAST_DATABLOCK_WITH_LIST:
                            raise ValueError("Not released in Client")
                        case pdu.SetResponse.WITH_LIST:
                            cnt = _GXCommon.getObjectCount(self.reply.data)
                            pos = 0
                            while pos != cnt:
                                self.reply.error = pdu.DataAccessResult(self.reply.data.getUInt8())
                                if self.reply.error != 0:
                                    raise exc.ResultError(self.reply.error)
                                pos += 1
                        case err: raise ValueError(F"Got Invalid Set response {err}, expect {', '.join(map(lambda it: F'{it.name} = {it.value}', pdu.SetResponse))}")
                case XDLMSAPDU.WRITE_RESPONSE:
                    cnt = _GXCommon.getObjectCount(self.reply.data)
                    pos = 0
                    while pos != cnt:
                        ret = self.reply.data.getUInt8()
                        if ret != 0:
                            self.reply.error = self.reply.data.getUInt8()
                        pos += 1
                case XDLMSAPDU.ACTION_RESPONSE:
                    action_response = self.reply.data.getUInt8()
                    invoke_id_and_priority = self.reply.data.getUInt8()
                    match action_response:
                        case pdu.ActionResponse.NORMAL:
                            self.reply.error = pdu.ActionResult(self.reply.data.getUInt8())
                            if self.reply.error != 0:
                                raise exc.ResultError(self.reply.error)
                            if self.reply.data.position < self.reply.data.size:
                                ret = self.reply.data.getUInt8()
                                if ret == 0:
                                    GXDLMS.getDataFromBlock(self.reply.data, 0)
                                elif ret == 1:
                                    ret = int(self.reply.data.getUInt8())
                                    if ret != 0:
                                        self.reply.error = self.reply.data.getUInt8()
                                        if ret == 9 and self.reply.getError() == 16:
                                            self.reply.data.position = self.reply.data.position - 2
                                            GXDLMS.getDataFromBlock(self.reply.data, 0)
                                            self.reply.error = 0
                                            ret = 0
                                    else:
                                        GXDLMS.getDataFromBlock(self.reply.data, 0)
                                else:
                                    raise Exception("HandleActionResponseNormal failed. " + "Invalid tag.")
                        case pdu.ActionResponse.WITH_PBLOCK:
                            raise ValueError("Not released in Client")
                        case pdu.ActionResponse.WITH_LIST:
                            raise ValueError("Not released in Client")
                        case pdu.ActionResponse.NEXT_PBLOCK:
                            raise ValueError("Not released in Client")
                        case err:
                            raise ValueError(F"got {pdu.ActionResponse}: {err}, expect {', '.join(map(lambda it: F'{it.name} = {it.value}', pdu.ActionResponse))}")
                case XDLMSAPDU.ACCESS_RESPONSE:
                    data = self.reply.data
                    invokeId = self.reply.data.getUInt32()
                    len_ = self.reply.data.getUInt8()
                    tmp = None
                    if len_ != 0:
                        tmp = bytearray(len_)
                        data.get(tmp)
                        self.reply.time = _GXCommon.changeType(self.settings, tmp, DataType.DATETIME)
                    data.getUInt8()
                case XDLMSAPDU.GENERAL_BLOCK_TRANSFER:
                    if not self.settings.isServer and (self.reply.moreData & RequestTypes.FRAME) == 0:
                        self.handleGbt()
                case ACSEAPDU.AARQ | ACSEAPDU.AARE:
                    # This is parsed later.
                    self.reply.data.position = self.reply.data.position - 1
                case ACSEAPDU.RLRE | ACSEAPDU.RLRQ:
                    pass
                case XDLMSAPDU.CONFIRMED_SERVICE_ERROR:
                    GXDLMS.handleConfirmedServiceError(self.reply)
                case XDLMSAPDU.EXCEPTION_RESPONSE:
                    GXDLMS.handleExceptionResponse(self.reply)
                case XDLMSAPDU.GET_REQUEST | XDLMSAPDU.READ_REQUEST | XDLMSAPDU.WRITE_REQUEST | XDLMSAPDU.SET_REQUEST | XDLMSAPDU.ACTION_REQUEST:
                    pass
                case XDLMSAPDU.GLO_READ_REQUEST | XDLMSAPDU.GLO_WRITE_REQUEST | XDLMSAPDU.GLO_GET_REQUEST | XDLMSAPDU.GLO_SET_REQUEST | XDLMSAPDU.GLO_ACTION_REQUEST | \
                     XDLMSAPDU.DED_GET_REQUEST | XDLMSAPDU.DED_SET_REQUEST | XDLMSAPDU.DED_ACTION_REQUEST:
                    if self.settings.cipher is None:
                        raise ValueError("Secure connection is not supported.")
                    if (self.reply.moreData & RequestTypes.FRAME) == 0:
                        self.reply.data.position = self.reply.data.position - 1
                        p = None
                        if self.settings.cipher.dedicatedKey and (OSI.APPLICATION in self.level):
                            p = AesGcmParameter(self.settings.sourceSystemTitle, self.settings.cipher.dedicatedKey, self.settings.cipher.authenticationKey)
                        else:
                            p = AesGcmParameter(self.settings.sourceSystemTitle, self.settings.cipher.blockCipherKey, self.settings.cipher.authenticationKey)
                        tmp = GXCiphering.decrypt(self.settings.cipher, p, self.reply.data)
                        self.reply.data.clear()
                        self.reply.data.set(tmp)
                        self.reply.command = XDLMSAPDU(self.reply.data.getUInt8())
                        if self.reply.command == XDLMSAPDU.DATA_NOTIFICATION or self.reply.command == XDLMSAPDU.INFORMATION_REPORT_REQUEST:
                            self.reply.command = None
                            self.reply.data.position = self.reply.data.position - 1
                            self.getPdu()
                    else:
                        self.reply.data.position = self.reply.data.position - 1
                case XDLMSAPDU.GLO_READ_RESPONSE | XDLMSAPDU.GLO_WRITE_RESPONSE | XDLMSAPDU.GLO_GET_RESPONSE | XDLMSAPDU.GLO_SET_RESPONSE | XDLMSAPDU.GLO_ACTION_RESPONSE | \
                     XDLMSAPDU.GENERAL_GLO_CIPHERING | XDLMSAPDU.GLO_EVENT_NOTIFICATION_REQUEST | XDLMSAPDU.DED_GET_RESPONSE | XDLMSAPDU.DED_SET_RESPONSE | \
                     XDLMSAPDU.DED_ACTION_RESPONSE | XDLMSAPDU.GENERAL_DED_CIPHERING | XDLMSAPDU.DED_EVENT_NOTIFICATION_REQUEST:
                    if self.settings.cipher is None:
                        raise ValueError("Secure connection is not supported.")
                    if (self.reply.moreData & RequestTypes.FRAME) == 0:
                        self.reply.data.position = self.reply.data.position - 1
                        bb = GXByteBuffer(self.reply.data)
                        self.reply.data.size = self.reply.data.position = index
                        p = None
                        if self.settings.cipher.dedicatedKey and (OSI.APPLICATION in self.level):
                            p = AesGcmParameter(0, self.settings.sourceSystemTitle, self.settings.cipher.dedicatedKey, self.settings.cipher.authenticationKey)
                        else:
                            p = AesGcmParameter(0, self.settings.sourceSystemTitle, self.settings.cipher.blockCipherKey, self.settings.cipher.authenticationKey)
                        self.reply.data.set(GXCiphering.decrypt(self.settings.cipher, p, bb))
                        self.reply.command = None
                        self.getPdu()
                        self.reply.cipherIndex = self.reply.data.size
                case XDLMSAPDU.DATA_NOTIFICATION:
                    GXDLMS.handleDataNotification(self.settings, self.reply)
                    data = self.reply.data
                    start = data.position - 1
                    invokeId = data.getUInt32()
                    self.reply.time = None
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
                        self.reply.time = _GXCommon.getData(self.settings, GXByteBuffer(tmp), info)
                    GXDLMS.getDataFromBlock(self.reply.data, start)
                    GXDLMS.getValueFromData(self.settings, self.reply)
                case XDLMSAPDU.EVENT_NOTIFICATION_REQUEST:
                    pass
                case XDLMSAPDU.INFORMATION_REPORT_REQUEST:
                    pass
                case XDLMSAPDU.GENERAL_CIPHERING:
                    if self.settings.cipher is None:
                        raise ValueError("Secure connection is not supported.")
                    if (self.reply.moreData & RequestTypes.FRAME) == 0:
                        self.reply.data.position = self.reply.data.position - 1
                        p = AesGcmParameter(0, self.settings.sourceSystemTitle, self.settings.cipher.blockCipherKey, self.settings.cipher.authenticationKey)
                        tmp = GXCiphering.decrypt(self.settings.cipher, p, self.reply.data)
                        self.reply.data.clear()
                        self.reply.data.set(tmp)
                        self.reply.command = None
                        if p.security:
                            self.getPdu()
                case XDLMSAPDU.GATEWAY_REQUEST:
                    pass
                case XDLMSAPDU.GATEWAY_RESPONSE:
                    self.reply.data.getUInt8()
                    len_ = _GXCommon.getObjectCount(self.reply.data)
                    pda = bytearray(len_)
                    self.reply.data.get(pda)
                    GXDLMS.getDataFromBlock(self.reply, index)
                    self.reply.command = None
                    self.getPdu()
                case _:                                                                       raise ValueError("Invalid PDU Command.")
        elif (self.reply.moreData & RequestTypes.FRAME) == 0:
            if not self.reply.peek and self.reply.moreData == RequestTypes.NONE:
                if self.reply.command == ACSEAPDU.AARE or self.reply.command == ACSEAPDU.AARQ:
                    self.reply.data.position = 0
                else:
                    self.reply.data.position = 1
            if self.reply.command == XDLMSAPDU.GENERAL_BLOCK_TRANSFER:
                self.reply.data.position = self.reply.cipherIndex + 1
                self.handleGbt()
                self.reply.cipherIndex = self.reply.data.size
                self.reply.command = None
            elif self.settings.isServer:
                if self.reply.command in (
                        XDLMSAPDU.GLO_READ_REQUEST, XDLMSAPDU.GLO_WRITE_REQUEST, XDLMSAPDU.GLO_GET_REQUEST, XDLMSAPDU.GLO_SET_REQUEST, XDLMSAPDU.GLO_ACTION_REQUEST,
                        XDLMSAPDU.GLO_EVENT_NOTIFICATION_REQUEST, XDLMSAPDU.DED_GET_REQUEST, XDLMSAPDU.DED_SET_REQUEST, XDLMSAPDU.DED_ACTION_REQUEST,
                        XDLMSAPDU.DED_EVENT_NOTIFICATION_REQUEST):
                    self.reply.command = None
                    self.reply.data.position = self.reply.getCipherIndex()
                    self.getPdu()
            else:
                self.reply.command = None
                if self.reply.command in (
                        XDLMSAPDU.GLO_READ_RESPONSE, XDLMSAPDU.GLO_WRITE_RESPONSE, XDLMSAPDU.GLO_GET_RESPONSE, XDLMSAPDU.GLO_SET_RESPONSE, XDLMSAPDU.GLO_ACTION_RESPONSE,
                        XDLMSAPDU.DED_GET_RESPONSE, XDLMSAPDU.DED_SET_RESPONSE, XDLMSAPDU.DED_ACTION_RESPONSE, XDLMSAPDU.GENERAL_GLO_CIPHERING, XDLMSAPDU.GENERAL_DED_CIPHERING):
                    self.reply.data.position = self.reply.cipherIndex
                    self.getPdu()
                if self.reply.command == XDLMSAPDU.READ_RESPONSE and self.reply.totalCount > 1:
                    if not GXDLMS.handleReadResponse(self.settings, self.reply, 0):
                        return

        if (
            self.reply.command == XDLMSAPDU.READ_RESPONSE
            and self.reply.commandType == ReadResponse.DATA_BLOCK_RESULT
            and (self.reply.moreData & RequestTypes.FRAME) != 0
        ):
            return
        if (
            self.reply.data.position != self.reply.data.size
            and (
                self.reply.moreData == RequestTypes.NONE
                or self.reply.peek)
            and self.reply.command in (
                XDLMSAPDU.READ_RESPONSE,
                XDLMSAPDU.GET_RESPONSE,
                XDLMSAPDU.ACTION_RESPONSE,
                XDLMSAPDU.DATA_NOTIFICATION)
        ):
            pass
            # GXDLMS.getValueFromData(self.settings, self.reply)

    def __is_frame(self, notify, read_data: bytearray) -> bool:
        reply = GXByteBuffer(read_data)
        is_notify: bool = False
        match self.com_profile:
            case c_pf.HDLC():
                recv_frame = self.get_frame(read_data)
                if recv_frame is not None:
                    self.log(logL.INFO, F"RX: {recv_frame.content.hex(' ')}")
                    if recv_frame.control == frame.Control.UI_PF:
                        target = notify  # use instead of self.reply in getPdu(target). see in Gurux to do
                        is_notify = True
                    self.reply.frameId = recv_frame.control
                else:       # TODO: GURUX redundant
                    # self.write_trace(F"RX {self.id}: {get_os_time()}  {read_data}", TraceLevel.ERROR)
                    self.reply.frameId = frame.Control(0)
            case c_pf.TCPUDPIP():  # getTcpData TODO: check it
                target = self.reply
                if len(reply) - reply.position < 8:
                    target.complete = False
                    return True
                pos = reply.position
                while reply.position < len(reply) - 1:
                    value = reply.getUInt16()
                    if value == 1:
                        # checkWrapperAddress
                        if self.settings.isServer:
                            value = reply.getUInt16()
                            if self.settings.clientAddress != 0 and self.settings.clientAddress != value:
                                raise Exception("Source addresses do not match. It is " + str(value) + ". It should be " + str(self.settings.clientAddress) + ".")
                            self.settings.clientAddress = value
                            value = reply.getUInt16()
                            if self.settings.serverAddress != 0 and self.settings.serverAddress != value:
                                raise Exception("Destination addresses do not match. It is " + str(value) + ". It should be " + str(self.settings.serverAddress) + ".")
                            self.settings.serverAddress = value
                        else:
                            value = reply.getUInt16()
                            if self.settings.clientAddress != 0 and self.settings.serverAddress != value:
                                if notify is None:
                                    raise Exception("Source addresses do not match. It is " + str(value) + ". It should be " + str(self.settings.serverAddress) + ".")
                                notify.serverAddress = value
                                target = notify
                            else:
                                self.settings.serverAddress = value
                            value = reply.getUInt16()
                            if self.settings.clientAddress != 0 and self.settings.clientAddress != value:
                                if notify is None:
                                    raise Exception("Destination addresses do not match. It is " + str(value) + ". It should be " + str(self.settings.clientAddress) + ".")
                                target = notify
                                notify.clientAddress = value
                            else:
                                self.settings.clientAddress = value
                        #
                        value = reply.getUInt16()
                        complete = not (len(reply) - reply.position) < value
                        if complete and (len(reply) - reply.position) != value:
                            self.log(logL.DEB, "Data length is " + str(value) + "and there are " + str(len(reply) - reply.position) + " bytes.")
                        target.complete = complete
                        if not complete:
                            reply.position = pos
                        else:
                            target.packetLength = (reply.position + value)
                        break
                    else:
                        reply.position = reply.position - 1
                if target is not self.reply:
                    is_notify = True
            case c_pf.MBUS():  # not realised see how
                GXDLMS.getMBusData(self.settings, reply, self.reply)
            case _:                raise ValueError("Invalid Interface type.")
        if not self.reply.complete:
            return False

        # TODO: relocate notify to read_data_type
        if notify and not is_notify:
            #Check command to make sure it's not notify message.
            if self.reply.command in (XDLMSAPDU.DATA_NOTIFICATION,
                                      XDLMSAPDU.GLO_EVENT_NOTIFICATION_REQUEST,
                                      XDLMSAPDU.INFORMATION_REPORT_REQUEST,
                                      XDLMSAPDU.EVENT_NOTIFICATION_REQUEST,
                                      XDLMSAPDU.DED_INFORMATION_REPORT_REQUEST,
                                      XDLMSAPDU.DED_EVENT_NOTIFICATION_REQUEST):
                is_notify = True
                notify.complete = self.reply.complete
                notify.command = self.reply.command
                self.reply.command = None
                self.reply.time = None
                notify.self.reply.set(self.reply.data)
                # notify.value = self.reply.value
                self.reply.data.trim()
        if is_notify:
            return False
        return True

    async def read_data_block(self) -> Any:  # todo: 1.make return pdu, 2.make depend from CommunicationProfile
        ret = None
        self.received_frames.clear()
        self.reply.clear()
        while self.send_frames:
            # TODO: see how remove self.reply here !!!
            send_frame = self.send_frames.popleft()
            notify = GXReplyData()
            self.reply.error = 0
            recv_buf: bytearray = bytearray()
            if not self.reply.isStreaming():
                await self.media.send(send_frame.content)
                self.log(logL.INFO, F"TX: {send_frame.content.hex(" ")}")
            attempt: int = 1
            while attempt < 3:
                try:
                    await asyncio.wait_for(                 # todo: don't work exception!!!! Why????
                        fut=self.media.receive(recv_buf),
                        timeout=self.com_profile.parameters.inactivity_time_out)  # todo: only for HDLC
                    if self.__is_frame(notify, recv_buf):
                        break
                    elif notify.data.size != 0:
                        if not notify.isMoreData():
                            notify.clear()
                        continue
                    else:
                        """our frame not was found"""
                except TimeoutError as e:
                    self.log(logL.WARN, F'Data send failed: {e}.  Try to resend {attempt+1}/3. RX_buffer: {recv_buf.hex(" ")}')
                    await self.media.send(send_frame.content)
                    attempt += 1
            else:
                raise exc.Timeout("Failed to receive reply from the device in given time")
            recv_buf.clear()
            match self.reply.error:
                case 0:                        """errors is absence"""
                case 4:                        raise exc.NoObject
                case _:                        raise GXDLMSException(self.reply.error)
            if self.received_frames[-1].control.is_info() or self.received_frames[-1].control == frame.Control.UI_PF:
                if self.received_frames[-1].is_segmentation:
                    """pass handle frame. wait all information"""
                else:
                    llc = sub_layer.LLC(frame.Frame.join_info(self.received_frames))

                    self.reply.data.position = len(self.reply.data)
                    self.reply.data.set(llc.info)
                    ret = self.getPdu()

                    # TODO: LLC to PDU
            else:
                received_frame = self.received_frames.popleft()
                if send_frame.control == frame.Control.SNRM_P:
                    self.com_profile.negotiation.set_from_UA(received_frame.info)
                    self.log(logL.INFO, F"negotiation setup: {self.com_profile.negotiation}")
            if self.reply.isMoreData():
                if self.reply.isStreaming():
                    data = None
                else:
                    # Generates an acknowledgment message, with which the server is informed to send next packets. Frame type. Acknowledgment message as byte array
                    if self.reply.moreData == RequestTypes.NONE:
                        raise ValueError("Invalid receiverReady RequestTypes parameter.")
                    #  Get next frame.
                    if (self.reply.moreData & RequestTypes.FRAME) != 0:
                        id_ = self.settings.getReceiverReady()
                        # return GXDLMS.getHdlcFrame(settings, id_, None)
                        self.add_frames_to_queue(frame.Control(id_))
                    else:
                        if self.settings.getUseLogicalNameReferencing():
                            if self.settings.isServer:
                                cmd = XDLMSAPDU.GET_RESPONSE
                            else:
                                cmd = XDLMSAPDU.GET_REQUEST
                        else:
                            if self.settings.isServer:
                                cmd = XDLMSAPDU.READ_RESPONSE
                            else:
                                cmd = XDLMSAPDU.READ_REQUEST
                        if self.reply.moreData == RequestTypes.GBT:
                            p = GXDLMSLNParameters(self.settings, 0, XDLMSAPDU.GENERAL_BLOCK_TRANSFER, 0, None, None, 0xff)
                            p.WindowSize = self.reply.windowSize
                            p.blockNumberAck = self.reply.blockNumberAck
                            p.blockIndex = self.reply.blockNumber
                            p.Streaming = False
                            reply = self.getLnMessages(p)  # TODO: test it
                        else:
                            #  Get next block.
                            bb = GXByteBuffer(4)
                            if self.settings.getUseLogicalNameReferencing():
                                bb.setUInt32(self.settings.blockIndex)
                            else:
                                bb.setUInt16(self.settings.blockIndex)
                            self.settings.increaseBlockIndex()
                            if self.settings.getUseLogicalNameReferencing():
                                p = GXDLMSLNParameters(self.settings, 0, cmd, pdu.GetResponse.WITH_DATABLOCK, bb, None, 0xff)
                                reply = self.getLnMessages(p)
                            else:
                                p = GXDLMSSNParameters(self.settings, cmd, 1, VariableAccessSpecification.BLOCK_NUMBER_ACCESS, bb, None)
                                reply = self.getSnMessages(p)
                        data = reply
        return ret

    def getSnMessages(self, p: GXDLMSSNParameters):
        reply = GXByteBuffer()
        messages = list()
        frame_ = 0x0
        if p.command == XDLMSAPDU.INFORMATION_REPORT_REQUEST or p.command == XDLMSAPDU.DATA_NOTIFICATION:
            frame_ = 0x13
        while True:
            ciphering = p.settings.cipher and p.settings.cipher.security != Security.NONE and p.command != ACSEAPDU.AARQ and p.command != ACSEAPDU.AARE
            if (
                not ciphering
                and isinstance(self.com_profile, c_pf.HDLC)
            ):
                if p.settings.isServer:
                    reply.set(_GXCommon.LLC_REPLY_BYTES)
                elif not reply:
                    reply.set(_GXCommon.LLC_SEND_BYTES)
            cnt = 0
            cipherSize = 0
            if ciphering:
                cipherSize = GXDLMS._CIPHERING_HEADER_SIZE
            if p.data:
                cnt = p.data.size - p.data.position
            if p.command == XDLMSAPDU.INFORMATION_REPORT_REQUEST:
                reply.setUInt8(p.command)
                if not p.time:
                    reply.setUInt8(cdt.NullData.TAG)
                else:
                    pos = len(reply)
                    _GXCommon.setData(p.settings, reply, cdt.OctetString.TAG, p.time)
                    reply.move(pos + 1, pos, len(reply) - pos - 1)
                _GXCommon.setObjectCount(p.count, reply)
                reply.set(p.attributeDescriptor)
            elif p.command != ACSEAPDU.AARQ and p.command != ACSEAPDU.AARE:
                reply.setUInt8(p.command)
                if p.count != 0xFF:
                    _GXCommon.setObjectCount(p.count, reply)
                if p.requestType != 0xFF:
                    reply.setUInt8(p.requestType)
                reply.set(p.attributeDescriptor)
                if not p.settings.is_multiple_block():
                    p.multipleBlocks = len(reply) + cipherSize + cnt > p.settings.maxPduSize
                    if p.settings.is_multiple_block():
                        reply.size = 0
                        if (
                                not ciphering
                                and isinstance(self.com_profile, c_pf.HDLC)
                        ):
                            if p.settings.isServer:
                                reply.set(_GXCommon.LLC_REPLY_BYTES)
                            elif not reply:
                                reply.set(_GXCommon.LLC_SEND_BYTES)
                        match p.command:
                            case XDLMSAPDU.WRITE_REQUEST:
                                p.requestType = VariableAccessSpecification.WRITE_DATA_BLOCK_ACCESS
                            case XDLMSAPDU.READ_REQUEST:
                                p.requestType = VariableAccessSpecification.READ_DATA_BLOCK_ACCESS
                            case XDLMSAPDU.READ_RESPONSE:
                                p.requestType = ReadResponse.DATA_BLOCK_RESULT
                            case _:
                                raise ValueError("Invalid command.")
                        reply.setUInt8(p.command)
                        reply.setUInt8(1)
                        if p.requestType != 0xFF:
                            reply.setUInt8(p.requestType)
                        cnt = GXDLMS.appendMultipleSNBlocks(p, reply)
                else:
                    cnt = GXDLMS.appendMultipleSNBlocks(p, reply)
            if p.data:
                reply.set(p.data, p.data.position, cnt)
            if p.data and p.data.position == p.data.size:
                p.settings.index = 0
                p.settings.count = 0
            if ciphering and p.command != ACSEAPDU.AARQ and p.command != ACSEAPDU.AARE:
                cipher = p.settings.cipher
                s = AesGcmParameter(self.getGloMessage(p.command), cipher.systemTitle, cipher.blockCipherKey, cipher.authenticationKey)
                s.security = cipher.security
                s.invocationCounter = cipher.invocationCounter
                tmp = GXCiphering.encrypt(s, reply.array())
                assert not tmp
                reply.size = 0
                if isinstance(self.com_profile, c_pf.HDLC):
                    if p.settings.isServer:
                        reply.set(_GXCommon.LLC_REPLY_BYTES)
                    elif not reply:
                        reply.set(_GXCommon.LLC_SEND_BYTES)
                reply.set(tmp)
            if p.command != ACSEAPDU.AARQ and p.command != ACSEAPDU.AARE:
                assert not p.settings.maxPduSize < len(reply)
            while reply.position != len(reply):
                match self.com_profile:
                    case c_pf.TCPUDPIP():
                        messages.append(GXDLMS.getWrapperFrame(p.settings, p.command, reply))
                    case c_pf.HDLC():
                        messages.append(GXDLMS.getHdlcFrame(p.settings, frame_, reply))
                        if reply.position != len(reply):
                            frame_ = p.settings.getNextSend(False)
                    case _:
                        raise ValueError("InterfaceType")
            reply.clear()
            frame_ = 0
            if not p.data or p.data.position == p.data.size:
                break
        return messages

    def receiverReady(self, reply):
        """ Generates an acknowledgment message, with which the server is informed to send next packets. Frame type. Acknowledgment message as byte array. """
        if reply.moreData == RequestTypes.NONE:
            raise ValueError("Invalid receiverReady RequestTypes parameter.")
        #  Get next frame.
        if (reply.moreData & RequestTypes.FRAME) != 0:
            id_ = self.settings.getReceiverReady()
            # return GXDLMS.getHdlcFrame(settings, id_, None)
            return self.add_frames_to_queue(frame.Control(id_))
        if self.settings.getUseLogicalNameReferencing():
            if self.settings.isServer:
                cmd = XDLMSAPDU.GET_RESPONSE
            else:
                cmd = XDLMSAPDU.GET_REQUEST
        else:
            if self.settings.isServer:
                cmd = XDLMSAPDU.READ_RESPONSE
            else:
                cmd = XDLMSAPDU.READ_REQUEST

        if reply.moreData == RequestTypes.GBT:
            p = GXDLMSLNParameters(self.settings, 0, XDLMSAPDU.GENERAL_BLOCK_TRANSFER, 0, None, None, 0xff)
            p.WindowSize = reply.windowSize
            p.blockNumberAck = reply.blockNumberAck
            p.blockIndex = reply.blockNumber
            p.Streaming = False
            reply = self.getLnMessages(p)  # TODO: test it
        else:
            #  Get next block.
            bb = GXByteBuffer(4)
            if self.settings.getUseLogicalNameReferencing():
                bb.setUInt32(self.settings.blockIndex)
            else:
                bb.setUInt16(self.settings.blockIndex)
            self.settings.increaseBlockIndex()
            if self.settings.getUseLogicalNameReferencing():
                p = GXDLMSLNParameters(self.settings, 0, cmd, pdu.GetResponse.WITH_DATABLOCK, bb, None, 0xff)
                reply = self.getLnMessages(p)
            else:
                p = GXDLMSSNParameters(self.settings, cmd, 1, VariableAccessSpecification.BLOCK_NUMBER_ACCESS, bb, None)
                reply = self.getSnMessages(p)
        return reply

    def set_params(self, field: str, value: str):
        self.__dict__[field] = eval(value)

    async def close(self):
        """close , media is open"""
        self.log(logL.DEB, "close")
        if self.level > OSI.DATA_LINK:
            try:
                # Release is call only for secured connections. All meters are not supporting Release and it's causing problems.
                if (
                    isinstance(self.com_profile, c_pf.TCPUDPIP)
                    or (
                        isinstance(self.com_profile, c_pf.HDLC)
                        and self.settings.cipher.security != Security.NONE
                    )
                ):
                    self.releaseRequest()
                    await self.read_data_block()
            except Exception:
                self.log(logL.WARN, "don't support release ReleaseRequest")
                pass
                #  All meters don't support release.
            finally:
                self.level = OSI.DATA_LINK
            # hdlc close
            try:
                res = await self.disconnect_request()
                # todo: handle res
            except Exception as e:
                self.log(logL.ERR, F'Disconnect request ERROR: {e.args[0]}')
        self.level -= OSI.DATA_LINK

    async def disconnect_request(self):
        """ Sent to server DISC """
        if isinstance(self.com_profile, c_pf.HDLC):
            self.add_frames_to_queue(frame.Control.DISC_P)
        else:
            self.releaseRequest()
        return await self.read_data_block()

    @cached_property
    def n_phases(self) -> int:
        """cached phases amount"""
        return self.objects.get_n_phases()

    async def encode(self,
                     obj: ic.COSEMInterfaceClasses,
                     index: int,
                     value: str | int) -> cdt.CommonDataType:
        """encode attribute value from string if possible, else return None(for CHOICE variant) during connection"""
        if (ret := obj.encode(index, value)) is not None:
            return ret
        else:
            await self.read_attribute(obj, index)
            ret = obj.get_attr(index).copy()
            ret.set(value)
            return ret

    # TODO: remove in future
    def parseApplicationAssociationResponse(self):
        """ Parse server's challenge if HLS authentication is used. Received reply from the server. todo: refactoring here """
        ic = 0
        value = cdt.OctetString(self.reply.data.get_data())
        match self.m_id:
            case mechanism_id.HIGH_GMAC:
                secret = self.settings.sourceSystemTitle
                bb = GXByteBuffer(value)
                bb.getUInt8()
                ic = bb.getUInt32()
            case mechanism_id.HIGH_SHA256:
                tmp2 = GXByteBuffer()
                tmp2.set(self.secret)
                tmp2.set(self.settings.sourceSystemTitle)
                tmp2.set(self.settings.cipher.systemTitle)
                tmp2.set(self.settings.ctoSChallenge)
                tmp2.set(self.settings.stoCChallenge)
                secret = tmp2.array()
            case mechanism_id.HIGH:                      secret = self.secret
            case mechanism_id.HIGH_ECDSA:                raise ValueError("ECDSA is not supported.")
            case _ as mech_id:                                    raise ValueError(F'{mech_id} is not supported')
        tmp = self.secure(ic, self.settings.ctoSChallenge, bytes(secret))
        challenge = cdt.OctetString(bytearray(tmp))
        equals = challenge == value
        if not equals:
            self.log(logL.DEB, "Invalid StoC:" + GXByteBuffer.hex(value, True) + "-" + GXByteBuffer.hex(tmp, True))
        if not equals:
            raise Exception("parseApplicationAssociationResponse failed. " + " Server to Client do not match.")
        self.level |= OSI.APPLICATION

    def secure(self, ic, data, secret: bytes) -> bytes:
        """ TODO: """
        if not isinstance(secret, bytes):
            raise ValueError(F'cipher is not bytes type, got {secret.__class__}')
        #  Get server Challenge.
        challenge = GXByteBuffer()
        #  Get shared secret
        match self.m_id:
            case mechanism_id.HIGH:
                if len(secret) != 16:
                    raise ValueError(F'length secret must be 16, got {len(secret)}')
                cipher = AES.new(secret, AES.MODE_ECB)
                ciphertext: bytes = cipher.encrypt(copy_with_align(data))
                return ciphertext
            case mechanism_id.HIGH_GMAC:
                challenge.set(data)
                d = challenge.array()
                #  SC is always Security.Authentication.
                p = AesGcmParameter(0, secret, self.settings.cipher.blockCipherKey, self.settings.cipher.authenticationKey)
                p.security = Security.AUTHENTICATION
                p.invocationCounter = ic
                p.type_ = CountType.TAG
                challenge.clear()
                challenge.setUInt8(Security.AUTHENTICATION)
                challenge.setUInt32(p.invocationCounter)
                challenge.set(GXDLMSChippering.encryptAesGcm(p, d))
                return challenge.array()
            case mechanism_id.HIGH_SHA256:
                challenge.set(secret)
                d = challenge.array()
                md = hashlib.sha256()
                md.update(d)
                return md.digest()
            case mechanism_id.HIGH_MD5:
                challenge.set(data)
                challenge.set(secret)
                d = challenge.array()
                md = hashlib.md5()
                md.update(d)
                return md.digest()
            case mechanism_id.HIGH_SHA1:
                challenge.set(data)
                challenge.set(secret)
                d = challenge.array()
                md = hashlib.sha1()
                md.update(d)
                return md.digest()
            case mechanism_id.HIGH_ECDSA:                    raise Exception("ECDSA is not supported.")
            case _ as err:                                  raise Exception(F'Not support {err}')

    def getApplicationAssociationRequest(self):
        """ Get challenge request if HLS authentication is used. """
        match self.m_id, self.secret:
            case mechanism_id.HIGH_ECDSA | mechanism_id.HIGH_GMAC, None: raise ValueError('Password is invalid.')
            case _: pass
        self.settings.resetBlockIndex()
        match self.m_id:
            case mechanism_id.HIGH_GMAC:                pw = self.settings.cipher.systemTitle
            case mechanism_id.HIGH_SHA256:
                tmp = GXByteBuffer()
                tmp.set(self.secret)
                tmp.set(self.settings.cipher.systemTitle)
                tmp.set(self.settings.sourceSystemTitle)
                tmp.set(self.settings.stoCChallenge)
                tmp.set(self.settings.ctoSChallenge)
                pw = tmp.array()
            case _:                                              pw = self.secret
        ic = 0
        if self.settings.cipher:
            ic = self.settings.cipher.invocationCounter
        challenge = self.secure(ic, self.settings.getStoCChallenge(), pw)
        if self.settings.getUseLogicalNameReferencing():
            return self.get_action_request_normal(
                meth_desc=ut.CosemMethodDescriptor((overview.ClassID.ASSOCIATION_LN, ut.CosemObjectInstanceId(F"0.0.40.0.0.255"), ut.CosemObjectMethodId(1))),
                # meth_desc=self.current_association.get_meth_descriptor(1),
                method=method.ReplyToHLSAuthentication(bytearray(challenge)))
        else:
            return self.method2(0xFA00, 12, 8, challenge, cdt.OctetString.TAG)  # TODO: rewrite old client.method

    def parseAARE(self, buff: GXByteBuffer) -> AcseServiceUser:
        #  Get AARE tag and length
        tag = buff.getUInt8()
        if self.settings.isServer:
            if tag != (BerType.APPLICATION | BerType.CONSTRUCTED | AARQapdu.PROTOCOL_VERSION):
                raise ValueError("Invalid tag.")
        else:
            if tag != (BerType.APPLICATION | BerType.CONSTRUCTED | AARQapdu.APPLICATION_CONTEXT_NAME):
                raise ValueError("Invalid tag.")
        if _GXCommon.getObjectCount(buff) > len(buff) - buff.position:
            raise ValueError("PDU: Not enough data.")
        resultComponent = AssociationResult.ACCEPTED
        resultDiagnosticValue = AcseServiceUser.NULL
        len_ = 0
        tag = 0
        while buff.position < len(buff):
            tag = buff.getUInt8()
            if tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.APPLICATION_CONTEXT_NAME:  # 0xA1
                # Get length.
                len_ = buff.getUInt8()
                if len(buff) - buff.position < len_:
                    raise ValueError("Encoding failed. Not enough data.")
                if buff.getUInt8() != 0x6:
                    raise ValueError("Encoding failed. Not an Object ID.")
                if self.settings.isServer and self.settings.cipher:
                    self.settings.cipher.setSecurity(Security.NONE)
                #  Object ID length.
                len_ = buff.getUInt8()
                tmp = bytearray(len_)
                buff.get(tmp)
                if tmp[:6] != bytearray(b'\x60\x85\x74\x05\x08\x01'):
                    raise Exception("Encoding failed. Invalid Application context name.")
                match tmp[6], self.settings.getUseLogicalNameReferencing():
                    case 1 | 3, True:  pass
                    case 2 | 4, False: pass
                    case _:            raise GXDLMSException(AssociationResult.REJECTED_PERMANENT, AcseServiceUser.APPLICATION_CONTEXT_NAME_NOT_SUPPORTED)
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLED_AP_TITLE:  # 0xA2
                #  Get length.
                if buff.getUInt8() != 3:
                    raise ValueError("Invalid tag.")
                if self.settings.isServer:
                    #  Choice for result (INTEGER, universal)
                    if buff.getUInt8() != BerType.OCTET_STRING:
                        raise ValueError("Invalid tag.")
                    len_ = buff.getUInt8()
                    tmp = bytearray(len_)
                    buff.get(tmp)
                    try:
                        self.settings.sourceSystemTitle = tmp
                    except Exception as ex:
                        raise ex
                else:
                    #  Choice for result (INTEGER, universal)
                    if buff.getUInt8() != BerType.INTEGER:
                        raise ValueError("Invalid tag.")
                    #  Get length.
                    if buff.getUInt8() != 1:
                        raise ValueError("Invalid tag.")
                    resultComponent = AssociationResult(buff.getUInt8())
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLED_AE_QUALIFIER:  # 0xA3
                tag = int()
                resultDiagnosticValue = AcseServiceUser.NULL
                len_ = buff.getUInt8()
                #  ACSE service user tag.
                tag = buff.getUInt8()
                len_ = buff.getUInt8()
                if self.settings.isServer:
                    calledAEQualifier = bytearray(len_)
                    buff.get(calledAEQualifier)
                else:
                    #  Result source diagnostic component.
                    tag = buff.getUInt8()
                    if tag != BerType.INTEGER:
                        raise ValueError("Invalid tag.")
                    len_ = buff.getUInt8()
                    if len_ != 1:
                        raise ValueError("Invalid tag.")
                    resultDiagnosticValue = AcseServiceUser(buff.getUInt8())
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLED_AP_INVOCATION_ID:  # 0xA4
                if self.settings.isServer:
                    #  Get len.
                    if buff.getUInt8() != 3:
                        raise ValueError("Invalid tag.")
                    #  Choice for result (Universal, Octetstring type)
                    if buff.getUInt8() != BerType.INTEGER:
                        raise ValueError("Invalid tag.")
                    if buff.getUInt8() != 1:
                        raise ValueError("Invalid tag length.")
                    #  Get value.
                    len_ = buff.getUInt8()
                else:
                    #  Get length.
                    if buff.getUInt8() != 0xA:
                        raise ValueError("Invalid tag.")
                    #  Choice for result (Universal, Octet string type)
                    if buff.getUInt8() != BerType.OCTET_STRING:
                        raise ValueError("Invalid tag.")
                    #  responding-AP-title-field
                    #  Get length.
                    len_ = buff.getUInt8()
                    tmp = bytearray(len_)
                    buff.get(tmp)
                    self.settings.setSourceSystemTitle(tmp)
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLED_AE_INVOCATION_ID:  # 0xA5
                len_ = buff.getUInt8()
                tag = buff.getUInt8()
                len_ = buff.getUInt8()
                self.settings.userId = buff.getUInt8()
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLING_AP_TITLE:  # 0xA6
                len_ = buff.getUInt8()
                tag = buff.getUInt8()
                len_ = buff.getUInt8()
                tmp = bytearray(len_)
                buff.get(tmp)
                try:
                    self.settings.setSourceSystemTitle(tmp)
                except Exception as ex:
                    raise ex
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.SENDER_ACSE_REQUIREMENTS:  # 0xAA
                len_ = buff.getUInt8()
                tag = buff.getUInt8()
                len_ = buff.getUInt8()
                tmp = bytearray(len_)
                buff.get(tmp)
                self.settings.setStoCChallenge(tmp)
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLING_AE_QUALIFIER:  # 0xA7
                len_ = buff.getUInt8()
                tag = buff.getUInt8()
                len_ = buff.getUInt8()
                self.settings.userId = buff.getUInt8()
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLING_AP_INVOCATION_ID:  # 0xA8
                if buff.getUInt8() != 3:
                    raise ValueError("Invalid tag.")
                if buff.getUInt8() != 2:
                    raise ValueError("Invalid length.")
                if buff.getUInt8() != 1:
                    raise ValueError("Invalid tag length.")
                #  Get value.
                len_ = buff.getUInt8()
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLING_AE_INVOCATION_ID:  # 0xA9
                len_ = buff.getUInt8()
                tag = buff.getUInt8()
                len_ = buff.getUInt8()
                self.settings.userId = buff.getUInt8()
            elif tag in (BerType.CONTEXT | AARQapdu.SENDER_ACSE_REQUIREMENTS, BerType.CONTEXT | AARQapdu.CALLING_AP_INVOCATION_ID):  # 0x88
                #  Get sender ACSE-requirements field component.
                if buff.getUInt8() != 2:
                    raise ValueError("Invalid tag.")
                if buff.getUInt8() != BerType.OBJECT_DESCRIPTOR:
                    raise ValueError("Invalid tag.")
                #  Get only value because client application is
                #  sending system title with LOW authentication.
                buff.getUInt8()
            elif tag in (BerType.CONTEXT | AARQapdu.MECHANISM_NAME, BerType.CONTEXT | AARQapdu.CALLING_AE_INVOCATION_ID):  # 0x89
                ch = buff.getUInt8()
                if buff.getUInt8() != 0x60:
                    raise ValueError("Invalid tag.")
                if buff.getUInt8() != 0x85:
                    raise ValueError("Invalid tag.")
                if buff.getUInt8() != 0x74:
                    raise ValueError("Invalid tag.")
                if buff.getUInt8() != 0x05:
                    raise ValueError("Invalid tag.")
                if buff.getUInt8() != 0x08:
                    raise ValueError("Invalid tag.")
                if buff.getUInt8() != 0x02:
                    raise ValueError("Invalid tag.")
                ch = buff.getUInt8()
                self.m_id.set(ch)  # TODO: maybe check with current?
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLING_AUTHENTICATION_VALUE:  # 0xAC
                len_ = buff.getUInt8()
                #  Get authentication information.
                if buff.getUInt8() != 0x80:
                    raise ValueError("Invalid tag.")
                len_ = buff.getUInt8()
                tmp = bytearray(len_)
                buff.get(tmp)
                match self.m_id:
                    case mechanism_id.LOW: self.settings.password = tmp
                    case _:               self.settings.ctoSChallenge = tmp
            elif tag == BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.USER_INFORMATION:  # 0xBE
                #  Check result component.  Some meters are returning invalid user-information if connection failed.
                # if resultComponent != AssociationResult.ACCEPTED and resultDiagnosticValue != SourceDiagnostic.NONE:
                #     raise exc.AssociationResultError(resultComponent)
                try:
                    len_ = buff.getUInt8()
                    if len(buff) - buff.position < len_:
                        raise ValueError("Not enough data.")
                    #  Encoding the choice for user information
                    tag = buff.getUInt8()
                    if tag != 0x4:
                        raise ValueError("Invalid tag.")
                    len_ = buff.getUInt8()
                    if len(buff) - buff.position < len_:
                        raise ValueError("Not enough data.")
                    #  Tag for xDLMS-Initate.response
                    tag = buff.getUInt8()
                    originalPos = 0
                    if tag in (XDLMSAPDU.GLO_INITIATE_RESPONSE, XDLMSAPDU.GLO_INITIATE_REQUEST,
                               XDLMSAPDU.GENERAL_GLO_CIPHERING, XDLMSAPDU.GENERAL_DED_CIPHERING):
                        buff.position = buff.position - 1
                        p = AesGcmParameter(0, self.settings.sourceSystemTitle, self.settings.cipher.blockCipherKey, self.settings.cipher.authenticationKey)
                        tmp = GXCiphering.decrypt(self.settings.cipher, p, buff)
                        buff.size = 0
                        buff.set(tmp)
                        self.settings.cipher.security = p.security
                        self.settings.cipher.securitySuite = p.securitySuite
                        tag = buff.getUInt8()
                    tmp2 = GXByteBuffer()
                    tmp2.setUInt8(0)
                    tag2 = XDLMSAPDU(tag)      # TODO: remove it
                    response = tag2 == XDLMSAPDU.INITIATE_RESPONSE
                    if response:
                        #  Optional usage field of the negotiated quality of service component
                        tag = buff.getUInt8()
                        if tag != 0:
                            len_ = buff.getUInt8()
                            buff.position = buff.position + len_
                    elif tag2 == XDLMSAPDU.INITIATE_REQUEST:
                        #  Optional usage field of the negotiated quality of service component
                        tag = buff.getUInt8()
                        if tag != 0:
                            len_ = buff.getUInt8()
                            tmp = bytearray(len_)
                            buff.get(tmp)
                            if self.settings.cipher:
                                self.settings.cipher.setDedicatedKey(tmp)
                        elif self.settings.cipher:
                            self.settings.cipher.dedicatedKey = None
                        #  Optional usage field of the negotiated quality of service component
                        tag = buff.getUInt8()
                        if tag != 0:
                            len_ = buff.getUInt8()
                        #  Optional usage field of the proposed quality of service component
                        tag = buff.getUInt8()
                        #  Skip if used.
                        if tag != 0:
                            len_ = buff.getUInt8()
                            buff.position = buff.position + len_
                    elif tag2 == XDLMSAPDU.CONFIRMED_SERVICE_ERROR:
                        raise GXDLMSConfirmedServiceError(ConfirmedServiceError(buff.getUInt8()), ServiceError(buff.getUInt8()), buff.getUInt8())
                    else:
                        raise ValueError("Invalid tag.")
                    #  Get DLMS version number.
                    if not response:
                        self.settings.dlmsVersion = buff.getUInt8()
                        if self.settings.dlmsVersion != 6:
                            if not self.settings.isServer:
                                raise ValueError("Invalid DLMS version number.")
                    else:
                        if buff.getUInt8() != 6:
                            raise ValueError("Invalid DLMS version number.")
                    #  Tag for conformance block
                    tag = buff.getUInt8()
                    if tag != 0x5F:
                        raise ValueError("Invalid tag.")
                    #  Old Way...
                    if buff.getUInt8(buff.position) == 0x1F:
                        buff.getUInt8()
                    len_ = buff.getUInt8()
                    #  The number of unused bits in the bit string.
                    tag = buff.getUInt8()
                    #getConformanceToArray todo: make better
                    v = _GXCommon.swapBits(buff.getUInt8())
                    v |= _GXCommon.swapBits(buff.getUInt8()) << 8
                    v |= _GXCommon.swapBits(buff.getUInt8()) << 16
                    if self.settings.isServer:
                        self.negotiated_conformance.set(v & self.settings.proposedConformance)
                    else:
                        self.negotiated_conformance.set(v)
                        self.log(logL.INFO, f"SET CONFORMANCE: {self.negotiated_conformance}")
                    if not response:
                        #  Proposed max PDU size.
                        pdu = buff.getUInt16()
                        self.settings.maxPduSize = pdu
                        #  If client asks too high PDU.
                        if pdu > self.settings.maxServerPDUSize:
                            self.settings.setMaxPduSize = self.settings.maxServerPDUSize
                    else:
                        pdu = buff.getUInt16()
                        if pdu < 64:
                            raise GXDLMSConfirmedServiceError(ConfirmedServiceError.INITIATE_ERROR, ServiceError.SERVICE, Service.PDU_SIZE)
                        #  Max PDU size.
                        self.settings.maxPduSize = pdu
                    if response:
                        #  VAA Name
                        tag = buff.getUInt16()
                        if tag == 0x0007:
                            if not self.settings.getUseLogicalNameReferencing():
                                raise ValueError("Invalid VAA.")
                        elif tag == 0xFA00:
                            #  If SN
                            if self.settings.getUseLogicalNameReferencing():
                                raise ValueError("Invalid VAA.")
                        else:
                            #  Unknown VAA.
                            raise ValueError("Invalid VAA.")
                except Exception:
                    raise GXDLMSException(AssociationResult.REJECTED_PERMANENT, AcseServiceUser.NO_REASON_GIVEN)
            elif tag == BerType.CONTEXT | AARQapdu.PROTOCOL_VERSION:  # 0x80
                buff.getUInt8()
                unusedBits = buff.getUInt8()
                value = buff.getUInt8()
                sb = _GXCommon.toBitString(value, 8 - unusedBits)
                self.settings.protocolVersion = sb
            else:
                #  Unknown tags.
                self.log(logL.DEB, "Unknown tag: " + str(tag) + ".")
                if buff.position < len(buff):
                    len_ = buff.getUInt8()
                    buff.position = buff.position + len_
        #  All meters don't send user-information if connection is failed.
        #  For this reason result component is check again.
        # if resultComponent != AssociationResult.ACCEPTED and resultDiagnosticValue != SourceDiagnostic.NONE:
        #     raise exc.AssociationResultError(resultComponent, resultDiagnosticValue)
        return resultDiagnosticValue

    def parseAareResponse(self, reply) -> AcseServiceUser:
        """ TODO: need refactoring. Parses the AARE response.  Parse method will update the following data: DLMSVersion, MaxReceivePDUSize, UseLogicalNameReferencing, LNSettings or SNSettings,
        LNSettings or SNSettings will be updated, depending on the referencing, Logical name or Short name.
        Received data. GXDLMSClient#aarqRequest GXDLMSClient#useLogicalNameReferencing GXDLMSClient#negotiatedConformance GXDLMSClient#proposedConformance """
        if (ret := self.parseAARE(reply)) != AcseServiceUser.AUTHENTICATION_REQUIRED:
            self.level |= OSI.APPLICATION
        if self.settings.dlmsVersion != 6:
            raise ValueError("Invalid DLMS version number.")
        return ret

    def generate_user_information(self, cipher, encryptedData) -> bytes:
        info = pack('B', BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.USER_INFORMATION)
        if not cipher or not cipher.isCiphered():
            #  Length for AARQ user field + oding the choice for user-information (Octet STRING, universal)
            info += b'\x10\x04'
            i_r: bytes = self.getInitiateRequest()
            info += pack(F'B{len(i_r)}s', len(i_r), i_r)
        else:
            if encryptedData:
                #  Length for AARQ user field
                info += pack('B', 4 + len(encryptedData))
                #  Tag
                info += pack('B', BerType.OCTET_STRING)
                info += pack('B', 2 + len(encryptedData))
                #  Coding the choice for user-information (Octet STRING,
                #  universal)
                info += pack('B', XDLMSAPDU.GLO_INITIATE_REQUEST)
                info += pack('B', len(encryptedData))
                info += pack(F'{len(encryptedData)}s', encryptedData)
            else:
                tmp: bytes = self.getInitiateRequest()
                p = AesGcmParameter(XDLMSAPDU.GLO_INITIATE_REQUEST, cipher.systemTitle, cipher.blockCipherKey, cipher.authenticationKey)
                p.security = cipher.security
                p.invocationCounter = cipher.invocationCounter
                crypted = bytes(GXCiphering.encrypt(p, tmp))
                #  Length for AARQ user field. Coding the choice for user-information (Octet string, universal)
                info += pack(F'BBB{len(crypted)}s',
                             2 + len(crypted),
                             BerType.OCTET_STRING,
                             len(crypted),
                             crypted)
        return info

    def getInitiateRequest(self) -> bytes:
        """DLMS UA 1000-2 Ed. 10. 11 AARQ and AARE encoding examples. 11.2 Encoding of the xDLMS InitiateRequest. Todo: rewrite with use UsefullTypes"""
        info = pack('B', XDLMSAPDU.INITIATE_REQUEST)
        if not self.settings.cipher or not self.settings.cipher.dedicatedKey:
            info += b'\x00'
        else:
            info += b'\x01' + cdt.encode_length(len(self.settings.cipher.dedicatedKey)) + bytes(self.settings.cipher.dedicatedKey)
        info += pack(
            ">3B4s3sH",
            0,                          # encoding of the response-allowed component (BOOLEAN DEFAULT TRUE) usage flag (FALSE, default value TRUE conveyed)
            self.quality_of_service,
            self._objects.dlms_ver if self._objects else self.DEF_DLMS_VER,
            b'\x5f\x1f\x04\x00',        # <5f1f> Tag for conformance block + <04>length of the conformance block + <00> encoding the number of unused bits in the bit string
            self.proposed_conformance.contents,
            self.receive_pdu_size)
        return info

    def aarqRequest(self, m_id: mechanism_id.MechanismIdElement):
        """ Generate AARQ request.  Because all_ meters can't read all_ data in one packet, the packet must be split first, by using SplitDataToPackets method.  AARQ request as
        byte array. @see GXDLMSClient#parseAareResponse """
        info = bytes()
        self.settings.resetBlockIndex()
        self.settings.setStoCChallenge(None)
        # if self.auto_increase_invoke_ID:
        #     self.settings.setInvokeID(0)
        # else:
        #     self.settings.setInvokeID(1)
        #  If authentication or ciphering is used.
        #  ProtocolVersion: BerType.CONTEXT | AARQ-apdu.PROTOCOL_VERSION + length(always 2) + unused bites + context
        if self.protocol_version.encoding != b'\x04\x01\x80':
            info += pack('2sBc', b'\x80\x02',
                         8 - len(self.protocol_version),
                         self.protocol_version.contents)
        #  Application context name tag. Where A1 - Tag, 09 - content name length, 06 - BerType.OBJECT_IDENTIFIER, 07 - info length
        info += b'\xa1\x09\x06\x07' + self.APP_CONTEXT_NAME.contents
        #  Add system title.
        ciphered = self.settings.cipher and self.settings.cipher.isCiphered()
        if not self.settings.isServer and (ciphered or m_id == mechanism_id.HIGH_GMAC) or m_id == mechanism_id.HIGH_ECDSA:
            if len(self.settings.cipher.systemTitle) != 8:
                raise ValueError("SystemTitle")
            #  Add calling-AP-title: BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLING_AP_TITLE + length + BerType.OCTET_STRING + length + systemTitle
            info += pack(F'cBcB{len(self.settings.cipher.systemTitle)}s',
                         b'\xa6',
                         2 + len(self.settings.cipher.systemTitle),
                         b'\x04',
                         len(self.settings.cipher.systemTitle),
                         self.settings.cipher.systemTitle)
        #  CallingAEInvocationId: BerType.CONTEXT | BerType.CONSTRUCTED | AARQapdu.CALLING_AE_INVOCATION_ID + length + BerType.INTEGER + length + userId
        if not self.settings.isServer and self.settings.userId != -1:
            info += pack(F'4sB',
                         b'\xa9\x03\x02\x01',
                         self.settings.userId)
        # Retrieves the string that indicates the level of authentication, if any.
        if m_id != mechanism_id.NONE or (self.settings.cipher and self.settings.cipher.security != Security.NONE):
            info += b'\x8a\x02\x07\x80'
            # Where: 8b - Tag(CONTEXT(0x80) + AARQ-apdu.MECHANISM_NAME(0x0b)), 07 - info length
            info += b'\x8b\x07' + AuthenticationMechanismName.get_AARQ_mechanism_name(
                cryptographic=2,
                algorithm_id=int(m_id))
        #  Add Calling authentication information.
        if m_id != mechanism_id.NONE:
            if m_id == mechanism_id.LOW:
                c_a_v = self.secret
                """ calling-authentication-value """
            elif m_id == mechanism_id.HIGH:
                self.settings.ctoSChallenge = os.urandom(16)
                c_a_v = self.settings.ctoSChallenge
            else:
                # TODO: must be 8..64 bytes length of urandom for different auth level
                self.settings.ctoSChallenge = os.urandom(16)
                c_a_v = self.settings.ctoSChallenge
            # BerType.CONTEXT | BerType.CONSTRUCTED | AARQ-apdu.CALLING_AUTHENTICATION_VALUE + length + context + info_len
            info += pack(F'cBBB{len(c_a_v)}s',
                         b'\xac',
                         2 + len(c_a_v),
                         BerType.CONTEXT,
                         len(c_a_v),
                         c_a_v)
        u_i = self.generate_user_information(self.settings.cipher, None)
        info = pack('BB', BerType.APPLICATION | BerType.CONSTRUCTED,
                    len(info + u_i)) + info + u_i
        p = GXDLMSLNParameters(self.settings, 0, ACSEAPDU.AARQ, 0, info, None, 0xff)
        return self.getLnMessages(p)

    def getLnMessages(self, p: GXDLMSLNParameters):
        reply = GXByteBuffer()
        messages = list()
        frame_ = 0
        if p.command == XDLMSAPDU.DATA_NOTIFICATION or p.command == XDLMSAPDU.EVENT_NOTIFICATION_REQUEST:
            frame_ = 0x13
        while True:
            # """ Get next logical name PDU. @param p LN parameters. @param reply Generated message. """
            ciphering = p.command != ACSEAPDU.AARQ and p.command != ACSEAPDU.AARE and self.settings.cipher and self.settings.cipher.security != Security.NONE
            len_ = 0
            if p.command == ACSEAPDU.AARQ:
                if self.settings.gateway and self.settings.gateway.physicalDeviceAddress:
                    reply.setUInt8(XDLMSAPDU.GATEWAY_REQUEST)
                    reply.setUInt8(self.settings.gateway.networkId)
                    reply.setUInt8(len(self.settings.gateway.physicalDeviceAddress))
                    reply.set(self.settings.gateway.physicalDeviceAddress)
                reply.set(p.attributeDescriptor)
            else:
                if p.command != XDLMSAPDU.GENERAL_BLOCK_TRANSFER:
                    reply.setUInt8(p.command)
                if p.command in (XDLMSAPDU.EVENT_NOTIFICATION_REQUEST, XDLMSAPDU.DATA_NOTIFICATION, XDLMSAPDU.ACCESS_REQUEST, XDLMSAPDU.ACCESS_RESPONSE):
                    if p.command != XDLMSAPDU.EVENT_NOTIFICATION_REQUEST:
                        if p.invokeId != 0:
                            reply.setUInt32(p.invokeId)
                        else:
                            reply.setUInt32(GXDLMS.getLongInvokeIDPriority(self.settings))
                    if p.time is None:
                        reply.setUInt8(cdt.NullData.TAG)
                    else:
                        pos = len(reply)
                        _GXCommon.setData(self.settings, reply, cdt.OctetString.TAG, p.getTime())
                        if p.command != XDLMSAPDU.EVENT_NOTIFICATION_REQUEST:
                            reply.move(pos + 1, pos, len(reply) - pos - 1)
                    GXDLMS.multipleBlocks(p, reply, ciphering)
                elif p.command != ACSEAPDU.RLRQ:
                    if p.command != XDLMSAPDU.GET_REQUEST and p.data and reply:
                        GXDLMS.multipleBlocks(p, reply, ciphering)
                    if p.command == XDLMSAPDU.SET_REQUEST:
                        if p.multipleBlocks and not self.negotiated_conformance.general_block_transfer:
                            if p.requestType == 1:
                                p.requestType = SetRequest.SET_REQUEST_FIRST_DATABLOCK
                            elif p.requestType == 2:
                                p.requestType = SetRequest.SET_REQUEST_WITH_DATABLOCK
                    if p.command == XDLMSAPDU.GET_RESPONSE:
                        if p.multipleBlocks and not self.negotiated_conformance.general_block_transfer:
                            if p.requestType == 1:
                                p.requestType = 2
                    if p.command != XDLMSAPDU.GENERAL_BLOCK_TRANSFER:
                        reply.setUInt8(p.requestType)
                        if p.invokeId != 0:
                            reply.setUInt8(p.invokeId)
                        else:
                            reply.setUInt8(GXDLMS.getInvokeIDPriority(self.settings))
                reply.set(p.attributeDescriptor)
                if self.settings.is_multiple_block() and self.negotiated_conformance.general_block_transfer:
                    if p.lastBlock:
                        reply.setUInt8(1)
                        self.settings.setCount(0)
                        self.settings.setIndex(0)
                    else:
                        reply.setUInt8(0)
                    reply.setUInt32(p.blockIndex)
                    p.blockIndex += 1
                    if p.status != 0xFF:
                        if p.status != 0 and p.command == XDLMSAPDU.GET_RESPONSE:
                            reply.setUInt8(1)
                        reply.setUInt8(p.status)
                    if p.data:
                        len_ = p.data.size - p.data.position
                    else:
                        len_ = 0
                    totalLength = len_ + len(reply)
                    if ciphering:
                        totalLength += GXDLMS._CIPHERING_HEADER_SIZE
                    if totalLength > self.settings.maxPduSize:
                        len_ = self.settings.maxPduSize - len(reply)
                        if ciphering:
                            len_ -= GXDLMS._CIPHERING_HEADER_SIZE
                        len_ -= _GXCommon.getObjectCountSizeInBytes(len_)
                    _GXCommon.setObjectCount(len_, reply)
                    reply.set(p.data, len_)
                if len_ == 0:
                    if p.status != 0xFF and p.command != XDLMSAPDU.GENERAL_BLOCK_TRANSFER:
                        if p.status != 0 and p.command == XDLMSAPDU.GET_RESPONSE:
                            reply.setUInt8(1)
                        reply.setUInt8(p.status)
                    if p.data:
                        len_ = p.data.size - p.data.position
                        if self.settings.gateway and self.settings.gateway.physicalDeviceAddress:
                            if 3 + len_ + len(self.settings.gateway.physicalDeviceAddress) > self.settings.maxPduSize:
                                len_ -= (3 + len(self.settings.gateway.physicalDeviceAddress))
                            tmp = GXByteBuffer(reply)
                            reply.size = 0
                            reply.setUInt8(XDLMSAPDU.GATEWAY_REQUEST)
                            reply.setUInt8(self.settings.gateway.networkId)
                            reply.setUInt8(len(self.settings.gateway.physicalDeviceAddress))
                            reply.set(self.settings.gateway.physicalDeviceAddress)
                            reply.set(tmp)
                        if self.negotiated_conformance.general_block_transfer:
                            if 7 + len_ + len(reply) > self.settings.maxPduSize:
                                len_ = self.settings.maxPduSize - len(reply) - 7
                            if ciphering and p.command != XDLMSAPDU.GENERAL_BLOCK_TRANSFER:
                                reply.set(p.data)
                                tmp = []
                                if self.settings.cipher.securitySuite == SecuritySuite.AES_GCM_128_AUT_ENCR_AND_AES_128_KEY_WRAP:
                                    tmp = self.cipher0(p, reply)
                                p.data.size = 0
                                p.data.set(tmp)
                                reply.size = 0
                                len_ = p.data.size
                                if 7 + len_ > self.settings.maxPduSize:
                                    len_ = self.settings.maxPduSize - 7
                                ciphering = False
                        elif p.command != XDLMSAPDU.GET_REQUEST and len_ + len(reply) > self.settings.maxPduSize:
                            len_ = self.settings.maxPduSize - len(reply)
                        reply.set(p.data, p.data.position, len_)
                    elif (self.settings.gateway and self.settings.gateway.physicalDeviceAddress) and \
                            not (p.command == XDLMSAPDU.GENERAL_BLOCK_TRANSFER or (p.multipleBlocks and self.negotiated_conformance.general_block_transfer)):
                        if 3 + len_ + len(self.settings.gateway.physicalDeviceAddress) > self.settings.maxPduSize:
                            len_ -= (3 + len(self.settings.gateway.physicalDeviceAddress))
                        tmp = GXByteBuffer(reply)
                        reply.size = 0
                        reply.setUInt8(XDLMSAPDU.GATEWAY_REQUEST)
                        reply.setUInt8(self.settings.gateway.networkId)
                        reply.setUInt8(len(self.settings.gateway.physicalDeviceAddress))
                        reply.set(self.settings.gateway.physicalDeviceAddress)
                        reply.set(tmp)
                if ciphering and reply and not self.negotiated_conformance.general_block_transfer and p.command != XDLMSAPDU.RELEASE_REQUEST:
                    tmp = []
                    if self.settings.cipher.securitySuite == SecuritySuite.AES_GCM_128_AUT_ENCR_AND_AES_128_KEY_WRAP:
                        tmp = self.cipher0(p, reply.array())
                    reply.size = 0
                    reply.set(tmp)
            if p.command == XDLMSAPDU.GENERAL_BLOCK_TRANSFER or (p.multipleBlocks and self.negotiated_conformance.general_block_transfer):
                bb = GXByteBuffer()
                bb.set(reply)
                reply.clear()
                reply.setUInt8(XDLMSAPDU.GENERAL_BLOCK_TRANSFER)
                value = 0
                if p.lastBlock:
                    value = 0x80
                elif p.streaming:
                    value |= 0x40
                value |= p.windowSize
                reply.setUInt8(value)
                reply.setUInt16(p.blockIndex)
                p.blockIndex += 1
                if p.command != XDLMSAPDU.DATA_NOTIFICATION and p.blockNumberAck != 0:
                    reply.setUInt16(p.blockNumberAck)
                    p.blockNumberAck += 1
                else:
                    p.blockNumberAck = -1
                    reply.setUInt16(0)
                _GXCommon.setObjectCount(len(bb), reply)
                reply.set(bb)
                if p.command != XDLMSAPDU.GENERAL_BLOCK_TRANSFER:
                    p.command = XDLMSAPDU.GENERAL_BLOCK_TRANSFER
                    p.blockNumberAck += 1
                if self.settings.gateway and self.settings.gateway.physicalDeviceAddress:
                    if 3 + len_ + len(self.settings.gateway.physicalDeviceAddress) > self.settings.maxPduSize:
                        len_ -= (3 + len(self.settings.gateway.physicalDeviceAddress))
                    tmp = GXByteBuffer(reply)
                    reply.size = 0
                    reply.setUInt8(XDLMSAPDU.GATEWAY_REQUEST)
                    reply.setUInt8(self.settings.gateway.networkId)
                    reply.setUInt8(len(self.settings.gateway.physicalDeviceAddress))
                    reply.set(self.settings.gateway.physicalDeviceAddress)
                    reply.set(tmp)

            p.lastBlock = True
            if p.attributeDescriptor is None:
                self.settings.increaseBlockIndex()
            if p.command == ACSEAPDU.AARQ and p.command == XDLMSAPDU.GET_REQUEST:
                assert not self.settings.maxPduSize < len(reply)
            match self.com_profile:
                case c_pf.TCPUDPIP():
                    messages.append(GXDLMS.getWrapperFrame(self.settings, p.command, reply))  # TODO: rewrite getWrapperFrame with return list[bytes]
                case c_pf.HDLC():
                    self.add_frames_to_queue(frame.Control(frame_), bytes(reply.array()))
                case _:
                    raise ValueError("InterfaceType")
            reply.clear()
            frame_ = 0
            if not p.data or p.data.position == p.data.size:
                break
        return messages

    def get_get_request_normal(self, attr_desc: ut.CosemAttributeDescriptor | ut.CosemAttributeDescriptorWithSelection):
        p = GXDLMSLNParameters(settings=self.settings,
                               invokeId=0,
                               command=XDLMSAPDU.GET_REQUEST,
                               requestType=pdu.GetResponse.NORMAL,
                               attributeDescriptor=GXByteBuffer(attr_desc.contents),
                               data=None,
                               status=0xFF)
        return self.getLnMessages(p)

    def get_set_request_normal(self, obj: ic.COSEMInterfaceClasses, attr_index: int, value: bytes = None):
        self.settings.resetBlockIndex()
        access_selection_parameters = b'\x00'
        attribute_descriptor = GXByteBuffer(obj.get_attribute_descriptor(attr_index) + access_selection_parameters)
        data = GXByteBuffer()
        if value:
            data.set(value)
        else:
            attr = obj.get_attr(attr_index)
            data.set(attr.encoding)                                              # add raw data
        p = GXDLMSLNParameters(self.settings, 0, XDLMSAPDU.SET_REQUEST, SetRequest.SET_REQUEST_NORMAL, attribute_descriptor, data, 0xff)
        p.blockIndex = self.settings.blockIndex
        p.blockNumberAck = self.settings.blockNumberAck
        p.streaming = False
        return self.getLnMessages(p)

    def get_set_request_normal2(self, attr_desc: ut.CosemAttributeDescriptor, value: cdt.CommonDataTypes):
        self.settings.resetBlockIndex()
        attribute_descriptor = GXByteBuffer(attr_desc.contents)
        data = GXByteBuffer(value.encoding)
        p = GXDLMSLNParameters(self.settings, 0, XDLMSAPDU.SET_REQUEST, SetRequest.SET_REQUEST_NORMAL, attribute_descriptor, data, 0xff)
        p.blockIndex = self.settings.blockIndex
        p.blockNumberAck = self.settings.blockNumberAck
        p.streaming = False
        return self.getLnMessages(p)

    @deprecated("use get_action_request_normal")
    def get_action_request_normal_old(self, meth_desc: ut.CosemMethodDescriptor):
        self.settings.resetBlockIndex()
        method = self.objects.get_object(meth_desc).get_meth(int(meth_desc.method_id))
        method_invocation_parameters = GXByteBuffer(cdt.Boolean(b'\x03' + method.TAG).contents + method.encoding)
        method_descriptor = GXByteBuffer(meth_desc.contents)
        p = GXDLMSLNParameters(self.settings, 0, XDLMSAPDU.ACTION_REQUEST, ActionRequest.NORMAL, method_descriptor, method_invocation_parameters, 0xff)
        return self.getLnMessages(p)

    def get_action_request_normal(self, meth_desc: ut.CosemMethodDescriptor, method: cdt.CommonDataType):
        """method: specific method"""
        self.settings.resetBlockIndex()
        method_invocation_parameters = GXByteBuffer(cdt.Boolean(b'\x03' + method.TAG).contents + method.encoding)
        method_descriptor = GXByteBuffer(meth_desc.contents)
        p = GXDLMSLNParameters(self.settings, 0, XDLMSAPDU.ACTION_REQUEST, ActionRequest.NORMAL, method_descriptor, method_invocation_parameters, 0xff)
        return self.getLnMessages(p)

    def releaseRequest(self):
        # TODO: rewrite
        info = b'\x03\x80\x01\x00'
        if self.use_protected_release:
            #Increase IC.
            if self.settings.cipher and self.settings.cipher.isCiphered:
                self.settings.cipher.invocationCounter = self.settings.cipher.invocationCounter + 1
            info += self.generate_user_information(self.settings.cipher, None)
            info = pack('H', len(info)) + info
        buff = GXByteBuffer(info)
        if self.settings.getUseLogicalNameReferencing():
            p = GXDLMSLNParameters(self.settings, 0, ACSEAPDU.RLRQ, 0, buff, None, 0xff)
            reply = self.getLnMessages(p)
        else:
            reply = self.getSnMessages(GXDLMSSNParameters(self.settings, ACSEAPDU.RLRQ, 0xFF, 0xFF, None, buff))
        self.level -= OSI.APPLICATION
        return reply

    @classmethod
    def getGloMessage(cls, command: XDLMSAPDU | ACSEAPDU) -> XDLMSAPDU | ACSEAPDU:
        """ Get used glo message. Executed command. Integer value of glo message."""
        match command:
            case XDLMSAPDU.READ_REQUEST:      return XDLMSAPDU.GLO_READ_REQUEST
            case XDLMSAPDU.GET_REQUEST:       return XDLMSAPDU.GLO_GET_REQUEST
            case XDLMSAPDU.WRITE_REQUEST:     return XDLMSAPDU.GLO_WRITE_REQUEST
            case XDLMSAPDU.SET_REQUEST:       return XDLMSAPDU.GLO_SET_REQUEST
            case XDLMSAPDU.ACTION_REQUEST:    return XDLMSAPDU.GLO_ACTION_REQUEST
            case XDLMSAPDU.READ_RESPONSE:     return XDLMSAPDU.GLO_READ_RESPONSE
            case XDLMSAPDU.GET_RESPONSE:      return XDLMSAPDU.GLO_GET_RESPONSE
            case XDLMSAPDU.WRITE_RESPONSE:    return XDLMSAPDU.GLO_WRITE_RESPONSE
            case XDLMSAPDU.SET_RESPONSE:      return XDLMSAPDU.GLO_SET_RESPONSE
            case XDLMSAPDU.ACTION_RESPONSE:   return XDLMSAPDU.GLO_ACTION_RESPONSE
            case XDLMSAPDU.DATA_NOTIFICATION: return XDLMSAPDU.GENERAL_GLO_CIPHERING
            case ACSEAPDU.RLRQ:               return ACSEAPDU.RLRQ
            case ACSEAPDU.RLRE:               return ACSEAPDU.RLRE
            case _:                         raise Exception("Invalid GLO command.")

    @classmethod
    def getDedMessage(cls, command: XDLMSAPDU | ACSEAPDU) -> XDLMSAPDU | ACSEAPDU:
        """ Get used ded message. Executed command. Integer value of ded message. """
        match command:
            case XDLMSAPDU.GET_REQUEST:       return XDLMSAPDU.DED_GET_REQUEST
            case XDLMSAPDU.SET_REQUEST:       return XDLMSAPDU.DED_SET_REQUEST
            case XDLMSAPDU.ACTION_REQUEST:    return XDLMSAPDU.DED_ACTION_REQUEST
            case XDLMSAPDU.GET_RESPONSE:      return XDLMSAPDU.DED_GET_RESPONSE
            case XDLMSAPDU.SET_RESPONSE:      return XDLMSAPDU.DED_SET_RESPONSE
            case XDLMSAPDU.ACTION_RESPONSE:   return XDLMSAPDU.DED_ACTION_RESPONSE
            case XDLMSAPDU.DATA_NOTIFICATION: return XDLMSAPDU.GENERAL_DED_CIPHERING
            case ACSEAPDU.RLRQ:               return ACSEAPDU.RLRQ
            case ACSEAPDU.RLRE:               return ACSEAPDU.RLRE
            case _:                         raise Exception("Invalid DED command.")

    def cipher0(self, p: GXDLMSLNParameters, data: GXByteBuffer):
        cmd = 0
        key = None
        cipher = p.settings.cipher
        if not self.negotiated_conformance.general_protection:
            if cipher.dedicatedKey and (OSI.APPLICATION in self.level):  # todo: maybe level is wrong
                cmd = self.getDedMessage(p.command)
                key = cipher.dedicatedKey
            else:
                cmd = self.getGloMessage(p.command)
                key = cipher.blockCipherKey
        else:
            if cipher.dedicatedKey:
                cmd = XDLMSAPDU.GENERAL_DED_CIPHERING
                key = cipher.dedicatedKey
            else:
                cmd = XDLMSAPDU.GENERAL_GLO_CIPHERING
                key = cipher.blockCipherKey
        cipher.invocationCounter = cipher.invocationCounter + 1
        s = AesGcmParameter(cmd, cipher.systemTitle, key, cipher.authenticationKey)
        s.ignoreSystemTitle = p.settings.standard == Standard.ITALY
        s.security = cipher.security
        s.invocationCounter = cipher.invocationCounter
        tmp = GXCiphering.encrypt(s, data)
        if p.command == XDLMSAPDU.DATA_NOTIFICATION or p.command == XDLMSAPDU.GENERAL_GLO_CIPHERING or p.command == XDLMSAPDU.GENERAL_DED_CIPHERING:
            reply = GXByteBuffer()
            reply.setUInt8(tmp[0])
            if p.settings.getStandard() == Standard.ITALY:
                reply.setUInt8(0)
            else:
                _GXCommon.setObjectCount(len(p.settings.cipher.systemTitle), reply)
                reply.set(p.settings.cipher.systemTitle)
            reply.set(tmp, 1, len(tmp))
            return reply.array()
        return tmp

    @property
    def current_association(self) -> AssociationLN:
        return self.objects.sap2association(self.SAP)

    def get_SNRM_request(self):
        """ Generates SNRM request.  his method is used to generate send SNRMRequest. Before the SNRM request can be generated, at least the following properties must be set:
        ClientAddress, ServerAddress.
        According to IEC 62056-47: when communicating using TCP/IP, the SNRM request is not send. """
        self.add_frames_to_queue(control=frame.Control.SNRM_P)

    def add_frames_to_queue(self, control: frame.Control, data: bytes = bytes()):
        """ Create and set new frames to queue """
        new_frames: Deque[frame.Frame] = deque()
        """ frames container """
        if control == frame.Control.SNRM_P:
            info = self.com_profile.negotiation.SNRM
        elif control.is_information():
            info = sub_layer.LLC(message=data).content
            """ HDLS info field """
        else:
            info = bytes()
            if len(data) != 0:
                raise ValueError('Warning DATA not empty, but frame not info')
        while True:
            info3 = info[:self.com_profile.negotiation.max_info_transmit]
            info = info[self.com_profile.negotiation.max_info_transmit:]
            new_frames.append(frame.Frame(control=control if control != 0 else self.settings.getNextSend(True),
                                          DA=self.DA,
                                          SA=self.SA,
                                          info=info3,
                                          is_segmentation=bool(len(info))
                                          ))
            if len(info) == 0:
                break
            else:
                control = frame.Control(self.settings.getNextSend(False))
        self.send_frames.extend(new_frames)

    def __str__(self):
        if not self._objects or not self._objects.LDN.value:
            return str(self.id)
        else:
            return self._objects.LDN.value.to_str()

    def get_serial_number(self) -> str:
        """ return serial number as text. If serial object is absence return 'недоступен' """
        if self._objects is None:
            return "нет типа"
        obj = self._objects.serial_number
        if isinstance(obj, Data) and obj.value is not None:
            if isinstance(obj.value, cdt.OctetString):
                return obj.value.to_str()
            else:
                return str(obj.value)
        else:
            return 'недоступен'

    async def read_attribute(self, obj: ic.COSEMInterfaceClasses | str,
                             attr_index: int):
        # TODO: redundant, use read_attr?
        if isinstance(obj, str):
            obj = self.objects.get_object(obj)
        self.get_get_request_normal(obj.get_attr_descriptor(
            value=attr_index,
            with_selection=bool(self.negotiated_conformance.selective_access)))
        start_read_time: float = time.perf_counter()
        await self.read_data_block()
        self.last_transfer_time = datetime.timedelta(seconds=time.perf_counter()-start_read_time)
        obj.set_attr(attr_index, self.reply.data.get_data())

    async def read_attr(self, attr_desc: ut.CosemAttributeDescriptor) -> bytes:
        """instead <read_attribute> in future. Read and return encoding"""
        self.get_get_request_normal(attr_desc)
        await self.read_data_block()
        return self.reply.data.get_data()

    def recv_attr_value(self, attr_desc: ut.CosemAttributeDescriptor) -> cdt.CommonDataTypes:
        """receive attribute value from server"""
        obj = self.objects.get_object(attr_desc)
        index = int(attr_desc.attribute_id)
        obj.set_attr(index=index,
                     value=self.read_attr(attr_desc))
        return obj.get_attr(index)

    async def write_attr2(self, attr_desc: ut.CosemAttributeDescriptor, value: cdt.CommonDataTypes):
        data = self.get_set_request_normal2(attr_desc, value)
        await self.read_data_block()

    @deprecated("use execute_method2")
    async def execute_method(self, meth_desc: ut.CosemMethodDescriptor):
        data = self.get_action_request_normal_old(meth_desc)
        await self.read_data_block()

    async def execute_method2(self, obj: ic.COSEMInterfaceClasses, i: int, mip=None):
        data = self.get_action_request_normal(
            meth_desc=obj.get_meth_descriptor(i),
            method=obj.get_meth_element(i).DATA_TYPE() if mip is None else mip)
        await self.read_data_block()

    async def is_equal_attribute(self, obj: ic.COSEMInterfaceClasses, attr_index: int | str, with_time: bool | datetime.datetime = False) -> bool:
        self.get_get_request_normal(obj.get_attr_descriptor(attr_index))
        await self.read_data_block()
        if obj.get_attr(attr_index).encoding == self.reply.data.get_data():
            return True
        else:
            # self.set_error(Application.VALUE_ERROR, F'{obj} attr-{attr_index}: got {self.reply.data.get_data()} must {obj[attr_index]}')
            return False
