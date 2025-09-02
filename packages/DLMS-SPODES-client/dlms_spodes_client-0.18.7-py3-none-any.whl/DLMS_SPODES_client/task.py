import asyncio
import random
from copy import copy
import re
from typing_extensions import deprecated
import hashlib
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Protocol, cast, override
from itertools import count
import datetime
import time
from semver import Version as SemVer
from StructResult import result
from DLMS_SPODES.pardata import ParValues
from DLMS_SPODES.types.implementations import enums, long_unsigneds, bitstrings, octet_string, structs, arrays
from DLMS_SPODES.pardata import ParData
from DLMS_SPODES.cosem_interface_classes.parameter import Parameter
from DLMS_SPODES import exceptions as exc, pdu_enums as pdu
from DLMS_SPODES.cosem_interface_classes import (
    cosem_interface_class as ic,
    collection,
    overview,
    ln_pattern
)
from DLMS_SPODES.cosem_interface_classes.clock import Clock
from DLMS_SPODES.cosem_interface_classes.image_transfer.image_transfer_status import ImageTransferStatus
from DLMS_SPODES.cosem_interface_classes.image_transfer.ver0 import ImageTransferInitiate, ImageBlockTransfer
from DLMS_SPODES.cosem_interface_classes.association_ln.ver0 import ObjectListType, ObjectListElement
from DLMS_SPODES.cosem_interface_classes import association_ln
from DLMS_SPODES.types import cdt, ut, cst
from DLMS_SPODES.hdlc import frame
from DLMS_SPODES.enums import Transmit, Application, Conformance
from DLMS_SPODES.firmwares import get_firmware
from DLMS_SPODES.cosem_interface_classes.image_transfer import image_transfer_status as i_t_status
from DLMSAdapter.main import AdapterException, Adapter, gag
from DLMSCommunicationProfile.osi import OSI
from .client import Client, logL, Security, Data, mechanism_id, AcseServiceUser, State


firm_id_pat = re.compile(b".*(?P<fid>PWRM_M2M_[^_]{1,10}_[^_]{1,10}).+")
boot_ver_pat = re.compile(b"(?P<boot_ver>\\d{1,4}).+")


type Errors = list[Exception]


class Base[T: result.Result](Protocol):
    """Exchange task for DLMS client"""
    msg: str

    def __post_init__(self) -> None:
        if self.msg == "":
            self.msg = self.__class__.__name__

    @property
    def current(self) -> 'Base[T]':
        return self

    async def run(self, c: Client) -> T | result.Error:
        """exception handling block"""
        try:
            return await self.physical(c)
        except (ConnectionRefusedError, TimeoutError) as e:
            return result.Error.from_e(e)
        except exc.DLMSException as e:
            return result.Error.from_e(e)
        except Exception as e:
            return result.Error.from_e(e)
        # except asyncio.CancelledError as e:
        #     await c.close()  # todo: change to DiscRequest
        #     return result.Error.from_e(exc.Abort("manual stop"))  # for handle BaseException
        finally:
            c.received_frames.clear()  # for next exchange need clear all received frames. todo: this bag, remove in future

    async def PH_connect(self, c: Client) -> result.Ok | result.Error:
        if c.media is None:
            return result.Error.from_e(exc.NoPort("no media"), "PH_connect")
        elif not c.media.is_open():
            await c.media.open()
        c.level = OSI.PHYSICAL
        c.log(logL.INFO, F"Open port communication channel: {c.media}")
        # todo: replace to <data_link>
        if (
            c._objects is None
            and not isinstance(self, InitType)
        ):
            if isinstance(res := await init_type.data_link(c), result.Error):
                return res.with_msg("PH_connect")
            await c.close()  # todo: change to DiscRequest, or make not closed or reconnect !!!
        return result.OK

    @staticmethod
    async def physical_t(c: Client):
        await c.close()  # todo: change to DiscRequest

    async def physical(self, c: Client) -> T | result.Error:
        if OSI.PHYSICAL not in c.level:
            if isinstance((res := await self.PH_connect(c)), result.Error):
                return res
        ret = await self.data_link(c)
        await self.physical_t(c)
        return ret

    async def DL_connect(self, c: Client):
        """Data link Layer connect"""
        c.send_frames.clear()
        # calculate addresses  todo: move to c.com_profile(HDLC)
        c.DA = frame.Address(
            upper_address=int(c.server_SAP),
            lower_address=c.com_profile.parameters.device_address,
            length=c.addr_size
        )
        c.SA = frame.Address(upper_address=int(c.SAP))
        c.log(logL.INFO, F"{c.SA=} {c.DA=}")
        # initialize connection
        c.reply.clear()
        # replace this
        if c.settings.cipher.security != Security.NONE:
            c.log(logL.DEB, F"Security: {c.settings.cipher.security}/n"
                            F"System title: {c.settings.cipher.systemTitle.hex()}"
                            F"Authentication key: {c.settings.cipher.authenticationKey.hex()}"
                            F"Block cipher key: {c.settings.cipher.blockCipherKey.hex()}")
            if c.settings.cipher.dedicatedKey:
                c.log(logL.DEB, F"Dedicated key: {c.settings.cipher.dedicatedKey.hex()}")
        # SNRM
        c.get_SNRM_request()
        await c.read_data_block()
        c.level = OSI.DATA_LINK
        c.reply.clear()

    async def data_link(self, c: Client) -> T | result.Error:
        if OSI.DATA_LINK not in c.level:
            await self.DL_connect(c)
        # todo: make tile
        return await self.application(c)

    async def AA(self, c: Client):
        """Application Associate"""
        if c.invocationCounter and c.settings.cipher is not None and c.settings.cipher.security != Security.NONE:
            # create IC object. TODO: remove it after close connection, maybe???
            c.settings.proposedConformance |= Conformance.GENERAL_PROTECTION

            # my block
            IC: Data = c._objects.add_if_missing(ut.CosemClassId(1),
                                                 logical_name=cst.LogicalName(bytearray((0, c.get_channel_index(), 43, 1,
                                                                                        c.current_association.security_setup_reference.e, 255))),
                                                 version=cdt.Unsigned(0))
            tmp_client_SAP = c.current_association.associated_partners_id.client_SAP
            challenge = c.settings.ctoSChallenge
            try:
                c.aarqRequest(c.m_id)
                await c.read_data_block()
                ret = c.parseAareResponse(c.reply.data)
                c.level |= OSI.APPLICATION  # todo: it's must be result of <ret> look down
                c.reply.clear()
                await c.read_attribute(IC, 2)
                c.settings.cipher.invocationCounter = 1 + int(IC.value)
                c.log(logL.DEB, "Invocation counter: " + str(c.settings.cipher.invocationCounter))
                # disconnect
                if c.media and c.media.is_open():
                    c.log(logL.DEB, "DisconnectRequest")
                    await c.disconnect_request()
            finally:
                c.SAP = tmp_client_SAP
                c.settings.useCustomChallenge = challenge is not None
                c.settings.ctoSChallenge = challenge

            # gurux with several removed methods
            # add = self.settings.clientAddress
            # auth = self.settings.authentication
            # security = self.client.ciphering.security
            # challenge = self.client.ctoSChallenge
            # try:
            #     self.client.clientAddress = 16
            #     self.settings.authentication = Authentication.NONE
            #     self.client.ciphering.security = Security.NONE
            #     reply = GXReplyData()
            #     self.get_SNRM_request()
            #     self.status = Status.READ
            #     self.read_data_block2()
            #     self.objects.IEC_HDLS_setup.set_from_info(self.reply.data.get_data())
            #     self.connection_state = ConnectionState.HDLC
            #     self.reply.clear()
            #     self.aarqRequest()
            #     self.read_data_block2()
            #     self.parseAareResponse(reply.data)
            #     reply.clear()
            #     item = GXDLMSData(self.invocationCounter)
            #     data = self.client.read(item, 2)[0]
            #     reply = GXReplyData()
            #     self.read_data_block(data, reply)
            #     item.encodings[2] = reply.data.get_data()
            #     Update data type on read.
            #     if item.getDataType(2) == cdt.NullData.TAG:
            #         item.setDataType(2, reply.valueType)
            #     self.client.updateValue(item, 2, reply.value)
            #     self.client.ciphering.invocationCounter = 1 + item.value
            #     print("Invocation counter: " + str(self.client.ciphering.invocationCounter))
            #     if self.media and self.media.isOpen():
            #         self.log(logL.INFO, "DisconnectRequest")
            #         self.disconnect_request()
            # finally:
            #     self.settings.clientAddress = add
            #     self.settings.authentication = auth
            #     self.client.ciphering.security = security
            #     self.client.ctoSChallenge = challenge

        c.aarqRequest(c.m_id)
        await c.read_data_block()
        # await c.read_attr(ut.CosemAttributeDescriptor((collection.ClassID.ASSOCIATION_LN, ut.CosemObjectInstanceId("0.0.40.0.0.255"), ut.CosemObjectAttributeId(6)))) # for test only
        match c.parseAareResponse(c.reply.data):
            case AcseServiceUser.NULL:
                c.log(logL.INFO, 'Authentication success')
                c.level |= OSI.APPLICATION
            case AcseServiceUser.AUTHENTICATION_REQUIRED:
                c.reply.clear()
                c.getApplicationAssociationRequest()
                await c.read_data_block()
                c.parseApplicationAssociationResponse()
            case _ as diagnostic:
                raise exc.AssociationResultError(diagnostic)
        if c._objects is not None:
            c.get_get_request_normal(c._objects.LDN.get_attr_descriptor(2))
            await c.read_data_block()
            if c.is_universal():
                await change_ldn.exchange(c)
            else:
                await match_ldn.exchange(c)

    async def application(self, c: Client) -> T | result.Error:
        if OSI.APPLICATION not in c.level:
            await self.AA(c)
        # no tile
        return await self.exchange(c)

    async def exchange(self, c: Client) -> T | result.Error:
        """application level exchange"""

    async def connect(self, c: Client) -> None:
        await self.PH_connect(c)
        await self.DL_connect(c)
        await self.AA(c)


