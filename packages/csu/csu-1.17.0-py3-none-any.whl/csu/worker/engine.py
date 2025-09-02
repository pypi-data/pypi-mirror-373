import asyncio
import traceback
from abc import ABC
from abc import abstractmethod
from asyncio import CancelledError
from asyncio import Future
from asyncio import Queue
from asyncio import Semaphore
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from datetime import time
from datetime import timedelta
from enum import Flag
from enum import auto
from functools import partial
from random import randint
from typing import Protocol

from datetimerange import DateTimeRange

from ..exceptions import InternalServiceError
from ..timezones import naivenow
from . import logger
from .enums import WorkerState
from .job import Job


class TaskProtocol(Protocol):
    job_kwargs: dict

    async def done_watchdog(self, job: Job):
        pass


class ResultTypeProtocol(Protocol):
    PENDING: object
    SUCCESS: object
    ABSENT: object
    ERROR: object


class AbstractWorker(ABC):
    state: WorkerState = WorkerState.UNKNOWN
    runner: asyncio.Task

    def __str__(self):
        return f"{type(self).__name__}({self.state.name})"

    def __repr__(self):
        return f"{type(self).__name__}({id(self)}, state={self.state.name})"

    def report(self, inspect: defaultdict[str, int]):
        inspect[self.state.name] += 1

    def start(self):
        self.runner = asyncio.create_task(self.run())
        # noinspection PyTypeChecker
        self.runner.add_done_callback(self.on_exit)
        logger.info("%s started.", self)

    def on_exit(self, future: Future):
        try:
            result = future.result()
        except CancelledError as exc:
            logger.info("%s.on_exit(%s) %r", self, future, exc)
            self.state = WorkerState.CANCELED
        except Exception as exc:
            logger.critical("%s.on_exit(%s) unexpected failure: %r", self, future, exc)
            self.state = WorkerState.FAILED
        else:
            logger.info("%s.on_exit(%s) exit with result: %r", self, future, result)
            self.state = WorkerState.EXITED

    @abstractmethod
    async def run(self):
        pass

    async def before(self):  # noqa: B027
        """
        Called before a unit of work is performed.
        """

    async def after(self, *, idle):  # noqa: B027
        """
        Called before after a unit of work is performed.
        :param idle: True if run would have a spin-loop condition.
        """


class SleepingTimeRangeMixin:
    state: WorkerState
    sleeping_timerange: tuple[time, time]

    async def before(self):
        # noinspection PyUnresolvedReferences
        await super().before()

        now = naivenow()
        today = now.date()
        start, end = self.sleeping_timerange
        sleep_range = DateTimeRange(
            datetime.combine(today, start),
            datetime.combine(today if start <= end else today + timedelta(days=1), end),
        )
        if now in sleep_range:
            self.state = WorkerState.SLEEPING
            delta = (sleep_range.end_datetime - now).total_seconds()
            logger.info("%s.before() sleeping until %s (%s seconds)", self, sleep_range.end_datetime, delta)
            await asyncio.sleep(delta)


class SleepingCooldown(Flag):
    IDLE = auto()
    BUSY = auto()


class SleepingCooldownMixin:
    state: WorkerState
    cooldown_min_seconds: int
    cooldown_max_seconds: int
    cooldown_on: SleepingCooldown

    async def after(self, *, idle):
        # noinspection PyUnresolvedReferences
        await super().after(idle=idle)
        if self.cooldown_on & (SleepingCooldown.IDLE if idle else SleepingCooldown.BUSY):
            self.state = WorkerState.COOLDOWN
            sleep_seconds = randint(self.cooldown_min_seconds, self.cooldown_max_seconds)  # noqa: S311
            logger.info("%s.after() having a cooldown of %s seconds.", self, sleep_seconds)
            await asyncio.sleep(sleep_seconds)


