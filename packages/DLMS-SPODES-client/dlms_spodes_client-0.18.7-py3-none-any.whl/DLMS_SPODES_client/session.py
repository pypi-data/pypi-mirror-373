from collections import deque
from time import time
import queue
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Collection, Iterator, Self
import threading
from functools import cached_property
import asyncio
from StructResult import result
from DLMSCommunicationProfile.osi import OSI
from DLMS_SPODES import exceptions as exc
from .logger import LogLevel as logL
from .client import Client
from . import task
from .settings import settings


class UniversalLock:
    def __init__(self) -> None:
        self._thread_lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    def __enter__(self) -> "UniversalLock":
        self._thread_lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._thread_lock.release()

    async def __aenter__(self) -> Self:
        await self._async_lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._async_lock.release()


class DualStorage[T]:
    _persistent: deque[T]
    _volatile:  deque[T]
    _lock: UniversalLock

    def __init__(self, persistent_depth: int, volatile_depth: int) -> None:
        self._persistent = deque(maxlen=persistent_depth)
        self._volatile = deque(maxlen=volatile_depth)
        self._lock = UniversalLock()

    async def add(self, el: T) -> None:
        async with self._lock:
            self._persistent.append(el)
            self._volatile.append(el)

    def get_persistent(self) -> list[T]:
        with self._lock:
            return list(self._persistent)

    def get_volatile(self) -> set[T]:
        with self._lock:
            old = self._volatile
            self._volatile = deque(maxlen=self._volatile.maxlen)
        return set(old)


@dataclass(eq=False)
class Result:
    c: Client
    tsk: task.Base
    res: result.Result
    time: float

    def __hash__(self) -> int:
        return hash(self.c)


@dataclass(eq=False)
class Session[T: result.Result]:
    c: Client
    tsk: task.Base[T]
    acquire_timeout: float = 10.0
    complete: bool = field(init=False, default=False)
    res: T | result.Error = field(init=False, default=result.OK)

    async def run(self) -> None:
        try:
            await asyncio.wait_for(self.c.lock.acquire(), timeout=self.acquire_timeout)
        except TimeoutError as e:
            self.res = result.Error.from_e(e, "Client is buzy")
            await self.__complete()
            return
        try:
            self.c.log(logL.INFO, "Acquire")
            self.res = await self.tsk.run(self.c)
            await asyncio.sleep(0)  # switch to other session ?? need
        except asyncio.CancelledError:
            self.res = result.Error.from_e(exc.Abort("Task cancelled"), "in session run")
            return
        finally:
            await self.__complete()
            self.c.lock.release()
        # try media close
        try:
            await asyncio.wait_for(self.c.lock.acquire(), timeout=.1)  # keep anywhere
        except TimeoutError:
            self.c.log(logL.INFO, "opened media use in other session")
            return
        try:
            if self.c.media.is_open():
                await asyncio.wait_for(self.c.media.close(), timeout=5)  # keep anywhere
                self.c.log(logL.DEB, f"closed communication channel: {self.c.media}")
            else:
                self.c.log(logL.WARN, F"communication channel: {self.c.media} already closed")
            self.c.level = OSI.NONE
        except asyncio.TimeoutError:
            self.c.log(logL.ERR, "не удалось закрыть канал за 0.5 секунды")
        finally:
            self.c.lock.release()

    async def __complete(self) -> None:
        self.complete = True
        if result_storage is not None:
            await result_storage.add(Result(
                c=self.c,
                tsk=self.tsk,
                res=self.res,
                time=time(),
            ))

    def __hash__(self) -> int:
        return hash(self.c)


@dataclass(frozen=True)
class DistributedTask:
    """The task for distributed execution on several customers."""
    tsk: task.Base
    clients: Collection[Client]

    def __str__(self) -> str:
        return f"{self.tsk.msg}[{len(self.clients)}])"


if settings.session.result_storage.persistent_depth > 0:

    class ResultStorage(DualStorage[Result]):
        def client2res(self, c: Client) -> list[Result]:
            with self._lock:
                tmp = list(self._persistent)
            return [res for res in tmp if res.c == c]


    result_storage: ResultStorage = ResultStorage(
        persistent_depth=settings.session.result_storage.persistent_depth,
        volatile_depth=settings.session.result_storage.volatile_depth
    )
    """exchange results archive"""

else:
    result_storage: None = None