class Simple[T](Base[result.Simple[T]], Protocol):
    """Simple result"""
    @override
    async def exchange(self, c: Client) -> result.SimpleOrError[T]: ...


class Boolean(Simple[bool], Protocol):
    """Simple[bool] result"""
    @override
    async def exchange(self, c: Client) -> result.SimpleOrError[bool]: ...


class CDT[T: cdt.CommonDataType](Simple[T], Protocol):
    """Simple[CDT] result"""
    @override
    async def exchange(self, c: Client) -> result.SimpleOrError[T]: ...


class List[T](Base[result.List[T]], Protocol):
    """With List result"""
    @override
    async def exchange(self, c: Client) -> result.List[T] | result.Error: ...


class OK(Base[result.Ok], Protocol):
    """Always result OK"""

    @override
    async def exchange(self, c: Client) -> result.Ok | result.Error: ...


@dataclass
class ClientBlocking(Base):
    """complete by time or abort"""
    delay: Optional[float] = field(default=99999999.0)
    msg: str = ""

    async def run(self, c: Client) -> result.Ok:
        try:
            c.level = OSI.APPLICATION
            c.log(logL.WARN, F"blocked for {self.delay} second")
            await asyncio.sleep(self.delay)
            return result.OK
        finally:
            c.level = OSI.NONE

    async def exchange(self, c: Client) -> result.Result:
        raise RuntimeError(f"not support for {self.__class__.__name__}")


# todo: make with <data_link>
class TestDataLink(Base):
    msg: str = ""

    async def physical(self, c: Client):
        if OSI.PHYSICAL not in c.level:
            if not c.media.is_open():
                await c.media.open()
            c.level = OSI.PHYSICAL
            c.DA = frame.Address(
                upper_address=int(c.server_SAP),
                lower_address=c.com_profile.parameters.device_address,
                length=c.addr_size
            )
            c.SA = frame.Address(upper_address=int(c.SAP))
            c.get_SNRM_request()
            await c.read_data_block()
            c.level = OSI.DATA_LINK
            await c.close()  # todo: change to DiscRequest

    async def exchange(self, c: Client):
        return result.OK


@dataclass
class Dummy(OK):
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        """"""
        return result.OK


@dataclass
class HardwareDisconnect(OK):
    msg: str = ""

    @override
    async def exchange(self, c: Client) -> result.Ok | result.Error:
        await c.media.close()
        c.level = OSI.NONE
        msg = '' if self.msg is None else F": {self.msg}"
        c.log(logL.WARN, F"HARDWARE DISCONNECT{msg}")
        return result.OK


@dataclass
class HardwareReconnect(OK):
    delay: int = 0
    """delay between disconnect and restore Application"""
    msg: str = "reconnect media without response"

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        if isinstance((res := await HardwareDisconnect().exchange(c)), result.Error):
            return res
        if self.delay != 0:
            c.log(logL.INFO, F"delay({self.delay})")
            await asyncio.sleep(self.delay)
        await self.connect(c)  # restore Application
        return result.OK


@dataclass
class Loop(OK):
    task: Base[result.Result]
    func: Callable[[Any], bool]
    delay: int
    msg: str = ""
    attempt_amount: int = 0
    """0 is never end loop"""

    async def run(self, c: Client) -> result.Result:
        attempt = count()
        while not self.func(await super(Loop, self).run(c)):
            if next(attempt) == self.attempt_amount:
                return result.Error.from_e(ValueError("end of attempts"))
            await asyncio.sleep(self.delay)
        return result.OK

    async def exchange(self, c: Client) -> result.Result:
        return await self.task.exchange(c)


@dataclass
class ConditionalTask[T](Base):
    """Warning: experimental"""
    precondition_task: Base[result.Result]
    comp_value: T
    predicate: Callable[[T, T], bool]
    main_task: Base[result.Result]
    msg: str = ""

    async def exchange(self, c: Client) -> result.Result:
        res = await self.precondition_task.exchange(c)
        if self.predicate(self.comp_value, res.value):
            return await self.main_task.exchange(c)
        return result.Error.from_e(ValueError("Condition not satisfied"))


@dataclass
class Scheduler[T](Boolean):
    """𝑟𝑒𝑝𝑒𝑡𝑖𝑡𝑖𝑜𝑛_𝑑𝑒𝑙𝑎𝑦 = 𝑟𝑒𝑝𝑒𝑡𝑖𝑡𝑖𝑜𝑛_𝑑𝑒𝑙𝑎𝑦_𝑚𝑖𝑛 × (𝑟𝑒𝑝𝑒𝑡𝑖𝑡𝑖𝑜𝑛_𝑑𝑒𝑙𝑎𝑦_𝑒𝑥𝑝𝑜𝑛𝑒𝑛𝑡 × 0.01) ** 𝑛"""
    task: Base[T]
    execution_datetime: Optional[cdt.DateTime] = None
    start_interval: int = 0
    number_of_retries: int = 3
    total_of_retries: int = 100
    repetition_delay_min: int = 1
    repetition_delay_exponent: int = 100
    repetition_delay_max: int = 100
    msg: str = ""

    async def run(self, c: Client) -> result.Bool | result.Error:
        if self.start_interval != 0:
            await asyncio.sleep(random.Random(self.start_interval))
        c.log(logL.INFO, f"start {self.__class__.__name__}")
        total_of_retries = count()
        res = result.Bool()
        if self.execution_datetime is None:
            self.execution_datetime = cdt.DateTime.parse("1.1.0001")
        while True:
            dt = self.execution_datetime.get_right_nearest_datetime(datetime.datetime.now())
            match dt, res.value:
                case _, True:
                    return res
                case None, False:
                    return result.Error.from_e(exc.Timeout("start time is out"))
                case None, None:
                    """start now"""
                case _:
                    delay = (dt - datetime.datetime.now()).total_seconds()
                    c.log(logL.WARN, f"wait for {delay=}")
                    await asyncio.sleep((dt - datetime.datetime.now()).total_seconds())
            res.value = False
            for n in range(self.number_of_retries):
                if next(total_of_retries) > self.total_of_retries:
                    return result.Error.from_e(exc.Timeout("out of total retries"))
                c.log(logL.INFO, min(self.repetition_delay_max, self.repetition_delay_min * (self.repetition_delay_exponent * 0.01) ** n))
                await asyncio.sleep(min(self.repetition_delay_max, self.repetition_delay_min*(self.repetition_delay_exponent * 0.01)**n))
                if res.set(await super(Scheduler, self).run(c)):
                    return res

    async def exchange(self, c: Client) -> T | result.Error:
        return await self.task.exchange(c)


class Sequence[T: Any](List[T]):
    """for exchange task sequence"""
    tasks: list[Base[T]]
    __is_exchange: bool
    msg: str
    err_ignore: bool
    __current: Optional[Base[T]]

    def __init__(self, *tasks: Base[T], msg: str = "", err_ignore: bool = True):
        self.tasks = list(tasks)
        self.__current = None
        self.__is_exchange = False
        self.msg = self.msg = self.__class__.__name__ if msg == "" else msg
        self.err_ignore = err_ignore

    @property
    def current(self) -> 'Base[T]':
        return self.__current

    def append(self, task: Base[T]):
        if not self.__is_exchange:
            self.tasks.append(task)
        else:
            raise RuntimeError(F"append to {self.__class__.__name__} not allowed, already exchange started")

    async def exchange(self, c: Client) -> result.List[T] | result.Error:
        res = result.List()
        self.__is_exchange = True
        for t in self.tasks:
            self.__current = t
            try:
                res.append(await t.exchange(c))
            except exc.ResultError as e:  # todo: make without except
                res.append(result.Error.from_e(e, msg=t.msg))
            if (
                not self.err_ignore
                and not res.is_ok()
            ):
                break
        return res


