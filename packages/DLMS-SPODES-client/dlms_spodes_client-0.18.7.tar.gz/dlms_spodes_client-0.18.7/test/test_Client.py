import asyncio
import itertools
import time
import unittest
from DLMS_SPODES.pardata import ParValues, Parameter
from DLMS_SPODES.types import cdt
from DLMS_SPODES.cosem_interface_classes import collection
from DLMSAdapter.xml_ import xml50
from DLMSCommunicationProfile.HDLC.hdlc import HDLCParameters, HDLC
from StructResult import result
from src.DLMS_SPODES_client.client import Client, Network, Serial, IDFactory, RS485, BLEKPZ, logL
from src.DLMS_SPODES_client.session import DistributedTask, Session
from src.DLMS_SPODES_client import session
from src.DLMS_SPODES_client import task


task.get_adapter(adapter := xml50)


port1 = "COM6"
port2 = "COM5"
# mac = "A0:6C:65:53:7D:86"
mac = "5C:53:10:5A:E2:4B"

id_ = collection.ID(
    man=b'XXX',
    f_id=collection.ParameterValue(b'1234567', cdt.OctetString(bytearray(b'M2M-1')).encoding),
    f_ver=collection.ParameterValue(b'1234560', cdt.OctetString(bytearray(b'1.4.2')).encoding)
)

c_Serial_LOW = Client(
    # secret="30 30 30 30 30 30 30 30",    # for 101, 102, 103, 104 before ver 1.0
    id_="public",
    com_profile=HDLC(HDLCParameters(inactivity_time_out=3)),
    media=Serial(
        port=port2))
"""Serial LOW"""
c_Serial_Reader = Client(
    com_profile=HDLC(parameters=HDLCParameters(
        device_address=0,
        inactivity_time_out=3
    )),
    id_="reader",
    secret="30 30 30 30 30 30 30 30",    # for 101, 102, 103, 104 before ver 1.0
    SAP=0x20,
    media=Serial(
        port=port1))
"""Serial LOW"""
c_Serial_Reader.m_id.set(1)  # for KPZ
fobos1_Serial_Reader = Client(
    com_profile=HDLC(parameters=HDLCParameters(
        device_address=0,
        inactivity_time_out=3
    )),
    m_id=1,
    secret=b"Reader",
    SAP=0x20,
    addr_size=1,
    media=Serial(
        port="COM3"))
"""фобос1 reader"""
c_Serial_HIGH = Client(
    id_="c_Serial_HIGH",
    # secret="30 30 30 30 30 30 30 30",    # for 101, 102, 103, 104 before ver 1.0
    secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",  # for KPZ
    SAP=0x30,
    m_id=2,
    com_profile=HDLC(HDLCParameters(inactivity_time_out=30)),
    media=Serial(
        port=port1))
"""Serial HIGH"""
c_Serial_HIGH.m_id.set(2)  # for KPZ
c_Serial_HIGH2 = Client(
    id_="c_Serial_HIGH2",
    # secret="30 30 30 30 30 30 30 30",    # for 101, 102, 103, 104 before ver 1.0
    secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",  # for KPZ
    SAP=0x30,
    com_profile=HDLC(HDLCParameters(inactivity_time_out=20)),
    media=Serial(
        port=port2))
"""Serial HIGH2"""
c_Serial_HIGH2.m_id.set(2)  # for KPZ
c_Net_LOW = Client(
    media=Network(
        host="127.0.0.1",
        port='10000'),
    com_profile=HDLC(HDLCParameters(inactivity_time_out=3)),
)
"""Network LOW"""
c_BLE_LOW = Client(
    media=BLEKPZ(
        addr=mac),
    com_profile=HDLC(HDLCParameters(inactivity_time_out=3)),
)
"""BLEKPZ LOW"""
c_BLE_HIGH = Client(
    secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",  # for KPZ
    SAP=0x30,
    media=BLEKPZ(
        addr=mac),
    com_profile=HDLC(HDLCParameters(inactivity_time_out=30)),
)
c_BLE_HIGH.m_id.set(2)  # for KPZ
"""BLEKPZ High"""


