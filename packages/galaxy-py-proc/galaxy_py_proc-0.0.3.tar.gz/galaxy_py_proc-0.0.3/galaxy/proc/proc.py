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

import uuid
import sys
import traceback
from abc import ABC,                                            \
                abstractmethod
from transitions.core import Machine,                           \
                             EventData
import asyncio
from transitions.extensions.asyncio import AsyncMachine
from reactivex import of,                                       \
                      create,                                   \
                      from_future,                              \
                      timer,                                    \
                      interval
import functools
from reactivex.scheduler.eventloop import AsyncIOScheduler
from reactivex import operators as ops
from reactivex.disposable import Disposable
from reactivex import Observable
from asyncio import ensure_future
from typing import TypeVar
import aiofiles
from datetime import datetime

from galaxy.utils.type import CompId
from galaxy.utils.base import Component,                        \
                              Configurable,                     \
                              TimestampedState,                 \
                              TimestampedAsyncState
from galaxy.service.service import Manager,                     \
                                   AsyncManager,                \
                                   ServiceManager,              \
                                   ServiceAsyncManager,         \
                                   LogService,                  \
                                   LogAsyncService
from galaxy.proc import constant
from galaxy.proc.scheduler import Scheduler,                    \
                                  AsyncScheduler,               \
                                  TriggerFactory
from galaxy.kernel.loop import AsyncioLoop
from galaxy.command.router import Router,                       \
                                  AsyncRouter
from galaxy.command.interpreter import Interpreter,             \
                                       CmdInterpreter
from galaxy.net.zmq.zmq import ZmqAsyncServer
from galaxy.data.serial import Serializer,                      \
                               ProtobufSerializer
from galaxy.net.compression import Compressor
from galaxy.data.protobuf import net_pb2,                       \
                                 cmd_pb2
from galaxy.data.model.factory import MessageFactory,           \
                                      MessageProtobufFactory
from galaxy.perfo.decorator import timed,                       \
                                   async_timed

_T = TypeVar("_T")


class ProcessManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ProcessManager, self).__init__()
        self.procs: dict[CompId, Process] = {}
        self.scheduler: Scheduler = None

    def load_all(self) -> None:
        if self.scheduler is not None:
            self.scheduler.load()
        [proc.load() for proc in self.procs.values()]

    def _start(self) -> None:
        [proc.start() for proc in self.procs.values()]
        if self.scheduler is not None:
            self.scheduler.start()

    def _stop(self) -> None:
        [proc.stop() for proc in self.procs.values()]
        if self.scheduler is not None:
            self.scheduler.shutdown()

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<ProcessManager(id='{}')>".format(self.id)


class ProcessAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ProcessAsyncManager, self).__init__()
        self.procs: dict[CompId, AsyncProcess] = {}
        self.scheduler: AsyncScheduler = None

    async def load_all(self) -> None:
        if self.scheduler is not None:
            await self.scheduler.load()
        await asyncio.gather(*[proc.load() for proc in self.procs.values()])

    async def _start(self) -> None:
        await asyncio.gather(*[proc.start() for proc in self.procs.values()])
        if self.scheduler is not None:
            await self.scheduler.start()

    async def _stop(self) -> None:
        await asyncio.gather(*[proc.stop() for proc in self.procs.values()])
        if self.scheduler is not None:
            await self.scheduler.stop()

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<ProcessAsyncManager(id='{}')>".format(self.id)


class Process(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ProcessStateMachine = ProcessStateMachine(self)
        self.enabled: bool = False
        self.log: LogService | None = None
        self.service: ServiceManager | None = None
        self.scheduler: Scheduler | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    def _pause(self) -> None:
        raise NotImplementedError("Should implement _pause()")

    @abstractmethod
    def _resume(self) -> None:
        raise NotImplementedError("Should implement _resume()")

    def restart(self) -> None:
        self.stop()
        self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Process(id='{}')>".format(self.id)


class ProcessState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessState, self).__init__(name=name)
        self.proc = proc