class SetLocalTime(OK):
    """without decide time transfer"""
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        clock_obj: Clock = c.objects.get_object("0.0.1.0.0.255")
        if isinstance(res := await ReadAttribute(
            ln=clock_obj.logical_name,
            index=3
        ).exchange(c), result.Error):
            return ret
        delta = datetime.timedelta(minutes=int(res.value))
        dt = cst.OctetStringDateTime(datetime.datetime.now(datetime.UTC)+delta)
        if isinstance(res := await WriteAttribute(
            ln=clock_obj.logical_name,
            index=2,
            value=dt.encoding
        ).exchange(c), result.Error):
            return res
        return result.OK


class GetFirmwareVersion(CDT):
    """get firmware version by Client.id"""
    msg: str = ""

    async def exchange(self, c: Client) -> result.SimpleOrError[cdt.CommonDataType]:
        obj = c._objects.get(c.objects.id.f_ver.par[:6])
        return await ReadObjAttr(obj, c._objects.id.f_ver.par[6]).exchange(c)


class FindFirmwareVersion(Simple[collection.ParameterValue]):
    """try find COSEM server version, return: instance(B group), CDT"""
    msg: str = ""

    async def exchange(self, c: Client) -> result.SimpleOrError[collection.ParameterValue]:
        err = result.ErrorAccumulator()
        for desc in (ut.CosemAttributeDescriptor((1, "0.0.0.2.1.255", 2)), ut.CosemAttributeDescriptor((1, "0.0.96.1.2.255", 2))):
            try:
                res = result.Simple(collection.ParameterValue(
                    par=desc.instance_id.contents + desc.attribute_id.contents,
                    value=await c.read_attr(desc)
                ))
                res.propagate_err(err)
                return res
            except exc.ResultError as e:
                err.append_err(e)
                if e.result == pdu.DataAccessResult.OBJECT_UNDEFINED:
                    """try search in old object and set to new"""
                else:
                    break
        if isinstance((res := err.result), result.Error):
            return res
        raise RuntimeError(f"empty {err}")


class FindFirmwareId(Simple[collection.ParameterValue]):
    """try find COSEM server identifier, return: FirmwareID"""
    msg: str = ""

    async def exchange(self, c: Client) -> result.SimpleOrError[collection.ParameterValue]:
        err = result.ErrorAccumulator()
        for desc in (ut.CosemAttributeDescriptor((1, "0.0.0.2.0.255", 2)), ut.CosemAttributeDescriptor((1, "0.0.96.1.1.255", 2))):
            try:
                res = result.Simple(collection.ParameterValue(
                    par=desc.instance_id.contents + desc.attribute_id.contents,
                    value=await c.read_attr(desc)
                ))
                res.propagate_err(err)
                return res
            except exc.ResultError as e:
                err.append_err(e)
                if e.result==pdu.DataAccessResult.OBJECT_UNDEFINED:
                    """try search in old object and set to new"""
                else:
                    break
        if isinstance((res := err.result), result.Error):
            return res
        raise RuntimeError(f"empty {err}")


@dataclass
class KeepAlive(OK):
    """use read LDN.ln"""
    count = count(1)
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        c.log(logL.INFO, f"keep alive: {self.msg}, count: {next(self.count)}")
        await c.read_attr(collection.AttrDesc.LDN_VALUE)
        return result.OK


class GetLDN(CDT[octet_string.LDN]):
    """:return LDN value"""
    msg: str = ""

    async def exchange(self, c: Client) -> result.SimpleOrError[octet_string.LDN]:
        data = await c.read_attr(collection.AttrDesc.LDN_VALUE)
        return result.Simple(octet_string.LDN(data))


# todo: possible implementation ConditionalTask
# def compare_ldn(man: bytes, ldn: octet_string.LDN) -> bool:
#     return man == ldn.get_manufacturer()
#
#
# check_LDN = ConditionalTask(
#     precondition_task=GetLDN,
#     comp_value=b"KPZ",
#     predicate=compare_ldn,
#     main_task=None
# )


@dataclass
class MatchLDN(OK):
    universal: bool = field(default=False)
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        if isinstance((res := await GetLDN().exchange(c)), result.Error):
            return res.with_msg("match LDN")
        if c.objects.LDN.value is None:
            c._objects.LDN.set_attr(2, res.value)
        elif c._objects.LDN.value == res.value:
            """secret matching"""
        elif self.universal:
            c.log(logL.WARN, F"connected to other server, change LDN")
            await init_type.exchange(c)  # todo: maybe set spec?
        else:
            return result.Error(exc.IDError(F"got {res.value=}, expected {c._objects.LDN.value}"))
        return result.OK


match_ldn = MatchLDN()
change_ldn = MatchLDN(universal=True)


@dataclass
class Lock:
    __lock: asyncio.Lock = field(init=False, default_factory=asyncio.Lock)
    piece: float = field(default=0.8)
    name: str = ""

    async def acquire(self, c: Client):
        keep_alive = KeepAlive(self.name)
        while True:
            try:
                await asyncio.wait_for(self.__lock.acquire(), c.com_profile.parameters.inactivity_time_out * self.piece)  # todo: make not custom <inactivity_time_out>
                return
            except TimeoutError as e:
                await keep_alive.exchange(c)

    def release(self):
        self.__lock.release()


