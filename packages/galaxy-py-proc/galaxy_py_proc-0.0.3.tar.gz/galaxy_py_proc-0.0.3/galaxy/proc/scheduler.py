#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABC,                                            \
                abstractmethod
from transitions.core import Machine,                           \
                             EventData
from transitions.extensions.asyncio import AsyncMachine
from typing import Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import BaseJobStore
from apscheduler.jobstores.memory import MemoryJobStore
#from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
#from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.base import BaseExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ThreadPoolExecutor,      \
                                       ProcessPoolExecutor
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import AndTrigger,          \
                                           OrTrigger

from galaxy.utils.base import Component,                        \
                              Configurable,                     \
                              TimestampedState,                 \
                              TimestampedAsyncState
from galaxy.service.service import LogService,                  \
                                   LogAsyncService
from galaxy.proc import constant
from galaxy.kernel.loop import AsyncioLoop


class Scheduler(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: SchedulerStateMachine = SchedulerStateMachine(self)
        self.enabled: bool = False
        self.log: LogService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def restart(self) -> None:
        self.stop()
        self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Scheduler(id='{}')>".format(self.id)


class SchedulerState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerState, self).__init__(name=name)
        self.scheduler = scheduler


class SchedulerNewState(SchedulerState):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerNewState, self).__init__(constant.STATE_NEW, scheduler)


class SchedulerInitiatedState(SchedulerState):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerInitiatedState, self).__init__(constant.STATE_INIT, scheduler)

    def enter(self, event_data: EventData) -> None:
        self.scheduler.log.logger.debug("The scheduler {} is loading".format(self.scheduler))
        self.scheduler._load()
        self.scheduler.log.logger.debug("The scheduler {} is loaded".format(self.scheduler))
        super(SchedulerInitiatedState, self).enter(event_data)


class SchedulerRunningState(SchedulerState):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerRunningState, self).__init__(constant.STATE_RUNNING, scheduler)

    def enter(self, event_data: EventData) -> None:
        self.scheduler.log.logger.debug("The scheduler {} is starting".format(self.scheduler))
        self.scheduler._start()
        self.scheduler.log.logger.debug("The scheduler {} is running".format(self.scheduler))
        super(SchedulerRunningState, self).enter(event_data)


class SchedulerStoppedState(SchedulerState):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerStoppedState, self).__init__(constant.STATE_STOPPED, scheduler)

    def enter(self, event_data: EventData) -> None:
        self.scheduler.log.logger.debug("The scheduler {} is stopping".format(self.scheduler))
        self.scheduler._stop()
        self.scheduler.log.logger.debug("The scheduler {} is stopped".format(self.scheduler))
        super(SchedulerStoppedState, self).enter(event_data)


class SchedulerPausedState(SchedulerState):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerPausedState, self).__init__(constant.STATE_PAUSED, scheduler)

    async def enter(self, event_data: EventData) -> None:
        self.scheduler.log.logger.debug("The scheduler {} is pausing".format(self.scheduler))
        self.scheduler._pause()
        self.scheduler.log.logger.debug("The scheduler {} is paused".format(self.scheduler))
        super(SchedulerPausedState, self).enter(event_data)


class SchedulerShutdownState(SchedulerState):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerShutdownState, self).__init__(constant.STATE_SHUTDOWN, scheduler)


class SchedulerTimeoutState(SchedulerState):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        super(SchedulerTimeoutState, self).__init__(constant.STATE_TIMEOUT, scheduler)