class TestType(unittest.TestCase):
    def start_coro(self, sess: Session):
        async def coro(sess: Session):
            await sess.run()

        asyncio.run(coro(sess))

    def test_create_Client(self):
        id_factory = IDFactory("d")
        c1 = Client(id_=id_factory.create())
        c2 = Client(id_="d2", del_cb=id_factory.remove)
        del c2
        Client(id_=id_factory.create())
        Client()
        c3 = Client()
        c3.com_profile = HDLC()
        print(c1.id, c3.id, id_factory.value)

    def test_Session(self):
        self.start_coro(sess := Session(
            c=c_Serial_Reader,
            tsk=task.Dummy()
        ))
        print(sess)

    def test_SchedulerTask(self):
        class FalseAlways(task.Base):
            async def exchange(self, c: Client) -> result.Result:
                c.log(logL.INFO, "EXCHANGE BLOCK")
                return result.Simple(value=False)

        self.start_coro(sess := Session(
            c=c_Serial_LOW,
            tsk=task.Scheduler(
                task=FalseAlways(),
                execution_datetime=cdt.DateTime.parse("__.__.____ __:__:00"),
                number_of_retries=5,
                total_of_retries=2,
                repetition_delay_exponent=150
            )
        ))
        print(sess)

    def test_Worker(self):
        worker = session.worker
        worker.start()
        work2 = session.worker.add_sessions(
            Session(
                c=c_Serial_LOW,
                tsk=task.Dummy()),
            name="dummy"
        )
        work = session.worker.add_sessions(
            Session(
                c=c_Serial_LOW,
                tsk=task.Dummy()),
            name="dummy"
        )
        while not (
            work.is_complete()
            and work2.is_complete()
        ):
            time.sleep(1)
            work.pop()
            work2.pop()
        print(work, work2)

    def test_Work_cancel(self):
        worker = session.worker
        worker.start()
        work = session.worker.add_sessions(
            Session(
                c=c_Serial_LOW,
                tsk=task.init_type),
            name="dummy"
        )
        time.sleep(0.3)
        session.worker.cancel(work)
        while not work.is_complete():
            work.pop()
            time.sleep(0.1)
        print(work)

    def test_Manager(self):
        worker = session.worker
        worker.start()
        work1 = worker.add_task(DistributedTask(
            tsk=task.Dummy(),
            clients=[c_Serial_LOW]
        ))
        print(work1)
        time.sleep(.5)
        work2 = worker.add_task(DistributedTask(
            tsk=task.Dummy(),
            clients=[c_Serial_Reader]
        ))
        print(work2)
        while not (work1.is_complete() and work2.is_complete()):
            print(work1.pop())
            print(work2.pop())
            time.sleep(1)
        print("complete")
        print(work1)

    def ddos(self, c: Client, amount: int):
        worker = session.worker
        worker.start()
        works = list()
        for _ in range(amount):
            works.append(worker.add_sessions(Session(
                c=c,
                tsk=task.Dummy()
            )))
        while len(works):
            w = works[-1]
            w.pop()
            if w.is_complete():
                works.remove(w)
            time.sleep(.01)
            print(len(works), time.time())
        worker.stop()
        print("complete")

    def test_ddos_Serial(self):
        self.ddos(c_Serial_LOW, 50)

    def test_ddos_BLE(self):
        self.ddos(c_BLE_LOW, 2)

    def test_ClientBlocking(self):
        worker = session.worker
        worker.start()
        work = worker.add_sessions(session.Session(
            c_Serial_LOW,
            tsk=task.ClientBlocking(),
            acquire_timeout=0.01
        ))
        c = itertools.count()
        while not work.is_complete():
            time.sleep(1)
            work.pop()
            print(f"{c_Serial_LOW.lock.locked()=}")
            if next(c) == 2:
                worker.cancel(work)
        print(f"{c_Serial_LOW.lock.locked()=}")
        print("complete")

    def test_lowest_connect(self):
        ts = TransactionServer(
            DistributedTask(task.Dummy(), [c_Serial_LOW])
        )
        ts.start()
        while not ts.is_complete():
            ts.pop()
            time.sleep(1)
        print(c_Serial_LOW.objects)

    def test_reader_connect(self):
        ts = TransactionServer(
            clients=[c_Serial_Reader],
            tsk=task.Dummy()
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        print(c_Serial_LOW.objects)

    def test_fobos1_connect(self):
        ts = TransactionServer(
            clients=[fobos1_Serial_Reader],
            tsk=task.Dummy()
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        print(fobos1_Serial_Reader.objects)

    def test_lowest_network_connect(self):
        ts = TransactionServer(
            clients=[c_Net_LOW],
            tsk=task.Dummy()
        )
        c_Net_LOW.com_profile.parameters.device_address = None
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        print(c_Net_LOW.objects)

    def test_lowest_KPZBLE_connect(self):
        ts = TransactionServer(
            clients=[c_BLE_LOW],
            tsk=task.Dummy()
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        print(c_BLE_LOW.objects)

    def test_high_connect(self):
        c_Serial_HIGH.response_timeout = 10
        c_Serial_HIGH2.response_timeout = 10
        ts = TransactionServer(
            DistributedTask(task.Dummy(), [c_Serial_HIGH]),
            DistributedTask(task.ReadAttribute(ln="0.0.96.3.20.255", index=3), [c_Serial_HIGH]),
            DistributedTask(task.WriteParValue(ParValues(par=Parameter.parse("0.0.96.3.20.255:3").append(0), data="00")), [c_Serial_HIGH]),
            DistributedTask(task.ReadAttribute(ln="0.0.96.3.20.255", index=3), [c_Serial_HIGH])
        )
        ts.start()
        while not ts.is_complete():
            ts.pop()
            time.sleep(1)
        print(c_Serial_HIGH.objects)

    def test_SetLocalTime(self):
        ts = TransactionServer(
            clients=[c := Client(
                secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",
                media=Serial(
                    port=port2),
                response_timeout=3)],
            tsk=task.SetLocalTime()
        )
        ts.start()
        c.m_id.set(2)
        c.SAP.set(0x30)  # for KPZ
        while not ts.sessions.is_complete():
            time.sleep(1)
        print(c.objects)

    def test_Loop(self):
        def foo(res):
            return res == cdt.Long(4)

        ts = TransactionServer(
            clients=[
                client := Client(
                    secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",
                    addr_size=-1)
            ],
            tsk=task.Loop(
                task=task.ReadAttribute(
                    ln="0.0.1.0.0.255",
                    index=3),
                # func=lambda res: res == cdt.Long(4),
                func=foo,
                delay=2,
                attempt_amount=5
            )
        )
        client.m_id.set(2)
        client.SAP.set(0x30)  # for KPZ

        # client.device_address.set(0)
        client.media = Serial(
            port=port1
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        print("stop")

    def testsimple_read(self):
        ts = TransactionServer(
            clients=[
                client := Client(
                    addr_size=-1)
            ],
            # tsk=task.ReadAttribute(
            #     ln="0.0.1.0.0.255",
            #     index=2)
            tsk=task.ReadAttribute(
                ln="0.0.1.0.0.255",
                index=2)
        )
        # client.m_id.set(2)
        # client.SAP.set(0x30)  # for KPZ
        client.media = Serial(
            port=port1
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        print("stop")

    def test_reconnect(self):
        ts = TransactionServer(
            clients=[
                client := Client(
                    addr_size=-1)
            ],
            tsk=task.Sequence(
                task.ReadAttribute(
                    ln="0.0.1.0.0.255",
                    index=2),
                task.HardwareReconnect(delay=1),
                task.ReadAttribute(
                    ln="0.0.1.0.0.255",
                    index=2),

            )
        )
        # client.m_id.set(2)
        # client.SAP.set(0x30)  # for KPZ
        client.media = Serial(
            port=port1
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        print("stop")

    def test_InitType(self):
        client = c_Serial_Reader
        client2 = c_Serial_LOW
        ts = TransactionServer(
            clients=[
                client,
                client2
            ],
            tsk=task.init_type
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
            print(f"{ts.sessions.is_complete()=}")
        time.sleep(3)
        print(ts.sessions.ok_results)

    def test_async_network(self):
        client = Client(
            com_profile=HDLC(parameters=HDLCParameters(device_address=0)),
            secret="30 30 30 30 30 30 30 30",
            addr_size=1,
            conformance="010000000001111000011101",
            media=Serial(port="COM3")
        )
        type_ = "4d324d5f31"
        ver = "1.5.7"
        man = b"KPZ"
        # client.objects = collection.get(
        #     m=man,
        #     t=cdt.OctetString(type_),
        #     ver=AppVersion.from_str(ver))
        client.com_profile.parameters.device_address = 0
        client2 = Client(
            com_profile=HDLC(parameters=HDLCParameters(device_address=0)),
            secret="00 00 00 00 00 00 00 00",
            addr_size=1,
            conformance="010000000001111000011101",
            media=Serial(port=port1)
        )
        client2.m_id.set(1)
        client3 = Client(
            com_profile=HDLC(parameters=HDLCParameters(device_address=0)),
            secret="00 00 00 00 00 00 00 00",
            addr_size=1,
            conformance="010000000001111000011101",
            media=Network(
                host="127.0.0.1",
                port="10000")
        )
        client3.m_id.set(0)
        ts = TransactionServer(
            clients=[client3],
            # clients=[client, client2, client3],
            tsk=(s := task.Sequence(
                task.init_type,
                task.WriteAttribute("0.0.1.0.0.255", 3, "100"),
                task.ReadAttribute("0.0.1.0.0.255", 2),
                task.WriteTime()
            )))
        ts.start()
        # s.append(task.InitType())
        # print(f"{ts.is_complete()=}")
        # time.sleep(1)
        # print(f"{ts.is_complete()=}")
        # time.sleep(1)
        # print(f"{ts.is_complete()=}")
        # ts2 = TransactionServer2(
        #     clients=[client2, client3],
        #     exchanges=(tasks.ReadAttribute("0.0.42.0.0.255", 2),))
        # tse.start()
        time.sleep(.3)
        for r in ts.sessions:
            print(F'{r.complete=}')
        print("end")
        print(f"{ts.sessions.is_complete()=}")
        time.sleep(3)
        print(ts.sessions.ok_results)

    def tests_stop(self):
        client = Client(
            com_profile=HDLC(parameters=HDLCParameters(device_address=0)),
            secret="30 30 30 30 30 30 30 30",
            addr_size=1,
            conformance="010000000001111000011101",
            response_timeout=3)
        client.SAP.set(0x20)
        client.m_id.set(1)
        client.media = Serial(
            port=port1
        )
        ts = TransactionServer(
            clients=[client],
            tsk=(s := task.Sequence(
                task.init_type,
                # task.WriteAttribute("0.0.1.0.0.255", 3, "100"),
                # task.ReadAttribute("1.0.99.1.0.255", 2),
                task.ReadAttribute("0.0.99.98.2.255", 2),
                task.ReadAttribute("0.0.99.98.3.255", 2),
                # task.WriteTime()
            )))
        ts.start()

        time.sleep(.3)
        for r in ts.sessions:
            print(F'{r.complete=}')
        print(f"{ts.sessions.is_complete()=}")
        # time.sleep(4)
        # ts.abort()
        # time.sleep(1)
        # ts.abort()
        print(ts.sessions.ok_results)
        while not ts.sessions.is_complete():
            time.sleep(1)
        a = ts.sessions[0]
        print(ts)

    def test_write(self):
        client = Client(
            com_profile=HDLC(parameters=HDLCParameters(device_address=0)),
            secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",
            addr_size=1,
            conformance="010000000001111000011101",
            media=Serial(port1))
        # type_ = "4d324d5f31"
        # ver = "1.5.7"
        # man = b"KPZ"
        # client.objects = collection.get(
        #     m=man,
        #     t=cdt.OctetString(type_),
        #     ver=AppVersion.from_str(ver))
        client.SAP.set(0x30)
        client.m_id.set(2)
        ts = TransactionServer(
            clients=[client],
            tsk=(s := task.Sequence(
                task.init_type,
                task.WriteAttribute("0.0.1.0.0.255", 3, "100"),
            )))
        ts.start()

        time.sleep(.3)
        for r in ts.sessions:
            print(F'{r.complete=}')
        print(f"{ts.sessions.is_complete()=}")
        # time.sleep(4)
        # ts.abort()
        # time.sleep(1)
        # ts.abort()
        print(ts.sessions.ok_results)
        while not ts.sessions.is_complete():
            time.sleep(1)
        a = ts.sessions[0]
        print(ts)

    def test_firmware_update(self):
        ts = TransactionServer(
            clients=[c_Serial_HIGH2],
            tsk=task.UpdateFirmware())
        ts.start()

        while not ts.sessions.is_complete():
            time.sleep(1)
            print(f"{ts.sessions.is_complete()=}")
        a = ts.sessions[0]
        print(ts)

    def test_read_association(self):
        client = Client(
            secret="30 30 30 30 30 30 30 30",
            conformance="010000000001111000011101",
            media=Serial(
                port=port1))
        # client.SAP.set(0x30)  # for KPZ
        # client.m_id.set(2)  # for KPZ
        client.m_id.set(1)  # for 101, 102, 103, 104 before ver 1.0
        ts = TransactionServer(
            clients=[client],
            tsk=task.ReadAttribute(
                ln='0.0.40.0.1.255',
                index=2
            ))
        ts.start()

        while not ts.sessions.is_complete():
            time.sleep(1)
        print(f"{ts.sessions.is_complete()=}")

    def test_CreateCollection(self):
        client = Client(
            com_profile=HDLC(parameters=HDLCParameters(device_address=0)),
            SAP=0x30,
            secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",
            addr_size=1,
            media=Serial(
              port="COM3")
        )
        client.m_id.set(2)
        ts = TransactionServer(
            clients=[client],
            tsk=task.TestAll()
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
            print(f"{ts.sessions.is_complete()=}")
        a = ts.sessions[0]
        print(ts)

    def test_universal(self):
        client = Client(
            com_profile=HDLC(parameters=HDLCParameters(device_address=0)),
            universal=True,
            SAP=0x30,
            secret="30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30",
            addr_size=1,
            m_id=2,
            media=Serial(
              port="COM3")
        )
        client.objects = collection.Collection()
        client.objects.LDN.set_attr(2, b'\x09\x0fXXX01234567890123')
        print(client.objects, client.objects.LDN.value)
        ts = TransactionServer(
            clients=[client],
            tsk=task.Dummy()
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
            print(f"{ts.sessions.is_complete()=}")
        a = ts.sessions[0]
        print(ts)

    def test_IDSAP(self):
        value = task.IDSAP(
            id=id_,
            sap=task.enums.ClientSAP(0x10)
        )
        value2 = task.IDSAP(
            id=id_,
            sap=task.enums.ClientSAP(0x30)
        )
        print(hash(value), hash(value2))

    def test_KPZ_old(self):
        c = Client(
            com_profile=HDLC(),
            SAP=0x00,
            secret="30 30 30 30 30 30 30 30",    # for 101, 102, 103, 104 before ver 1.0
            id_="public",
            response_timeout=3,
            media=Serial(
                port=port1))
        """Serial LOW"""
        c.m_id.set(1)
        ts = TransactionServer(
            clients=[c],
            tsk=task.Dummy()
        )
        ts.start()
        while not ts.sessions.is_complete():
            time.sleep(1)
        self.assertIsNotNone(c.objects, "empty collection")
        print(c.objects)