@dataclass
class CreateType(Simple[collection.Collection]):
    col_id: collection.ID
    msg: str = "CreateType".__class__.__name__
    obj_list: Optional[cdt.Array] = None
    wait_list: asyncio.Lock = field(init=False)
    """wait <object list>"""
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    col: collection.Collection = field(init=False)

    def __post_init__(self):
        self.col = collection.Collection(id_=collection.ID(
            man=self.col_id.man,
            f_id=self.col_id.f_id,
            f_ver=self.col_id.f_ver
        ))
        """common collection"""
        self.wait_list = Lock(name="wait <object list>")

    async def exchange(self, c: Client) -> result.Simple[collection.Collection]:
        res = result.Simple(self.col)
        await self.wait_list.acquire(c)
        try:
            if self.obj_list is None:
                self.obj_list = cdt.Array(await c.read_attr(collection.AttrDesc.OBJECT_LIST), type_=structs.ObjectListElement)
            if len(self.col) == 0:
                for country_olel in filter(lambda it: ln_pattern.COUNTRY_SPECIFIC == it.logical_name, self.obj_list):
                    self.col.set_country(collection.CountrySpecificIdentifiers(country_olel.logical_name.d))
                    c.log(logL.INFO, F"set country: {self.col.country}")
                    match self.col.country:
                        case collection.CountrySpecificIdentifiers.RUSSIA:
                            country_desc = collection.AttrDesc.SPODES_VERSION
                        case _:
                            country_desc = None
                    if (
                        country_desc is not None
                        and next(filter(lambda it: country_desc.instance_id.contents == it.logical_name.contents, self.obj_list), False)
                    ):
                        self.col.set_country_ver(collection.ParameterValue(
                            par=country_desc.instance_id.contents + country_desc.attribute_id.contents,
                            value=await c.read_attr(country_desc)
                        ))
                        c.log(logL.INFO, F"set country version: {self.col.country_ver}")
                    else:
                        c.log(logL.WARN, "was not find <country specific code version> in object_list")
                    break
                else:
                    c.log(logL.WARN, "was not find <country specific code> in object_list")
                self.col.spec_map = self.col.get_spec()
                for o_l_el in self.obj_list:
                    o_l_el: structs.ObjectListElement
                    try:
                        self.col.add_if_missing(  # todo: remove add_if?
                            class_id=ut.CosemClassId(int(o_l_el.class_id)),
                            version=o_l_el.version,
                            logical_name=o_l_el.logical_name)
                    except collection.CollectionMapError as e:
                        res.append_err(e)
                self.col.add_if_missing(
                    class_id=overview.ClassID.DATA,
                    version=None,                                                                   # todo: check version else set 0
                    logical_name=cst.LogicalName.from_obis("0.0.42.0.0.255"))                       # todo: make better
            for ass in collection.get_filtered(self.col, (overview.ClassID.ASSOCIATION_LN,)):
                ass: collection.AssociationLN
                if ass.logical_name.e != 0:
                    await ReadObjAttr(ass, 3).exchange(c)  # todo: remove from self.queue
                    if ass.associated_partners_id.client_SAP == c.SAP:
                        cur_ass = ass
                        break
            else:  # use current association if no variant
                cur_ass = self.col.add_if_missing(
                    class_id=overview.ClassID.ASSOCIATION_LN,
                    version=None,
                    logical_name=cst.LogicalName.from_obis("0.0.40.0.0.255")
                )
                await ReadObjAttr(cur_ass, 3).exchange(c)
            cur_ass.set_attr(2, self.obj_list)
            if cur_ass.associated_partners_id.client_SAP != c.SAP:
                c.log(logL.ERR, F"Wrong current server SAP: {c.SAP} use {cur_ass.associated_partners_id.client_SAP}")
            self.queue.put_nowait((cur_ass, 3))  # read forcibly <associated_partners_id>: use in MapTypeCreator(by <has_sap> method)
            reduce_ln = ln_pattern.LNPattern.parse("0.0.(40,42).0.0.255")
            """reduced objects for read"""
            for o_l_el in cur_ass.object_list:  # todo: read necessary data for create_type
                if reduce_ln == o_l_el.logical_name:
                    """nothing do it"""
                else:
                    if (obj := self.col.get(o_l_el.logical_name.contents)) is None:
                        continue
                    for access in o_l_el.access_rights.attribute_access:
                        i = int(access.attribute_id)
                        if (
                            i == 1                                                                      # skip LN
                            or not access.access_mode.is_readable()                                     # skip not readable
                            or (                                                                        # skip early gotten object_list
                                cur_ass.logical_name == o_l_el.logical_name
                                and i == 2
                            ) or (
                                access.access_mode.is_writable()                                        # skip unknown type writable element
                                and not (                                                               # except for:
                                    isinstance(obj.get_attr_element(i).DATA_TYPE, ut.CHOICE)
                                    or (
                                        isinstance(obj, collection.ProfileGeneric)
                                        and i == 3)
                                )
                            ) or obj.get_attr_element(i).classifier == collection.ic.Classifier.DYNAMIC  # skip DYNAMIC
                        ):
                            continue
                        self.queue.put_nowait((obj, i))
            for d_id in collection.get_filtered(
                    objects=self.col,
                    keys=(
                            ln_pattern.DEVICE_ID,
                            ln_pattern.PROGRAM_ENTRIES)):
                self.queue.put_nowait((d_id, 2))  # todo: make second queue2 for ReadEmptyAttribute(d_id.logical_name, 2).exchange(c)
        except TimeoutError as e:
            c.log(logL.ERR, F"can't got <object list>: {e}")
        finally:
            self.wait_list.release()
        while True:
            try:
                obj, i = self.queue.get_nowait()
            except asyncio.QueueEmpty as e:
                c.log(logL.INFO, "QueueEmpty")
                try:
                    await asyncio.wait_for(self.queue.join(), c.com_profile.parameters.inactivity_time_out)  # todo: why whis timeout??  # todo: make not custom <inactivity_time_out>
                    break
                except TimeoutError as e:
                    c.log(logL.INFO, "wait returned tasks in queue")
                    continue  # wait returned tasks in queue
            try:
                await c.read_attribute(obj, i)
            except TimeoutError as e:
                c.log(logL.ERR, F"return {obj}:{i} in queue: {e}")
                await self.queue.put((obj, i))
            except exc.Timeout as e:
                c.log(logL.ERR, F"break create type {self.col} by {e}")
                await self.queue.put((obj, i))
                raise e
            except AttributeError as e:
                c.log(logL.ERR, F"skip value wrong value for {obj}:{i}: {e}")
            except Exception as e:  # todo: make better!!!
                c.log(logL.ERR, F"skip value wrong value for {obj}:{i}: {e}")
            finally:
                self.queue.task_done()
        print("stop create")
        return res


type ID_SAP = tuple[collection.ID, enums.ClientSAP]


@dataclass(frozen=True)
class IDSAP:
    id: collection.ID
    sap: enums.ClientSAP


@dataclass
class NonInit:
    msg: str

    def __getattr__(self, item):
        raise RuntimeError(self.msg)


class MapTypeCreator:
    adapter: Adapter
    lock: asyncio.Lock
    con: dict[[IDSAP], CreateType]

    def __init__(self, adapter: Adapter):
        self.adapter = adapter
        self.con = dict()
        self.lock = asyncio.Lock()

    async def get_collection(
            self,
            c: Client,
            col_id: collection.ID
    ) -> result.Simple[collection.Collection]:
        new_col: collection.Collection
        err: Errors
        id_sap = IDSAP(col_id, c.SAP)
        async with self.lock:
            if id_sap in self.con.keys():
                c.log(logL.INFO, F"{self.__class__.__name__} {col_id} already in container")
            else:
                c.log(logL.INFO, F"{self.__class__.__name__} register new collection: {col_id}")
                self.con[id_sap] = CreateType(col_id)
        res = await self.con[id_sap].exchange(c)
        async with self.lock:
            try:
                gotten, _ = self.adapter.get_collection(col_id)  # check for first update
                if gotten.has_sap(id_sap.sap):
                    """not need keep"""
                else:
                    self.adapter.set_collection(res.value)  # todo: make as ADAPTER.merge_collection(ret)
            except AdapterException as e:
                self.adapter.set_collection(res.value)
        res.value, err = res.value.copy()
        if err is not None:
            res.extend_err(err)
        return res


@dataclass
class InitType(Simple[collection.Collection]):
    adapter: Adapter
    msg: str = ""

    async def exchange(self, c: Client) -> result.SimpleOrError[collection.Collection]:
        if isinstance((res := await Sequence(
            GetLDN(),
            FindFirmwareId(),
            FindFirmwareVersion(),
            msg="get collection.ID",
            err_ignore=False
        ).exchange(c)), result.Error):
            return res.with_msg("init type")
        ldn, f_id, f_ver = res.value
        col_id = collection.ID(ldn.get_manufacturer(), f_id, f_ver)
        try:
            if (res := self.adapter.get_collection(col_id)).value.has_sap(c.SAP):
                c.log(logL.INFO, F"find collection in {self.adapter}")
            else:
                raise AdapterException(F"was found collection from adapter with absent current {c.SAP}")
        except AdapterException as e:
            c.log(logL.WARN, F"not find into adapter: {e}")
            res = await map_type_creator.get_collection(
                c=c,
                col_id=col_id
            )
        c._objects = res.value
        c._objects.LDN.set_attr(2, ldn)
        return res


init_type: InitType
"""init after get_adapter"""
map_type_creator: MapTypeCreator
"""init after get_adapter"""


def get_adapter(value: Adapter):
    global map_type_creator, init_type
    map_type_creator = MapTypeCreator(value)
    init_type = InitType(value)


get_adapter(gag)  # Dummy Adapter


@dataclass
class ReadAttribute(CDT):
    ln: collection.LNContaining
    index: int
    msg: str = ""

    async def exchange(self, c: Client) -> result.Simple[cdt.CommonDataType]:
        obj = c.objects.get_object(self.ln)
        return await ReadObjAttr(obj, self.index).exchange(c)


@dataclass
class ReadObjAttr(CDT):
    obj: collection.InterfaceClass
    index: int
    msg: str = ""

    async def exchange(self, c: Client) -> result.SimpleOrError[cdt.CommonDataType]:
        # TODO: check is_readable?
        c.get_get_request_normal(
            attr_desc=self.obj.get_attr_descriptor(
                value=self.index,
                with_selection=bool(c.negotiated_conformance.selective_access)))
        start_read_time: float = time.perf_counter()
        await c.read_data_block()
        c.last_transfer_time = datetime.timedelta(seconds=time.perf_counter()-start_read_time)
        try:
            self.obj.set_attr(self.index, c.reply.data.get_data())
            return result.Simple(self.obj.get_attr(self.index))
        except ValueError as e:
            return result.Error.from_e(e)
        except ut.UserfulTypesException as e:
            return result.Error.from_e(e)
        except exc.DLMSException as e:
            return result.Error.from_e(e)


@dataclass
class Par2Data[T: cdt.CommonDataType](CDT):
    """get CommonDataType by Parameter"""
    par: Parameter
    msg: str = "read data by Parameter"

    async def exchange(self, c: Client) -> result.SimpleOrError[T]:
        if isinstance((res := c.objects.par2obj(self.par)), result.Error):
            return res
        if isinstance((res := await ReadObjAttr(res.value, self.par.i).exchange(c)), result.Error):
            return res
        for el in self.par.elements():
            res.value = res.value[el]
        return res


class ReadSequence(Sequence):
    tasks: list[ReadAttribute]

    def __post_init__(self):
        assert all((isinstance(t, ReadAttribute) for t in self.tasks))