class SchedulerStateMachine(object):
    """
    classdocs
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """
        Constructor
        """
        self._scheduler: Scheduler = scheduler
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, SchedulerState] = {
                                                  constant.STATE_NEW: SchedulerNewState(self._scheduler),
                                                  constant.STATE_INIT: SchedulerInitiatedState(self._scheduler),
                                                  constant.STATE_RUNNING: SchedulerRunningState(self._scheduler),
                                                  constant.STATE_STOPPED: SchedulerStoppedState(self._scheduler),
                                                  constant.STATE_PAUSED: SchedulerPausedState(self._scheduler),
                                                  constant.STATE_SHUTDOWN: SchedulerShutdownState(self._scheduler),
                                                  constant.STATE_TIMEOUT: SchedulerTimeoutState(self._scheduler)
                                                 }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: Machine = Machine(model=self._scheduler,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncScheduler(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: SchedulerAsyncStateMachine = SchedulerAsyncStateMachine(self)
        self.enabled: bool = False
        self.log: LogAsyncService | None = None
        self.loop: AsyncioLoop | None = None

    async def _load(self) -> None:
        super(AsyncScheduler, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncScheduler(id='{}')>".format(self.id)


class SchedulerAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerAsyncState, self).__init__(name=name)
        self.scheduler = scheduler


class SchedulerNewAsyncState(SchedulerAsyncState):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerNewAsyncState, self).__init__(constant.STATE_NEW, scheduler)


class SchedulerInitiatedAsyncState(SchedulerAsyncState):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerInitiatedAsyncState, self).__init__(constant.STATE_INIT, scheduler)

    async def enter(self, event_data: EventData) -> None:
        self.scheduler.log.logger.debug("The scheduler {} is loading".format(self.scheduler))
        await self.scheduler._load()
        self.scheduler.log.logger.debug("The scheduler {} is loaded".format(self.scheduler))
        await super(SchedulerInitiatedAsyncState, self).enter(event_data)


class SchedulerRunningAsyncState(SchedulerAsyncState):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerRunningAsyncState, self).__init__(constant.STATE_RUNNING, scheduler)

    async def enter(self, event_data):
        self.scheduler.log.logger.debug("The scheduler {} is starting".format(self.scheduler))
        await self.scheduler._start()
        self.scheduler.log.logger.debug("The scheduler {} is running".format(self.scheduler))
        await super(SchedulerRunningAsyncState, self).enter(event_data)


class SchedulerStoppedAsyncState(SchedulerAsyncState):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerStoppedAsyncState, self).__init__(constant.STATE_STOPPED, scheduler)

    async def enter(self, event_data: EventData) -> None:
        self.scheduler.log.logger.debug("The scheduler {} is stopping".format(self.scheduler))
        await self.scheduler._stop()
        self.scheduler.log.logger.debug("The scheduler {} is stopped".format(self.scheduler))
        await super(SchedulerStoppedAsyncState, self).enter(event_data)


class SchedulerPausedAsyncState(SchedulerAsyncState):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerPausedAsyncState, self).__init__(constant.STATE_PAUSED, scheduler)

    async def enter(self, event_data: EventData) -> None:
        self.scheduler.log.logger.debug("The scheduler {} is pausing".format(self.scheduler))
        await self.scheduler._pause()
        self.scheduler.log.logger.debug("The scheduler {} is paused".format(self.scheduler))
        await super(SchedulerPausedAsyncState, self).enter(event_data)


class SchedulerShutdownAsyncState(SchedulerAsyncState):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, scheduler)


class SchedulerTimeoutAsyncState(SchedulerAsyncState):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        super(SchedulerTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, scheduler)


class SchedulerAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, scheduler: AsyncScheduler) -> None:
        """
        Constructor
        """
        self._scheduler: AsyncScheduler = scheduler
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, SchedulerAsyncState] = {
                                                       constant.STATE_NEW: SchedulerNewAsyncState(self._scheduler),
                                                       constant.STATE_INIT: SchedulerInitiatedAsyncState(self._scheduler),
                                                       constant.STATE_RUNNING: SchedulerRunningAsyncState(self._scheduler),
                                                       constant.STATE_STOPPED: SchedulerStoppedAsyncState(self._scheduler),
                                                       constant.STATE_SHUTDOWN: SchedulerShutdownAsyncState(self._scheduler),
                                                       constant.STATE_TIMEOUT: SchedulerTimeoutAsyncState(self._scheduler),
                                                       constant.STATE_PAUSED: SchedulerPausedAsyncState(self._scheduler)
                                                      }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING,
                                                    "conditions": "is_enabled"
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "pause",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_PAUSED
                                                   },
                                                   {
                                                    "trigger": "resume",
                                                    "source": constant.STATE_PAUSED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: AsyncMachine = AsyncMachine(model=self._scheduler,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class JobStoreFactory(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)

    def _load(self) -> None:
        super(JobStoreFactory, self)._load()

    @abstractmethod
    def create(self) -> BaseJobStore:
        raise NotImplementedError("Should implement create()")


class MemoryjobStoreFactory(JobStoreFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MemoryjobStoreFactory, self).__init__()

    def create(self) -> MemoryJobStore:
        store = MemoryJobStore()
        return store


# class SQLAlchemyjobStoreFactory(JobStoreFactory):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(SQLAlchemyjobStoreFactory, self).__init__()
#
#     def create_jobstore(self) -> SQLAlchemyJobStore:
#         store = SQLAlchemyJobStore(self.conf["url"])
#         return store


# class MongoDBjobStoreFactory(JobStoreFactory):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(MongoDBjobStoreFactory, self).__init__()
#
#     def create_jobstore(self) -> MongoDBJobStore:
#         store = MongoDBJobStore()
#         return store


class ExecutorFactory(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)

    def _load(self) -> None:
        super(ExecutorFactory, self)._load()

    @abstractmethod
    def create(self) -> BaseExecutor:
        raise NotImplementedError("Should implement create()")


class AsyncExecutorFactory(ExecutorFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncExecutorFactory, self).__init__()

    def create(self) -> AsyncIOExecutor:
        executor = AsyncIOExecutor()
        return executor


class ProcessPoolExecutorFactory(ExecutorFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ProcessPoolExecutorFactory, self).__init__()

    def create(self) -> ProcessPoolExecutor:
        executor = ProcessPoolExecutor(self.conf["max_workers"])
        return executor


class ThreadPoolExecutorFactory(ExecutorFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ThreadPoolExecutorFactory, self).__init__()

    def create_executor(self) -> ThreadPoolExecutor:
        executor = ThreadPoolExecutor(self.conf["max_workers"])
        return executor


class SchedulerFactory(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)

    def _load(self) -> None:
        super(SchedulerFactory, self)._load()

    @abstractmethod
    def create(self) -> Any:
        raise NotImplementedError("Should implement create()")


class APSchedulerAsyncIOSchedulerFactory(SchedulerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(APSchedulerAsyncIOSchedulerFactory, self).__init__()
        self.loop: AsyncioLoop | None = None
        self.jobstore_factories: dict[str, JobStoreFactory] | None = None
        self.executor_factories: dict[str, ExecutorFactory] | None = None

    def _load(self) -> None:
        super(APSchedulerAsyncIOSchedulerFactory, self)._load()
        [jobstore_fact._load() for jobstore_fact in self.jobstore_factories.values()]
        [executor_fact._load() for executor_fact in self.executor_factories.values()]

    def create(self) -> AsyncIOScheduler:
        scheduler = AsyncIOScheduler(event_loop=self.loop.loop)
        jobstores = {name: fact.create() for name, fact in self.jobstore_factories.items()}
        executors = {name: fact.create() for name, fact in self.executor_factories.items()}
        scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=self.conf["job_defaults"], timezone=self.conf["timezone"])
        return scheduler


class TriggerFactory(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)

    def _load(self) -> None:
        super(TriggerFactory, self)._load()

    @abstractmethod
    def create(self) -> BaseTrigger:
        raise NotImplementedError("Should implement create()")


class IntervalTriggerFactory(TriggerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(IntervalTriggerFactory, self).__init__()

    def create(self) -> IntervalTrigger:
        kwargs = {}
        if "years" in self.conf:
            kwargs["years"] = self.conf["years"]
        if "months" in self.conf:
            kwargs["months"] = self.conf["months"]
        if "weeks" in self.conf:
            kwargs["weeks"] = self.conf["weeks"]
        if "hours" in self.conf:
            kwargs["hours"] = self.conf["hours"]
        if "minutes" in self.conf:
            kwargs["minutes"] = self.conf["minutes"]
        if "seconds" in self.conf:
            kwargs["seconds"] = self.conf["seconds"]
        if "microseconds" in self.conf:
            kwargs["microseconds"] = self.conf["microseconds"]
        if "start_time" in self.conf:
            kwargs["start_time"] = self.conf["start_time"]
        if "end_time" in self.conf:
            kwargs["end_time"] = self.conf["end_time"]
        trigger = IntervalTrigger(**kwargs)
        return trigger


class DateTriggerFactory(TriggerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DateTriggerFactory, self).__init__()

    def create(self) -> DateTrigger:
        kwargs = {}
        if "date" in self.conf:
            kwargs["run_time"] = self.conf["date"]
        trigger = DateTrigger(**kwargs)
        return trigger


class CronTriggerFactory(TriggerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CronTriggerFactory, self).__init__()

    def create(self) -> CronTrigger:
        kwargs = {}
        if "year" in self.conf:
            kwargs["year"] = self.conf["year"]
        if "month" in self.conf:
            kwargs["month"] = self.conf["month"]
        if "day" in self.conf:
            kwargs["day"] = self.conf["day"]
        if "week" in self.conf:
            kwargs["week"] = self.conf["week"]
        if "day_of_week" in self.conf:
            kwargs["day_of_week"] = self.conf["day_of_week"]
        if "hour" in self.conf:
            kwargs["hour"] = self.conf["hour"]
        if "minute" in self.conf:
            kwargs["minute"] = self.conf["minute"]
        if "second" in self.conf:
            kwargs["second"] = self.conf["second"]
        if "start_time" in self.conf:
            kwargs["start_time"] = self.conf["start_time"]
        if "end_time" in self.conf:
            kwargs["end_time"] = self.conf["end_time"]
        if "timezone" in self.conf:
            kwargs["timezone"] = self.conf["timezone"]
        trigger = CronTrigger(**kwargs)
        return trigger


class AndTriggerFactory(TriggerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AndTriggerFactory, self).__init__()
        self.trigger_facts: list[TriggerFactory] | None = None

    def create(self) -> AndTrigger:
        kwargs = {}
        if "threshold" in self.conf:
            kwargs["threshold"] = self.conf["threshold"]
        if "max_iterations" in self.conf:
            kwargs["max_iterations"] = self.conf["max_iterations"]
        kwargs["triggers"] = [trigger_fact.create() for trigger_fact in self.trigger_facts]
        trigger = AndTrigger(**kwargs)
        return trigger


class OrTriggerFactory(TriggerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(OrTriggerFactory, self).__init__()

    def create(self) -> OrTrigger:
        kwargs = {}
        if "threshold" in self.conf:
            kwargs["threshold"] = self.conf["threshold"]
        if "max_iterations" in self.conf:
            kwargs["max_iterations"] = self.conf["max_iterations"]
        kwargs["triggers"] = [trigger_fact.create() for trigger_fact in self.trigger_facts]
        trigger = OrTrigger(**kwargs)
        return trigger


class APSchedulerAsyncIOScheduler(AsyncScheduler):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(APSchedulerAsyncIOScheduler, self).__init__()
        self.scheduler_fact: APSchedulerAsyncIOSchedulerFactory | None = None
        self.scheduler: AsyncIOScheduler | None = None

    async def _load(self) -> None:
        await super(APSchedulerAsyncIOScheduler, self)._load()
        self.scheduler_fact._load()
        self.scheduler = self.scheduler_fact.create()

    async def _start(self) -> None:
        self.scheduler.start()

    async def _stop(self) -> None:
        self.scheduler.shutdown()

    def __repr__(self) -> str:
        return "<APSchedulerAsyncIOScheduler(id='{}')>".format(self.id)