class ProcessNewState(ProcessState):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessNewState, self).__init__(constant.STATE_NEW, proc)


class ProcessInitiatedState(ProcessState):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessInitiatedState, self).__init__(constant.STATE_INIT, proc)

    def enter(self, event_data: EventData) -> None:
        self.proc.log.logger.debug("The proc {} is loading".format(self.proc))
        self.proc._load()
        self.proc.log.logger.debug("The proc {} is loaded".format(self.proc))
        super(ProcessInitiatedState, self).enter(event_data)


class ProcessRunningState(ProcessState):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessRunningState, self).__init__(constant.STATE_RUNNING, proc)

    def enter(self, event_data: EventData) -> None:
        self.proc.log.logger.debug("The proc {} is starting".format(self.proc))
        if self.proc.scheduler is not None:
            self.proc.scheduler.scheduler.add_job(self.proc._start, "interval", minutes=self.proc.conf["interval"], id=str(self.proc.id))
        else:
            self.proc._start()
        self.proc.log.logger.debug("The proc {} is running".format(self.proc))
        super(ProcessRunningState, self).enter(event_data)


class ProcessStoppedState(ProcessState):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessStoppedState, self).__init__(constant.STATE_STOPPED, proc)

    def enter(self, event_data: EventData) -> None:
        self.proc.log.logger.debug("The proc {} is stopping".format(self.proc))
        if self.proc.scheduler is not None:
            self.proc.scheduler.scheduler.remove_job(str(self.proc.id))
        else:
            self.proc._stop()
        self.proc.log.logger.debug("The proc {} is stopped".format(self.proc))
        super(ProcessStoppedState, self).enter(event_data)


class ProcessPausedState(ProcessState):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessPausedState, self).__init__(constant.STATE_PAUSED, proc)

    async def enter(self, event_data: EventData) -> None:
        self.proc.log.logger.debug("The proc {} is pausing".format(self.proc))
        if self.proc.scheduler is not None:
            self.proc.scheduler.scheduler.pause_job(str(self.proc.id))
        else:
            self.proc._pause()
        self.proc.log.logger.debug("The proc {} is paused".format(self.proc))
        super(ProcessPausedState, self).enter(event_data)


class ProcessShutdownState(ProcessState):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessShutdownState, self).__init__(constant.STATE_SHUTDOWN, proc)


class ProcessTimeoutState(ProcessState):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        super(ProcessTimeoutState, self).__init__(constant.STATE_TIMEOUT, proc)