@dataclass(repr=False)
class AbstractProducer(AbstractWorker):
    state = WorkerState.UNKNOWN
    engine: "AbstractEngine"

    @property
    @abstractmethod
    def job_class(self) -> type[Job]:
        pass

    @abstractmethod
    async def fetch_task(self) -> TaskProtocol | None:
        """
        Should raise error if there would be a spin-loop condition.
        """

    def __str__(self):
        return f"{type(self).__name__}()"

    async def run(self):
        task: TaskProtocol | None
        logger.info("%s.run() started.", self)
        while True:
            await self.before()
            idle = False
            try:
                self.state = WorkerState.WORKING
                task = await self.fetch_task()
            except InternalServiceError as exc:
                logger.error("%s.run() failed %r", self, exc)
                task = None
                idle = True
            except Exception as exc:
                logger.exception("%s.run() failed %r", self, exc)
                task = None
                idle = True
            await self.after(idle=idle)
            if task:
                # noinspection PyArgumentList
                await self.engine.push(job := self.job_class(**task.job_kwargs))
                logger.info("%s.run() awaiting %s.done of %s.", self, job, task)
                await task.done_watchdog(job)


@dataclass(repr=False)
class AbstractConsumer(AbstractWorker):
    engine: "AbstractEngine"

    @property
    @abstractmethod
    def result_type_enum(self) -> type[ResultTypeProtocol]:
        pass

    @abstractmethod
    async def save_result(self, job: Job, /, **kwargs):
        pass

    def __str__(self):
        return f"{type(self).__name__}({id(self)})"

    async def run(self):
        while True:
            await self.before()
            self.state = WorkerState.READY
            job: Job = await self.engine.pull()
            job.started.set_result(True)
            logger.info("%s.run() working on: %s", self, job)
            self.state = WorkerState.WORKING
            logger.info("%s.run() - performing...", self)
            try:
                fields = await self.perform_work(job)
            except Exception as exc:
                logger.error("%s.perform_work(%s) failed: %r", self, job, exc)
                result = await self.save_result(
                    job,
                    result_type=self.result_type_enum.ERROR,
                    result_details=f"{exc!r}\n{traceback.format_exc()}",
                )
                idle = True
            else:
                result = await self.save_result(
                    job,
                    result_type=self.result_type_enum.SUCCESS if fields else self.result_type_enum.ABSENT,
                    result_details=None if fields else repr(fields),
                    **fields or {},
                )
                idle = False
            job.done.set_result(result)
            self.engine.mark_done()
            await self.after(idle=idle)

    @abstractmethod
    async def perform_work(self, job: Job) -> dict:
        pass


@dataclass
class AbstractEngine(ABC):
    workers: list[AbstractConsumer | AbstractProducer]
    queue: Queue

    def __init__(self):
        self.workers = []
        self.queue = Queue()
        self.semaphore = Semaphore(value=0)

    def __str__(self):
        return f"{type(self).__name__}({len(self.workers)}w/{self.queue.qsize()}q)"

    async def push(self, job: Job) -> None:
        logger.info("%s.push(%s)", self, job)
        await self.semaphore.acquire()
        await self.queue.put(job)

    def push_nowait(self, job: Job) -> None:
        logger.info("%s.push_nowait(%s)", self, job)
        self.queue.put_nowait(job)

    async def pull(self) -> Job:
        self.semaphore.release()
        return await self.queue.get()

    def mark_done(self):
        self.queue.task_done()

    @abstractmethod
    async def start(self):
        pass

    async def stop(self):
        logger.info("%s.stop()", self)
        logger.info("%s stats: %s", self, self.inspect())
        for i, worker in enumerate(self.workers, 1):
            logger.info("%s worker %s: %r", self, i, worker)

        tasks = [worker.runner for worker in self.workers]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.workers.clear()
        logger.info("%s shutdown complete.", self)

    def report(self, inspect: defaultdict[str, int]):
        inspect["QSIZE"] = self.queue.qsize()

    def inspect(self) -> dict[str, dict[str, int]]:
        result = defaultdict(partial(defaultdict, int))
        for worker in self.workers:
            worker.report(result[type(worker).__name__])
        self.report(result[type(self).__name__])
        return {name: {counter: value for counter, value in sorted(counters.items())} for name, counters in result.items()}  # noqa: C416