type AttrValueComp = Callable[[cdt.CommonDataType | None], bool]


def is_empty(value: cdt.CommonDataType | None) -> bool:
    """is empty attribute value"""
    return True if value is None else False


@dataclass
class ReadAttributeIf(Base):
    """read if func with arg as value is True"""
    ln: collection.LNContaining
    index: int
    func: AttrValueComp
    msg: str = ""

    async def exchange(self, c: Client) -> result.Simple[cdt.CommonDataType]:
        # TODO: check is_readable
        obj = c.objects.get_object(self.ln)
        if self.func(obj.get_attr(self.index)):
            return await ReadAttribute(
                ln=self.ln,
                index=self.index).exchange(c)
        else:
            return result.OK


@dataclass
class ReadEmptyAttribute(Base):
    """read if attribute is empty"""
    ln: collection.LNContaining
    index: int
    msg: str = ""

    async def exchange(self, c: Client) -> result.Simple[cdt.CommonDataType]:
        # TODO: check is_readable
        return await ReadAttributeIf(
            ln=self.ln,
            index=self.index,
            func=is_empty
        ).exchange(c)


@dataclass
class ReadWritableAttributes(Base):
    """read if attribute is writable"""
    ln: collection.LNContaining
    indexes: tuple[int, ...]
    msg: str = ""

    async def exchange(self, c: Client) -> result.List[cdt.CommonDataType]:
        # TODO: check is_readable
        res = result.List()
        indexes: list[int] = []
        ass: collection.AssociationLN = c._objects.sap2association(c.SAP)
        for i in self.indexes:
            if ass.is_writable(self.ln, i):
                indexes.append(i)
        if len(indexes) != 0:
            res.append(await ReadAttributes(
                ln=self.ln,
                indexes=tuple(indexes)
            ).exchange(c))
        else:
            res.append(result.OK)
            c.log(logL.INFO, F"skip {self.__class__.__name__} operation, all is actually")
        return res


# copy past from ReadWritableAttributes
@dataclass
class ActualizeAttributes(OK):
    """read if attribute is empty or writable"""
    ln: collection.LNContaining
    indexes: tuple[int, ...]
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        # TODO: check is_readable
        ass: collection.AssociationLN = c.objects.sap2association(c.SAP)
        obj = c.objects.get_object(self.ln)
        indexes = [
            i for i in self.indexes if (
                obj.get_attr(i) is None
                or obj.get_attr_element(i).classifier == ic.Classifier.DYNAMIC
                or ass.is_writable(self.ln, i)
            )
        ]
        if len(indexes) != 0:
            if isinstance((res := await ReadAttributes(
                ln=self.ln,
                indexes=tuple(indexes)
            ).exchange(c)), result.Error):
                return res
        return result.OK


@dataclass
class ReadAttributes(List[cdt.CommonDataType]):
    ln: collection.LNContaining
    indexes: tuple[int, ...]
    msg: str = ""

    async def exchange(self, c: Client) -> result.List[cdt.CommonDataType] | result.Error:
        res = result.List()
        obj = c.objects.get_object(self.ln)
        # TODO: check for Get-Request-With-List
        for i in self.indexes:
            res.append(await ReadObjAttr(obj, i).exchange(c))
        return res


@dataclass
class Write(OK):
    """write with ParameterData struct"""
    par_data: ParData
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        obj = c.objects.par2obj(self.par_data.par)
        if self.par_data.par.n_elements == 0:
            enc = self.par_data.data.encoding
        elif isinstance(res := await ReadObjAttr(obj, self.par_data.par.i).exchange(c), result.Error):
            return res
        else:
            data = a_data
            for el in self.par_data.par.elements():
                data = data[el]
            data.set(self.par_data.data)
            enc = data.encoding
        data = c.get_set_request_normal(
            obj=obj,
            attr_index=self.par_data.par.i,
            value=enc)
        ret = await c.read_data_block()
        return result.OK


@dataclass
class WriteParValue(OK):
    """write with ParameterValues struct"""
    par_value: ParValues[cdt.Transcript]
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        if isinstance(res1 := c.objects.par2obj(self.par_value.par), result.Error):
            return res1
        obj = res1.value
        if (a_data := res1.value.get_attr(self.par_value.par.i)) is None:
            if isinstance((res := await Par2Data(self.par_value.par).exchange(c)), result.Error):
                return res
            else:
                a_data = res.value
        s_u = c._objects.par2su(self.par_value.par)
        if isinstance(s_u, cdt.ScalUnitType):
            value: cdt.Transcript = str(float(self.par_value.data) * 10 ** -int(s_u.scaler))
        else:
            value = self.par_value.data
        if self.par_value.par.n_elements == 0:
            set_data = a_data.parse(value)
        elif isinstance((res := await Par2Data(par).exchange(c)), result.Error):
            return res
        else:
            data = a_data
            for el in self.par_value.par.elements():
                data = data[el]
            new_data = data.parse(value)  # todo: can't use with CHOICE
            data.set(new_data)
            set_data = a_data
        data = c.get_set_request_normal(
            obj=obj,
            attr_index=self.par_value.par.i,
            value=set_data.encoding)
        ret = await c.read_data_block()
        return result.OK


@dataclass
@deprecated("use <Write>")
class WriteAttribute(OK):
    ln: collection.LNContaining
    index: int
    value: bytes | str | int | list | tuple | datetime.datetime
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        obj = c._objects.get_object(self.ln)
        if isinstance(self.value, (str, int, list, tuple, datetime.datetime)):
            value2 = await c.encode(
                obj=obj,
                index=self.index,
                value=self.value)
            enc = value2.encoding
        else:
            enc = self.value
        data = c.get_set_request_normal(
            obj=obj,
            attr_index=self.index,
            value=enc)
        ret = await c.read_data_block()
        return result.OK  # todo: return Data-Access-Result


@deprecated("use Execute")
@dataclass
class ExecuteByDesc(Base):
    """execute method by method descriptor # TODO: rewrite this"""
    desc: ut.CosemMethodDescriptor
    msg: str = ""

    async def exchange(self, c: Client) -> result.Result:
        try:
            await c.execute_method(self.desc)
            return result.Simple(pdu.ActionResult.SUCCESS)
        except Exception as e:
            return result.Error.from_e(exc.DLMSException(F'Исполнение {self.desc}'))


@dataclass
class Execute(Base):
    """execute method"""
    ln: collection.LNContaining
    index: int
    value: cdt.CommonDataType = None  # todo: maybe use simple bytes
    msg: str = ""

    async def exchange(self, c: Client) -> result.SimpleOrError[pdu.ActionResult.SUCCESS]:
        obj = c._objects.get_object(self.ln)
        try:
            await c.execute_method2(obj, self.index, self.value)
            return result.Simple(value=pdu.ActionResult.SUCCESS)
        except Exception as e:
            return result.Error.from_e(exc.DLMSException(F'Исполнение {self.desc}'))


class WriteTime(Base):
    """write Clock.time depend from transfer time"""
    msg: str = ""

    async def exchange(self, c: Client):
        try:
            obj = c._objects.clock
            c.get_get_request_normal(obj.get_attr_descriptor(3))
            await c.read_data_block()
            tz = obj.get_attr_element(3).DATA_TYPE(c.reply.data.get_data())
            res = await WriteAttribute(
                ln=obj.logical_name,
                index=2,
                value=(datetime.datetime.utcnow() + datetime.timedelta(minutes=int(tz)) + c.last_transfer_time)
            ).exchange(c)
            return res
        except Exception as e:
            # logger.info(F'ERROR: write Clock: attribute 2 {e}')
            return result.Error.from_e(exc.DLMSException(F"write time: {e}"))


@dataclass
class Progress(State):
    position: int
    max: int
    message: str

    def __str__(self):
        return F"{self.message}: {self.position}/{self.max}"