class ProcessStateMachine(object):
    """
    classdocs
    """

    def __init__(self, proc: Process) -> None:
        """
        Constructor
        """
        self._proc: Process = proc
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ProcessState] = {
                                                constant.STATE_NEW: ProcessNewState(self._proc),
                                                constant.STATE_INIT: ProcessInitiatedState(self._proc),
                                                constant.STATE_RUNNING: ProcessRunningState(self._proc),
                                                constant.STATE_STOPPED: ProcessStoppedState(self._proc),
                                                constant.STATE_PAUSED: ProcessPausedState(self._proc),
                                                constant.STATE_SHUTDOWN: ProcessShutdownState(self._proc),
                                                constant.STATE_TIMEOUT: ProcessTimeoutState(self._proc)
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
        self.machine: Machine = Machine(model=self._proc,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncProcess(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ProcessAsyncStateMachine = ProcessAsyncStateMachine(self)
        self.enabled: bool = False
        self.log: LogAsyncService | None = None
        self.service: ServiceAsyncManager | None = None
        self.loop: AsyncioLoop | None = None
        self.router: AsyncRouter | None = None
        self.interpreter: Interpreter | None = None
        self.scheduler: AsyncScheduler | None = None
        self.trigger_fact: TriggerFactory | None = None

    async def _load(self) -> None:
        super(AsyncProcess, self)._load()
        if self.router is not None:
            self.router._load()
        if self.interpreter is not None:
            self.interpreter._load()
        if self.trigger_fact is not None:
            self.trigger_fact._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    async def _pause(self) -> None:
        raise NotImplementedError("Should implement _pause()")

    @abstractmethod
    async def _resume(self) -> None:
        raise NotImplementedError("Should implement _resume()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def send_data(self, payload: list, to_clisrv: ZmqAsyncServer) -> None:
        if isinstance(to_clisrv.serializer, ProtobufSerializer):
            obs = of(payload).pipe(ops.map(lambda d: MessageProtobufFactory.create_msg(d, self.id)),
                                   ops.map(lambda d: MessageProtobufFactory.update_msg_before_sending(d, to_clisrv.id)),
                                   ops.map(lambda d: to_clisrv.serializer.serialize(d)),
                                   ops.map(lambda d: to_clisrv.compressor.compress(d)))
        else:
            obs = of(payload).pipe(ops.map(lambda d: MessageFactory.create_msg(d, self.id)),
                                   ops.map(lambda d: MessageFactory.update_msg_before_sending(d, to_clisrv.id)),
                                   ops.map(lambda d: to_clisrv.serializer.serialize(d)),
                                   ops.map(lambda d: to_clisrv.compressor.compress(d)))
        obs.subscribe(on_next=lambda d: to_clisrv.send([d]))

    def forward_data(self, message: net_pb2.Message, to_server: ZmqAsyncServer, from_: list[bytes] | None = None) -> None:
        if isinstance(to_server.serializer, ProtobufSerializer):
            obs = of(message).pipe(ops.map(lambda d: MessageProtobufFactory.update_msg_before_sending(d, to_server.id)),
                                   ops.map(lambda d: to_server.serializer.serialize(d)),
                                   ops.map(lambda d: to_server.compressor.compress(d)))
        else:
            obs = of(message).pipe(ops.map(lambda d: MessageFactory.update_msg_before_sending(d, to_server.id)),
                                   ops.map(lambda d: to_server.serializer.serialize(d)),
                                   ops.map(lambda d: to_server.compressor.compress(d)))
        if from_ is None:
            obs.subscribe(on_next=lambda d: to_server.send([d]))
        else:
            obs.subscribe(on_next=lambda d: to_server.send(from_ + [d]))

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncProcess(id='{}')>".format(self.id)


class RepetitiveAsyncProcess(AsyncProcess, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RepetitiveAsyncProcess, self).__init__()
        self.disposable: Disposable | None = None
        self.obs: Observable | None = None
        self.async_sched: AsyncIOScheduler = None
        self.process_running: bool = False

    @abstractmethod
    async def process(self) -> None:
        raise NotImplementedError("Should implement process()")

    @timed
    def _process(self) -> Observable[_T]:

        async def async_process() -> None:
            try:
                self.process_running = True
                await self.process()
                self.process_running = False
            except Exception as e:
                self.log.logger.exception("An exception occurred : {}".format(str(e)))

        return from_future(self.loop.loop.create_task(async_process()))

    async def _load(self) -> None:
        await super()._load()
        self.async_sched = AsyncIOScheduler(self.loop.loop)
        if "interval" in self.conf:
            obs = timer(0, self.conf["interval"], self.async_sched)
        else:
            obs = timer(0, 0, self.async_sched)
        self.obs = obs.pipe(ops.filter(lambda _: self.state == constant.STATE_RUNNING),
                            ops.filter(lambda _: not self.process_running),
                            ops.flat_map(lambda _: self._process()))

    async def _start(self) -> None:
        if self.disposable is None:
            self.disposable = self.obs.subscribe(on_next=lambda _: self.log.logger.debug("The iteration of {} is completed".format(self.name)),
                                                 scheduler=self.async_sched)

    async def _stop(self) -> None:
        self.disposable.dispose()
        self.disposable = None

    async def _pause(self) -> None:
        pass

    async def _resume(self) -> None:
        pass


class ProcessAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessAsyncState, self).__init__(name=name)
        self.proc = proc


class ProcessNewAsyncState(ProcessAsyncState):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessNewAsyncState, self).__init__(constant.STATE_NEW, proc)


class ProcessInitiatedAsyncState(ProcessAsyncState):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessInitiatedAsyncState, self).__init__(constant.STATE_INIT, proc)

    async def enter(self, event_data: EventData) -> None:
        self.proc.log.logger.debug("The proc {} is loading".format(self.proc))
        await self.proc._load()
        self.proc.log.logger.debug("The proc {} is loaded".format(self.proc))
        await super(ProcessInitiatedAsyncState, self).enter(event_data)


class ProcessRunningAsyncState(ProcessAsyncState):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessRunningAsyncState, self).__init__(constant.STATE_RUNNING, proc)

    async def enter(self, event_data):
        self.proc.log.logger.debug("The proc {} is starting".format(self.proc))
        if self.proc.scheduler is not None:
            trigger = self.proc.trigger_fact.create()
            self.proc.scheduler.scheduler.add_job(self.proc._start, trigger, id=str(self.proc.id))
        else:
            await self.proc._start()
        self.proc.log.logger.debug("The proc {} is running".format(self.proc))
        await super(ProcessRunningAsyncState, self).enter(event_data)