class Work:
    name: str
    __non_complete: set[Session]
    __complete: set[Session]
    time: float
    __active_tasks: set[asyncio.Task]
    __is_canceled: bool

    def __init__(self, *sessions: Session, name: str) -> None:
        self.name = name
        self.__non_complete = set(sessions)
        self.__complete = set()
        self.time = time()
        self.__active_tasks = set()
        """used for canceling the Work"""
        self.__is_canceled = False
        """cancelation flag"""

    def __str__(self) -> str:
        return f"Worker[{len(self.__non_complete)}/{len(self.all)}]: {"complete" if self.is_complete() else "in work"}[{len(self.ok_results)}/{len(self.__complete)}]"

    @classmethod
    def from_distributed_task(cls, *dis_tasks: DistributedTask, name: str) -> Self:
        sessions: list[Session] = list()
        client_tasks: dict[Client, list[task.Base]] = defaultdict(list)
        for dis_tsk in dis_tasks:
            for client in dis_tsk.clients:
                client_tasks[client].append(dis_tsk.tsk)
        for client, tasks in client_tasks.items():
            if len(tasks) == 1:
                sessions.append(Session(client, tsk=tasks[0]))
            else:
                sessions.append(Session(client, tsk=task.Sequence(*tasks)))
        return cls(*sessions, name=name)

    @cached_property
    def all(self) -> set[Session[result.Result]]:
        return self.__non_complete | self.__complete

    def __iter__(self) -> Iterator[Session[result.Result]]:
        for sess in self.__non_complete:
            yield sess

    def __getitem__(self, item) -> Session[result.Result]:
        return tuple(self.all)[item]

    @cached_property
    def clients(self) -> set[Client]:
        return {sess.c for sess in self.all}

    @property
    def ok_results(self) -> tuple[Session[result.Result], ...]:
        """without errors exchange clients"""
        return tuple(sess for sess in self.__complete if sess.res.is_ok())

    @property
    def nok_results(self) -> tuple[Session[result.ErrorPropagator], ...]:
        """Sessions with errors (excluding incomplete and canceled)"""
        return tuple(sess for sess in self.__complete if not sess.res.is_ok())

    @property
    def active_err(self) -> tuple[Session[result.Result], ...]:
        """Sessions with errors"""
        return tuple(sess for sess in self.all if not sess.res.is_ok())

    @property
    def in_progress(self) -> tuple[Session[result.Result], ...]:
        """Sessions that are still performed (current condition)"""
        return tuple(sess for sess in self.__non_complete if not sess.complete)

    def pop(self) -> set[Session[result.Result]]:
        """get and move complete session"""
        to_move = {sess for sess in self.__non_complete if sess.complete}
        self.__complete |= to_move
        self.__non_complete -= to_move
        return to_move

    def is_complete(self) -> bool:
        """check all complete sessions. call <pop> before"""
        return (
            len(self.__non_complete) == 0
            or self.__is_canceled
        )

    async def cancel(self) -> None:
        self.__is_canceled = True
        tasks_to_cancel = list(self.__active_tasks)
        self.__active_tasks.clear()
        for task in tasks_to_cancel:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

    @property
    def is_canceled(self) -> bool:
        """Checks whether the work was canceled"""
        return self.__is_canceled

    def add_active_task(self, task: asyncio.Task) -> None:
        self.__active_tasks.add(task)
        task.add_done_callback(lambda t: self.__active_tasks.discard(t))


work_storage: Optional[DualStorage[Work]] = None
if settings.session.work_storage.persistent_depth > 0:
    work_storage = DualStorage[Work](
        persistent_depth=settings.session.work_storage.persistent_depth,
        volatile_depth=settings.session.work_storage.volatile_depth
    )
    """exchange archive of Works"""


@dataclass
class Cancel:
    work: Work


@dataclass
class Worker:
    time_checking: float = 1.0
    __t: Optional[threading.Thread] = field(init=False, default=None)
    __stop: threading.Event = field(init=False, default_factory=threading.Event)
    __works: queue.Queue[Work | Cancel] = field(init=False, default_factory=queue.Queue)
    __has_work: asyncio.Event = field(init=False, default_factory=asyncio.Event)

    def start(self, abort_timeout: int = 5) -> None:
        if self.__t is not None and self.__t.is_alive():
            raise RuntimeError("Thread is already running")
        self.__t = threading.Thread(
            target=self._run_async_loop,
            args=(abort_timeout,),
            daemon=True
        )
        self.__t.start()

    def cancel(self, work: Work) -> Cancel:
        self.__works.put(cancel := Cancel(work))
        self.__has_work.set()
        return cancel

    def add_task(self, *dis_task: DistributedTask, name: str = "no_name") -> Work:
        self.__works.put(worker := Work.from_distributed_task(*dis_task, name=name))
        self.__has_work.set()
        return worker

    def add_sessions(self, *sess: Session[result.Result], name: str = "no_name") -> Work:
        self.__works.put(worker := Work(*sess, name=name))
        self.__has_work.set()
        return worker

    def stop(self) -> None:
        self.__stop.set()
        self.__has_work.set()

    def join(self, timeout: Optional[float] = None) -> None:
        if self.__t is not None:
            self.__t.join(timeout)

    def _run_async_loop(self, abort_timeout: int) -> None:
        try:
            asyncio.run(self._coro_loop(abort_timeout))
        except Exception as e:
            print(f"Transaction thread error: {e}")

    async def _coro_loop(self, abort_timeout: int) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._monitor(tg), name="main_monitor")

    async def _monitor(self, tg: asyncio.TaskGroup) -> None:
        while not self.__stop.is_set():
            try:
                await asyncio.wait_for(self.__has_work.wait(), timeout=1.0)
                while not self.__stop.is_set():
                    try:
                        work = self.__works.get_nowait()
                        if isinstance(work, Cancel):
                            await work.work.cancel()
                        else:
                            for sess in work:
                                work.add_active_task(tg.create_task(sess.run()))
                            self.__works.task_done()
                            if work_storage is not None:
                                await work_storage.add(work)
                    except queue.Empty:
                        self.__has_work.clear()
                        break
                    await asyncio.sleep(0)
            except asyncio.TimeoutError:
                continue
        if self.__stop.is_set():
            raise asyncio.CancelledError("Stop requested")


worker: Optional[Worker]
if settings.session.worker.run:
    worker = Worker(settings.session.worker.time_checking)
else:
    worker = None