@dataclass
class UpdateFirmware(Boolean):
    """only for KPZ now, return version in cdt"""
    msg: str = ""

    async def exchange(self, c: Client) -> result.Simple[bool]:
        firm_id: bytes
        boot_ver: int
        firm_id_value: cdt.CommonDataType
        boot_ver_value: cdt.CommonDataType
        res = result.Bool()
        try:
            semver = cdt.encoding2semver(res.propagate_err(await GetFirmwareVersion().exchange(c)).encoding)
            c.log(logL.INFO, F"find {semver}")
        except ValueError as e:    # todo: handle non semver type
            res.append_e(exc.DLMSException(F"can't convert version to SemVer2.0: {e}"))
            return res
        if semver < SemVer(0, 0, 25):
            res.append_e(exc.VersionError(semver))
            return res
        elif semver < SemVer(1, 4):
            firm_id_value = res.propagate_err(await ReadAttribute("00 00 80 64 00 ff", 2).exchange(c))
            if firm_id_value is None:
                res.append_e(exc.DLMSException(F"error firmware ID read"))
                return res
            boot_ver_value = firm_id_value
            await ReadObjAttr(c._objects.firmware_image_transfer, 2).exchange(c)
            if semver >= SemVer(0, 26):
                await ReadObjAttr(c._objects.boot_image_transfer, 2).exchange(c)
                if semver >= SemVer(0, 53):
                    await ReadObjAttr(c._objects.firmware_image_transfer, 6).exchange(c)
        elif semver < SemVer(1, 8):
            firm_id_value = res.propagate_err(await ReadAttribute("00 00 00 02 00 ff", 2).exchange(c))
            if firm_id_value is None:
                res.append_e(exc.DLMSException(F"error firmware ID read: {res.value}"))
                return res
            else:
                boot_ver_value = res.propagate_err(await ReadAttribute("00 00 80 64 00 ff", 2).exchange(c))
                if boot_ver_value is None:
                    res.append_e(exc.DLMSException(F"error boot Version read: {boot_ver_value}"))
                    return res
            await ReadAttributes(
                ln=c._objects.firmware_image_transfer.logical_name,
                indexes=(2, 6)
            ).exchange(c)
            await ReadAttribute(
                ln=c._objects.boot_image_transfer.logical_name,
                index=2
            ).exchange(c)
        else:
            res.append_e(exc.ITEApplication("Unknown metrology Version"))
            return res
        # decide firm_id and boot_ver
        if (match := firm_id_pat.search(bytes(firm_id_value))) is None:
            res.append_e(exc.ITEApplication(F"not find Firmware ID in {firm_id_value}"))
            return res
        else:
            firm_id = match.group("fid")
        if (match := boot_ver_pat.search(bytes(boot_ver_value))) is None:
            res.append_e(exc.ITEApplication(F"not find Firmware ID in {boot_ver_value}"))
            return res
        else:
            boot_ver = int(match.group("boot_ver"))
        # add optional object if its values absence
        c._objects.firmware_image_transfer.clear_image()  # TODO: check for missing objects !!
        suitable_firmware: SemVer = SemVer(0, 0, 1)
        suitable_boot: int = 0
        temp_key: Optional[tuple] = None
        """ key of image for update """
        if not (firms := get_firmware(manufacturer := c._objects.id.man)):
            c.log(logL.ERR, F"not find firmwares for {manufacturer=}")
            res.append_e(exc.ITEApplication(F"not find firmwares for {manufacturer=}"))
            return res
        firmwares, boots = firms
        # search firmware image
        for app_args, desc in firmwares:
            try:
                compare_ver = SemVer(*app_args)
            except ValueError as e:
                c.log(logL.ERR, F"Неизвестный тип {app_args} в *.dat файле: {e}")
                continue
            if compare_ver <= suitable_firmware:
                continue
            elif firm_id == firm_id_pat.search(bytes(desc, encoding="ascii")).group("fid"):
                suitable_firmware = compare_ver
                temp_key = (app_args, desc)
            else:
                """search more"""
        firm_image: Optional[bytes] = None
        if suitable_firmware != semver and temp_key is not None:
            firm_image: bytes = firmwares.get(temp_key)
            c.log(logL.INFO, F"choice image to update {suitable_firmware=}")
        else:
            c.log(logL.INFO, F"{semver=} is actual")
        # search boot image
        temp_key = None
        for ver, desc in boots:
            if ver <= suitable_boot:
                continue
            elif firm_id == firm_id_pat.search(bytes(desc, encoding="ascii")).group("fid"):
                suitable_boot = ver
                temp_key = (ver, desc)
            else:
                """search more"""
        c._objects.boot_image_transfer.clear_image()
        boot_image: bytes | None = None
        if suitable_boot != boot_ver and temp_key is not None:
            boot_image: bytes = boots.get(temp_key)
            c.log(logL.INFO, F"choice image to update {suitable_boot=}")
        else:
            c.log(logL.INFO, F"{boot_ver=} is actual")
        if (
            boot_image is None
            and firm_image is None
        ):
            res.value = True
            return res
        # select update algorithm by FirmwareVersion. Only for KPZ
        if semver >= SemVer(0, 0, 53):
            if (
                boot_image
                and not res.propagate_err(await TransferImage(
                    obj=c._objects.boot_image_transfer,
                    image=boot_image).exchange(c))
            ):
                await ReadAttribute(
                    ln=c._objects.firmwares_description.logical_name,
                    index=2).exchange(c)
            if firm_image:
                res.propagate_err(await TransferImage(
                    obj=c._objects.firmware_image_transfer,
                    image=firm_image).exchange(c))
            return res
        elif semver >= SemVer(0, 0, 48):
            if (
                boot_image
                and res.propagate_err(await TransferImageOld2(
                    obj=c._objects.boot_image_transfer,
                    image=boot_image).exchange(c))
            ):
                await ReadAttribute(
                    ln=c._objects.firmwares_description.logical_name,
                    index=2
                ).exchange(c)
            if firm_image:
                res.propagate_err(await TransferImageOld2(
                    obj=c._objects.firmware_image_transfer,
                    image=firm_image).exchange(c))
            return res
        elif semver >= SemVer(0, 0, 39):
            if (
                boot_image
                and res.propagate_err(await TransferImageOld(
                    obj=c._objects.boot_image_transfer,
                    image=boot_image).exchange(c))
            ):
                await ReadAttribute(
                    ln=c._objects.firmwares_description.logical_name,
                    index=2
                ).exchange(c)
            if firm_image:
                res.propagate_err(await TransferImageOld(
                    obj=c._objects.firmware_image_transfer,
                    image=firm_image).exchange(c))
            return res
        elif semver >= SemVer(0, 0, 25):
            if firm_image:
                res.propagate_err(await TransferImageOld(
                    obj=c._objects.firmware_image_transfer,
                    image=firm_image).exchange(c))
            return res
        else:
            res.append_e(ValueError(F'Невозможно обновить версию {semver}'))
            return res
        c.objects = None  # clear collection for pass LDN checked
        res.append_err(await GetFirmwareVersion().run(c))  # to get new collection
        res.value = True
        return res