class ProcessStoppedAsyncState(ProcessAsyncState):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessStoppedAsyncState, self).__init__(constant.STATE_STOPPED, proc)

    async def enter(self, event_data: EventData) -> None:
        self.proc.log.logger.debug("The proc {} is stopping".format(self.proc))
        if self.proc.scheduler is not None:
            self.proc.scheduler.scheduler.remove_job(str(self.proc.id))
        else:
            await self.proc._stop()
        self.proc.log.logger.debug("The proc {} is stopped".format(self.proc))
        await super(ProcessStoppedAsyncState, self).enter(event_data)


class ProcessPausedAsyncState(ProcessAsyncState):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessPausedAsyncState, self).__init__(constant.STATE_PAUSED, proc)

    async def enter(self, event_data: EventData) -> None:
        self.proc.log.logger.debug("The proc {} is pausing".format(self.proc))
        if self.proc.scheduler is not None:
            self.proc.scheduler.scheduler.pause_job(str(self.proc.id))
        else:
            await self.proc._pause()
        self.proc.log.logger.debug("The proc {} is paused".format(self.proc))
        await super(ProcessPausedAsyncState, self).enter(event_data)


class ProcessShutdownAsyncState(ProcessAsyncState):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, proc)


class ProcessTimeoutAsyncState(ProcessAsyncState):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        super(ProcessTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, proc)


class ProcessAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, proc: AsyncProcess) -> None:
        """
        Constructor
        """
        self._proc: AsyncProcess = proc
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ProcessAsyncState] = {
                                                      constant.STATE_NEW: ProcessNewAsyncState(self._proc),
                                                      constant.STATE_INIT: ProcessInitiatedAsyncState(self._proc),
                                                      constant.STATE_RUNNING: ProcessRunningAsyncState(self._proc),
                                                      constant.STATE_STOPPED: ProcessStoppedAsyncState(self._proc),
                                                      constant.STATE_SHUTDOWN: ProcessShutdownAsyncState(self._proc),
                                                      constant.STATE_TIMEOUT: ProcessTimeoutAsyncState(self._proc),
                                                      constant.STATE_PAUSED: ProcessPausedAsyncState(self._proc)
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
        self.machine: AsyncMachine = AsyncMachine(model=self._proc,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class CmdServerProcess(AsyncProcess):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CmdServerProcess, self).__init__()
        self.is_running: bool = False
        self.obs: Observable | None = None

    @timed
    def _execute_cmd_payload(self, message: net_pb2.Message, from_: list[bytes]) -> Observable[_T]:

        async def async_execute_cmd_payload(message: net_pb2.Message, from_: list[bytes]) -> None:
            await self.router.route(message, from_)

        return from_future(self.loop.loop.create_task(async_execute_cmd_payload(message, from_)))

    @timed
    def _process_cmd(self, data: list, serializer: Serializer, compressor: Compressor) -> None:
        if isinstance(serializer, ProtobufSerializer):
            obs = of(data[-1]).pipe(ops.map(lambda d: compressor.decompress(d)),
                                    ops.map(lambda d: serializer.deserialize(d)),
                                    ops.map(lambda d: self._execute_cmd_payload(d, data[:-1])))
        else:
            obs = of(data[-1]).pipe(ops.map(lambda d: compressor.decompress(d)),
                                    ops.map(lambda d: serializer.deserialize(d)),
                                    ops.map(lambda d: self._execute_cmd_payload(d, data[:-1])))
        obs.subscribe(on_next=lambda d: self.log.logger.debug("The process data has been launched"))

    def _process_create_cmd_observable(self) -> Observable[_T]:
        cmd_srv = self.service.managers["net"].services["kernel"].servers["cmd"]
        queue = cmd_srv.protocol.queue

        def process_create_cmd(observer, scheduler) -> Disposable:
            async def async_process_create_cmd() -> None:
                try:
                    while True:
                        data = await queue.get()
                        observer.on_next(data)
                except Exception as e:
                    self.log.logger.exception("An exception occurred : {}".format(str(e)))
                    self.log.logger.exception(traceback.format_exc())
                    self.loop.loop.call_soon(functools.partial(observer.on_error, e))

            task = ensure_future(async_process_create_cmd())
            return Disposable(lambda: task.cancel())

        return create(process_create_cmd)

    async def _start(self) -> None:
        self.is_running = True
        if self.obs is None:
            scheduler = AsyncIOScheduler(self.loop.loop)
            cmd_srv = self.service.managers["net"].services["kernel"].servers["cmd"]
            self.obs = self._process_create_cmd_observable().pipe(ops.filter(lambda _: self.is_running is True),
                                                                  ops.map(lambda d: self._process_cmd(d, cmd_srv.serializer, cmd_srv.compressor)))
            self.obs.subscribe(on_next=lambda d: self.log.logger.debug("The received cmd has been processed"),
                                  scheduler=scheduler)

    async def _stop(self) -> None:
        self.obs.dispose()
        self.obs = None

    async def _pause(self) -> None:
        self.is_running = False

    async def _resume(self) -> None:
        self.is_running = True


class CmdCLIClientProcess(AsyncProcess):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CmdCLIClientProcess, self).__init__()
        self.interpreter: CmdInterpreter | None = None
        self.is_running: bool = False

        self.input_disposable: Disposable | None = None
        self.input_obs: Observable | None = None

        self.cmd_disposable: Disposable | None = None
        self.cmd_obs: Observable | None = None

    async def _load(self) -> None:
        await super()._load()

        self.input_obs = self._process_read_input_observable().pipe(ops.filter(lambda _: self.is_running is True),
                                                                    ops.flat_map(lambda cmd_line: self._process_cmd(cmd_line)))

        cmd_client = self.service.managers["net"].services["cmd"].clients["cmd"]
        self.cmd_obs = self._process_create_cmd_response_observable().pipe(ops.filter(lambda _: self.is_running is True),
                                                                           ops.map(lambda d: self._process_cmd_response(d, cmd_client.serializer, cmd_client.compressor)))

    @timed
    def _process_cmd(self, cmd_line: str) -> Observable[_T]:

        async def async_process_cmd(cmd_line: str) -> None:
            cmd_client = self.service.managers["net"].services["cmd"].clients["cmd"]

            payload = self.interpreter.create_commands(cmd_line)
            if payload is not None:
                self.send_data(payload, cmd_client)
            else:
                self.log.logger.debug("No command to send")

        return from_future(self.loop.loop.create_task(async_process_cmd(cmd_line)))

    @timed
    def _print_cmd_response(self, message: net_pb2.Message):
        for p in message.payload:
            cmd_resp = cmd_pb2.CommandResponse()
            cmd_resp.ParseFromString(p.value)
            res = []
            for result in cmd_resp.result:
                if result.Is(cmd_pb2.StringResult.DESCRIPTOR):
                    r = cmd_pb2.StringResult()
                    r.ParseFromString(result.value)
                    res.append(r.content)
                else:
                    res.append(result)
            out_resp = """Response id : {}
Request id : {}
Reply date : {}
Reply by : {}
Code : {}
Message : {}
Result :

{}""".format(uuid.UUID(bytes=cmd_resp.id.value, version=4),
           uuid.UUID(bytes=cmd_resp.req_id.value, version=4),
           datetime.fromisoformat(cmd_resp.rep_date),
           uuid.UUID(bytes=cmd_resp.rep_by.value, version=4),
           cmd_resp.code,
           cmd_resp.msg,
           "\n".join([str(r) for r in res]))
            print(out_resp)
        if "prompt" in self.conf:
            sys.stdout.write("{} ".format(self.conf["prompt"]))
            sys.stdout.flush()

    @timed
    def _process_cmd_response(self, data: list, serializer: Serializer, compressor: Compressor) -> None:
        self.log.logger.debug("The process command response has been launched")

        if isinstance(serializer, ProtobufSerializer):
            obs = of(data).pipe(ops.map(lambda d: compressor.decompress(d)),
                                ops.map(lambda d: serializer.deserialize(d)))
        else:
            obs = of(data).pipe(ops.map(lambda d: compressor.decompress(d)),
                                ops.map(lambda d: serializer.deserialize(d)))
        obs.subscribe(on_next=lambda d: self._print_cmd_response(d))

    @timed
    def _process_create_cmd_response_observable(self) -> Observable[_T]:
        cmd_client = self.service.managers["net"].services["cmd"].clients["cmd"]
        queue = cmd_client.protocol.queue

        def process_create_cmd_response(observer, scheduler) -> Disposable:
            async def async_process_create_cmd_response() -> None:
                try:
                    while True:
                        data = await queue.get()
                        observer.on_next(data)
                except Exception as e:
                    self.log.logger.exception("An exception occurred : {}".format(str(e)))
                    self.loop.loop.call_soon(functools.partial(observer.on_error, e))

            task = ensure_future(async_process_create_cmd_response())
            return Disposable(lambda: task.cancel())

        return create(process_create_cmd_response)

    def _process_read_input_observable(self) -> Observable[_T]:

        def process_read_input(observer, scheduler) -> Disposable:
            async def async_process_read_input() -> None:
                try:
                    is_quit = False
                    if "banner" in self.conf:
                        print(self.conf["banner"])
                    async with aiofiles.open("/dev/stdin", mode="r") as f:
                        if "prompt" in self.conf:
                            sys.stdout.write("{} ".format(self.conf["prompt"]))
                            sys.stdout.flush()
                        while not is_quit:
                            line = await f.readline()
                            observer.on_next(line.rstrip())
                except Exception as e:
                    self.log.logger.exception("An exception occurred : {}".format(str(e)))
                    self.loop.loop.call_soon(functools.partial(observer.on_error, e))

            task = ensure_future(async_process_read_input())
            return Disposable(lambda: task.cancel())

        return create(process_read_input)

    async def _start(self) -> None:
        scheduler = AsyncIOScheduler(self.loop.loop)

        self.is_running = True
        if self.input_disposable is None:
            self.input_disposable = self.input_obs.subscribe(on_next=lambda line: self.log.logger.debug("The received command {} has been processed".format(line)),
                                                             scheduler=scheduler)

        if self.cmd_disposable is None:
            self.cmd_disposable = self.cmd_obs.subscribe(on_next=lambda d: self.log.logger.debug("The received command response has been processed"),
                                                         scheduler=scheduler)

    async def _stop(self) -> None:
        self.input_disposable.dispose()
        self.input_disposable = None

        self.cmd_disposable.dispose()
        self.cmd_disposable = None

    async def _pause(self) -> None:
        self.is_running = False

    async def _resume(self) -> None:
        self.is_running = True