@dataclass
class TransferImage(Base):
    obj: collection.ImageTransfer
    image: bytes
    block_size: int = field(default=None)
    n_t_b: int = field(default=0)
    """not transferred block"""
    reconnect: bool = False
    """reconnect after Activation"""
    n_blocks: int = field(init=False, default=None)
    msg: str = ""

    def __post_init__(self):
        self.ITI = ImageTransferInitiate((
            bytearray(hashlib.md5(self.image).digest()),  # todo: make custom this
            cdt.DoubleLongUnsigned(len(self.image))
        ))

    async def transfer_block(self, c: Client, i: int):
        """i: index for transferring block"""
        offset: int = i * self.block_size
        c.log(logL.STATE, Progress(self.n_t_b, self.n_blocks, F"{self.obj.get_meth_element(2)}"))
        await c.execute_method2(
            obj=self.obj,
            i=2,
            mip=ImageBlockTransfer((
                cdt.DoubleLongUnsigned(i),
                cdt.OctetString(bytearray(self.image[offset: offset + self.block_size]))
            ))
        )

    # todo: make (await func.exchange(c)).value right, with ERROR HANDLE
    async def exchange(self, c: Client) -> result.Simple[bool]:
        """ update image if blocks is fulls ver 3"""
        c.log(logL.INFO, F"start update by {self.obj}")
        res = result.Simple()
        self.block_size = int(res.propagate_err(await ReadObjAttr(self.obj, 2).exchange(c)))  # todo: make ReadIfEmpty
        self.n_blocks, mod = divmod(len(self.image), self.block_size)
        if mod != 0:
            self.n_blocks += 1
        get_transferred_blocks_status = ReadObjAttr(self.obj, 3)
        get_not_transferred_block = ReadObjAttr(self.obj, 4)
        get_status = ReadObjAttr(self.obj, 6)
        get_to_activate_info = ReadObjAttr(self.obj, 7)
        # TODO: need common counter for exit from infinity loop
        c.current_obj = self.obj
        previous_status: i_t_status.ImageTransferStatus | None = None
        current_status: ImageTransferStatus = res.propagate_err(await get_status.exchange(c))
        activate_info: cdt.OctetString = res.propagate_err(await get_to_activate_info.exchange(c))
        if (
            current_status in (i_t_status.TRANSFER_NOT_INITIATED, i_t_status.VERIFICATION_FAILED, i_t_status.ACTIVATION_FAILED)
            or len(activate_info) == 0
            or activate_info[0].image_to_activate_identification != self.ITI.image_identifier
        ):
            await c.execute_method2(self.obj, 1, self.ITI)
            c.log(logL.INFO, "Start initiate Image Transfer")
            current_status = res.propagate_err(await get_status.exchange(c))
        elif current_status == i_t_status.ACTIVATION_SUCCESSFUL:
            # image in outside memory and already activated early, but erased by hard programming. Need again go to activation
            current_status = i_t_status.VERIFICATION_SUCCESSFUL
        else:
            c.log(logL.INFO, "already INITIATED")
            self.n_t_b = int(res.propagate_err(await get_not_transferred_block.exchange(c)))
            if self.n_t_b > (len(self.image) / self.block_size):  # all blocks were send
                await c.execute_method2(self.obj, 3)
                c.log(logL.INFO, "Start Verify Transfer")
        while True:
            c.log(logL.STATE, F"{self.obj.get_attr_element(6)}: {current_status.get_report().msg}")
            try:
                match current_status:
                    case i_t_status.VERIFICATION_FAILED if current_status == previous_status:
                        res.value = False
                        return res
                    case i_t_status.TRANSFER_INITIATED if current_status == previous_status:
                        res.append_e(exc.DLMSException("Expected Switch to Verification Initiated status, got Initiated"))
                        # c.set_error(Application.VERIFY_ERROR, F"Expected Switch to Verification Initiated status, got Initiated")
                    case i_t_status.TRANSFER_NOT_INITIATED:
                        res.append_e(exc.DLMSException("Got Not initiated status after call Initiation"))
                        # c.set_error(Application.ACTIVATION_ERROR, 'Got Not initiated status after call Initiation')
                    case i_t_status.TRANSFER_INITIATED:
                        while self.n_t_b < self.n_blocks:
                            await self.transfer_block(c, self.n_t_b)
                            self.n_t_b += 1  # todo: maybe get from SERVER - await get_not_transferred_block.exchange(c)
                        c.log(logL.INFO, "All blocks transferred")
                        await c.execute_method2(self.obj, 3)  # Start Verify Transfer
                    case i_t_status.VERIFICATION_INITIATED:
                        c.log(logL.INFO, "read bitstring. It must grow")
                        # TODO: calculate time for waiting or read growing bitstring ?
                        if len((await get_transferred_blocks_status.exchange(c)).value) < self.n_t_b:
                            c.log(logL.INFO, F"Got blocks[{len(self.obj.image_transferred_blocks_status)}]: {self.obj.image_transferred_blocks_status}")
                        else:
                            c.log(logL.INFO, "All Bits solved")
                    case i_t_status.VERIFICATION_FAILED:
                        valid = tuple(res.propagate_err(await get_transferred_blocks_status.exchange(c)))
                        c.log(logL.INFO, F"Got blocks[{len(self.obj.image_transferred_blocks_status)}]: {self.obj.image_transferred_blocks_status}")
                        log_state = Progress(0, self.n_blocks, F"{collection.get_name(self.obj.logical_name)}")
                        c.log(logL.STATE, log_state)
                        for index in filter(lambda it: valid[it] == b'\x00', range(len(valid))):
                            await self.transfer_block(c, index)
                            if isinstance(c.state, Progress):
                                log_state.position = index
                                c.log(logL.STATE, log_state)
                        await c.execute_method2(self.obj, 3)
                        c.log(logL.INFO, "Start Verify Transfer")
                    case i_t_status.VERIFICATION_SUCCESSFUL:
                        valid = tuple(res.propagate_err(await get_transferred_blocks_status.exchange(c)))
                        self.n_t_b = int(res.propagate_err(await get_not_transferred_block.exchange(c)))
                        activate_info = res.propagate_err(await get_to_activate_info.exchange(c))
                        c.log(logL.INFO, F"md5:{self.obj.image_to_activate_info[0].image_to_activate_signature}")
                        if any(map(lambda it: it == b'\x00', valid)):
                            # c.set_error(Application.VERIFY_ERROR, 'Exist 0 blocks')
                            res.append_e(exc.DLMSException("Exist 0 blocks"))
                            await c.execute_method2(self.obj, 1, self.ITI)
                            c.log(logL.INFO, "Start initiate Image Transfer, after wrong verify. Exist 0 blocks")
                            res.value = False
                            return res
                        elif self.n_t_b < len(valid):
                            # c.set_error(Application.VERIFY_ERROR, F'Got {self.obj.image_first_not_transferred_block_number} not transferred block')
                            res.append_err(exc.DLMSException(F"Got {self.obj.image_first_not_transferred_block_number} not transferred block"))
                            await c.execute_method2(self.obj, 1, self.ITI)
                            c.log(logL.INFO, "Start initiate Image Transfer, after wrong verify. Got not transferred block")
                            res.value = False
                            return res
                        elif activate_info[0].image_to_activate_signature != activate_info[0].image_to_activate_identification:
                            message: str = (F"Signature not match to Identification: got {activate_info[0].image_to_activate_signature}, "
                                            F"expected {activate_info[0].image_to_activate_identification}")
                            res.append_err(exc.DLMSException(message))
                            # c.set_error(Application.VERIFY_ERROR, message)
                            await c.execute_method2(self.obj, 1, self.ITI)
                            c.log(logL.INFO, F"Start initiate Image Transfer, after wrong verify. {message}")
                            res.value = False
                            return res
                        else:
                            await c.execute_method2(self.obj, 4)
                            c.log(logL.INFO, "Start Activate Transfer")
                    case i_t_status.ACTIVATION_INITIATED:
                        try:
                            await c.disconnect_request()
                        except TimeoutError as e:
                            c.log(logL.ERR, F"can't use <disconnect request>: {e}")
                        res.append_err(await HardwareDisconnect("expected reboot server after upgrade").exchange(c))
                        await asyncio.sleep(5)
                        res.value = True
                        return res
                    case i_t_status.ACTIVATION_SUCCESSFUL:
                        if (await get_to_activate_info.exchange(c))[0].image_to_activate_identification == self.ITI.image_identifier:
                            c.log(logL.INFO, "already activated this image")
                            res.value = True
                            return res
                        else:
                            await c.execute_method2(self.obj, 1, self.ITI)
                            c.log(logL.INFO, "Start initiate Image Transfer")
                            # TODO: need wait clearing memory in device ~5 sec
                    case i_t_status.ACTIVATION_FAILED:
                        res.append_err(exc.DLMSException("Ошибка активации..."))
                        # c.set_error(Application.ACTIVATION_ERROR, 'Ошибка активации...')
                        res.value = False
                        return res
                    case _: raise exc.DLMSException('Unknown image transfer status')
                previous_status = current_status
            except Exception as e:
                res.append_err(e)
                res.value = False
                return res
            finally:
                c.current_obj = None
            await asyncio.sleep(1)  # TODO: tune it
            current_status = res.propagate_err(await get_status.exchange(c))


@dataclass
class TransferImageOld(TransferImage):
    async def exchange(self, c: Client) -> result.Simple[bool]:
        res = result.Simple()
        c.current_obj = self.obj
        res.propagate_err(await ReadObjAttr(self.obj, 2).exchange(c))  # todo: make ReadIfEmpty
        self.block_size = int(res.value)
        self.n_blocks, mod = divmod(len(self.image), self.block_size)
        if mod != 0:
            self.n_blocks += 1
        try:
            await c.execute_method2(self.obj, 1, self.ITI)
            c.log(logL.INFO, "Start initiate Image Transfer")
            while self.n_t_b < self.n_blocks:   # todo copypast from TransferImage
                await self.transfer_block(c, self.n_t_b)
                self.n_t_b += 1  # todo: maybe get from SERVER - await get_not_transferred_block.exchange(c)
            c.log(logL.INFO, "All blocks transferred")
            await c.execute_method2(self.obj, 4)
            c.log(logL.INFO, "Start Activate Transfer, without verification")
            res.value = True
        except Exception as e:
            c.log(logL.ERR, F"unhandled update error. {e.args[0]}")
            res.value = False
        finally:
            c.current_obj = None
            return res


@dataclass
class TransferImageOld2(TransferImage):
    async def exchange(self, c: Client) -> result.Simple[bool]:
        c.current_obj = self.obj
        res = await ReadObjAttr(self.obj, 2).exchange(c)  # todo: make ReadIfEmpty
        self.block_size = int(res.value)
        try:
            # TODO: copypast from TransferImage
            self.n_blocks, mod = divmod(len(self.image), self.block_size)
            if mod != 0:
                self.n_blocks += 1
            get_not_transferred_block = ReadObjAttr(self.obj, 4)
            get_status = ReadObjAttr(self.obj, 6)
            get_to_activate_info = ReadObjAttr(self.obj, 7)
            current_status: ImageTransferStatus = (await get_status.exchange(c)).value
            activate_info: cdt.OctetString = (await get_to_activate_info.exchange(c)).value
            if (
                current_status in (i_t_status.TRANSFER_NOT_INITIATED, i_t_status.VERIFICATION_FAILED, i_t_status.ACTIVATION_FAILED)
                or len(activate_info) == 0
                or activate_info[0].image_to_activate_identification != self.ITI.image_identifier
            ):
                await c.execute_method2(self.obj, 1, self.ITI)
                c.log(logL.INFO, "Start initiate Image Transfer")
            else:
                c.log(logL.INFO, "already INITIATED")
                self.n_t_b = int((await get_not_transferred_block.exchange(c)).value)
                if self.n_t_b == 1:  # bag in SERVER: always start from 1
                    self.n_t_b = 0
            while self.n_t_b < self.n_blocks:
                await self.transfer_block(c, self.n_t_b)
                self.n_t_b += 1  # todo: maybe get from SERVER - await get_not_transferred_block.exchange(c)
            c.log(logL.INFO, "All blocks transferred")
            await c.execute_method2(self.obj, 4)
            c.log(logL.INFO, "Start Activate Transfer. Timeout 22 second. Waiting verification")
            await HardwareDisconnect("expected reboot server after upgrade").exchange(c)
            await asyncio.sleep(22)
            await Dummy.run(c)  # reconnect after HardwareDisconnect
            res.value = True
        except Exception as e:
            res.append_e(e)
            res.value = False
        finally:
            c.current_obj = None
            return res


class TestAll(Base):
    """read all attributes with check access"""  # todo: add Write with access
    msg: str = ""

    async def exchange(self, c: Client):
        # todo: refactoring with <append_err>
        res = result.Simple()
        if await init_type.exchange(c):
            ass: collection.AssociationLN = c._objects.sap2association(c.SAP)
            for obj in tuple(c._objects):
                indexes: list[int] = [i for i, _ in obj.get_index_with_attributes()]
                attempt = count(1)
                while True:
                    c.log(logL.INFO, F"start read {obj} attr: {', '.join(map(str, indexes))}. attempt={next(attempt)}")
                    len_indexes: int = len(indexes)
                    for i in tuple(indexes):
                        is_readable = ass.is_readable(
                            ln=obj.logical_name,
                            index=i)
                        try:
                            await ReadAttribute(
                                ln=obj.logical_name,
                                index=i
                            ).exchange(c)
                            if not is_readable:
                                c.log(logL.ERR, F"{obj} with attr={i} must be unreadable")
                            indexes.remove(i)
                            c.log(logL.INFO, F"Get {obj}:{obj.get_attr_element(i)}")
                            if res.value is None:
                                c.log(logL.WARN, F"ValueError. For {obj} attr:{i} {res}")
                        except exc.ResultError as e:
                            if e.result == pdu.DataAccessResult.READ_WRITE_DENIED and not is_readable:
                                c.log(logL.INFO, F"success ReadAccess TEST: {e}")
                                indexes.remove(i)
                            else:
                                c.log(logL.ERR, F"result_error {e}")
                        except exc.ITEApplication as e:
                            c.log(logL.ERR, F"ITEApplication. For {obj} attr:{i} {e}")
                        except Exception as e:
                            c.log(logL.ERR, F"Unknown. For {obj} attr:{i} {e}")
                    if len(indexes) == 0:
                        c.log(logL.INFO, "all read success")
                        break
                    elif len(indexes) == len_indexes:
                        c.log(logL.ERR, F"can't read attr={', '.join(map(str, indexes))}")
                        break
                    else:
                        c.log(logL.WARN, F"has a errors in attr={', '.join(map(str, indexes))}. Need more attempt")
                # todo: check write problem - if send_frame clear then counter is wrong, need fix in client it
            return res


@dataclass
class ApplyTemplate(Base):
    template: collection.Template
    msg: str = ""

    async def exchange(self, c: Client) -> result.Result:
        # todo: search col
        attr: cdt.CommonDataType
        res = result.Simple()
        for col in self.template.collections:
            if col == c._objects:
                use_col = col
                break
        else:
            c.log(logL.ERR, F"not find collection for {c}")
            raise asyncio.CancelledError()
        for ln, indexes in self.template.used.items():
            if (obj := res.propagate_err(use_col.logicalName2obj(ln))) is not None:
                for i in indexes:
                    if (attr := obj.get_attr(i)) is not None:
                        res.propagate_err(await WriteAttribute(
                            ln=ln,
                            index=i,
                            value=attr.encoding
                        ).exchange(c))
                    else:
                        res.append_e(exc.EmptyObj(F"skip apply {self.template} {ln: i}: no value"))
        return res


@dataclass
class ReadTemplate(OK):
    template: collection.Template
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        # todo: copypast from <ApplyTemplate>
        attr: cdt.CommonDataType
        res = result.ErrorAccumulator()
        for col in self.template.collections:
            if col == c._objects:
                use_col = col
                break
        else:
            c.log(logL.ERR, F"not find collection for {c}")
            raise asyncio.CancelledError()
        for ln, indexes in self.template.used.items():
            try:
                obj = use_col.get_object(ln)  # todo: maybe not need
            except exc.NoObject as e:
                c.log(logL.WARN, F"skip apply {self.template}: {e}")
                continue
            res.propagate_err(
                await ReadAttributes(
                    ln=ln,
                    indexes=tuple(indexes)
                ).exchange(c))
        return res.result


@dataclass
class AccessValidate(Base[result.Ok | result.Simple[list[Parameter]]]):
    """check all access rights for current SAP"""
    with_correct: bool = False
    msg: str = ""

    # todo: make with result.Error
    async def exchange(self, c: Client) -> result.Ok | result.Simple[list[Parameter]] | result.Error:
        obj_l: ObjectListType
        el: ObjectListElement
        a_a_i: association_ln.abstract.AttributeAccessItem
        if c._objects is None:
            return result.Error.from_e(exc.DLMSException("not find Collection"))
        elif (obj_l := c._objects.sap2association(c.SAP).object_list) is None:
            return result.Error.from_e(exc.EmptyObj(F"empty object_list for {c._objects.sap2association(c.SAP)}"))
        res = result.Simple(value=[])
        for el in obj_l:
            for a_a_i in el.access_rights.attribute_access:
                if a_a_i.access_mode.is_readable():
                    i = int(a_a_i.attribute_id)
                    try:
                        res_ = await ReadAttribute(
                            ln=el.logical_name,
                            index=int(a_a_i.attribute_id)
                        ).exchange(c)
                        if a_a_i.access_mode.is_writable():
                            await WriteAttribute(
                                ln=el.logical_name,
                                index=i,
                                value=res_.value.encoding
                            ).exchange(c)
                    except exc.ResultError as e:
                        res.append_e(e)
                        res.value.append(Parameter(el.logical_name.contents).set_i(i))
                        if self.with_correct:
                            a_a_i.access_mode.set(1)  # todo: make better in future
                    except exc.Timeout as e:
                        c.log(logL.ERR, F"for {el.logical_name}: {i} - {e}")
                        await HardwareReconnect().exchange(c)
                    except Exception as e:
                        res.append_e(e)
                        res.value.append(Parameter(el.logical_name.contents).set_i(i))
        if not res.is_ok():
            return res
        return result.OK


@dataclass
class WriteParDatas(List[result.Ok]):
    """write by ParData list"""
    par_datas: list[ParData]
    msg: str = ""

    async def exchange(self, c: Client) -> result.List[result.Ok] | result.Error:
        res = result.List()
        for pardata in self.par_datas:
            res.append(await WriteAttribute(
                ln=pardata.par.ln,
                index=pardata.par.i,
                value=pardata.data.encoding
            ).exchange(c))
        return res


@dataclass
class WriteParTranscript(OK):
    """write by ParValues[Transcript]"""
    par_value: ParValues[cdt.Transcript]
    msg: str = ""

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        par, value = self.par_value
        if isinstance((res := await Par2Data(par).exchange(c)), result.Error):
            return res
        data = copy(res.value)
        if isinstance(data, cdt.Digital):
            s_u = c._objects.par2su(par)
            if isinstance(s_u, cdt.ScalUnitType):
                value = int(float(value) * 10 ** -int(s_u.scaler))
        data.set(value)
        return await WriteAttribute(
            ln=self.par_value.par.obis,
            index=self.par_value.par.i,
            value=data.encoding
        ).exchange(c)


@dataclass
class WriteParTranscripts(Base):
    """write by ParValues[Transcript] list"""
    par_values: list[ParValues[cdt.Transcript]]
    msg: str = ""

    async def exchange(self, c: Client) -> result.List:
        res = result.List()
        for par_value in self.par_values:
            WriteParTranscript(par_value)
        return res
