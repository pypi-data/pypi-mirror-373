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
import asyncio
from transitions.extensions.asyncio import AsyncMachine

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
from galaxy.engine import constant


class EngineManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(EngineManager, self).__init__()
        self.engines: dict[CompId, Engine] = {}

    def load_all(self) -> None:
        [engine.load() for engine in self.engines.values()]

    def _start(self) -> None:
        [engine.start() for engine in self.engines.values()]

    def _stop(self) -> None:
        [engine.stop() for engine in self.engines.values()]

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<EngineManager(id='{}')>".format(self.id)


class EngineAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(EngineAsyncManager, self).__init__()
        self.engines: dict[CompId, AsyncEngine] = {}

    async def load_all(self) -> None:
        await asyncio.gather(*[engine.load() for engine in self.engines.values()])

    async def _start(self) -> None:
        await asyncio.gather(*[engine.start() for engine in self.engines.values()])

    async def _stop(self) -> None:
        await asyncio.gather(*[engine.stop() for engine in self.engines.values()])

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<EngineAsyncManager(id='{}')>".format(self.id)


class Engine(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: EngineStateMachine = EngineStateMachine(self)
        self.enabled: bool = False
        self.log: LogService | None = None
        self.service: ServiceManager | None = None

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
        return "<Engine(id='{}')>".format(self.id)


class EngineState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, engine: Engine) -> None:
        """
        Constructor
        """
        super(EngineState, self).__init__(name=name)
        self.engine = engine


class EngineNewState(EngineState):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        super(EngineNewState, self).__init__(constant.STATE_NEW, engine)


class EngineInitiatedState(EngineState):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        super(EngineInitiatedState, self).__init__(constant.STATE_INIT, engine)

    def enter(self, event_data: EventData) -> None:
        self.engine.log.logger.debug("The engine {} is loading".format(self.engine))
        self.engine._load()
        self.engine.log.logger.debug("The engine {} is loaded".format(self.engine))
        super(EngineInitiatedState, self).enter(event_data)


class EngineRunningState(EngineState):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        super(EngineRunningState, self).__init__(constant.STATE_RUNNING, engine)

    def enter(self, event_data: EventData) -> None:
        self.engine.log.logger.debug("The engine {} is starting".format(self.engine))
        self.engine._start()
        self.engine.log.logger.debug("The engine {} is running".format(self.engine))
        super(EngineRunningState, self).enter(event_data)


class EngineStoppedState(EngineState):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        super(EngineStoppedState, self).__init__(constant.STATE_STOPPED, engine)

    def enter(self, event_data: EventData) -> None:
        self.engine.log.logger.debug("The engine {} is stopping".format(self.engine))
        self.engine._stop()
        self.engine.log.logger.debug("The engine {} is stopped".format(self.engine))
        super(EngineStoppedState, self).enter(event_data)


class EnginePausedState(EngineState):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        super(EnginePausedState, self).__init__(constant.STATE_PAUSED, engine)

    async def enter(self, event_data: EventData) -> None:
        self.engine.log.logger.debug("The engine {} is pausing".format(self.engine))
        self.engine._pause()
        self.engine.log.logger.debug("The engine {} is paused".format(self.engine))
        super(EnginePausedState, self).enter(event_data)


class EngineShutdownState(EngineState):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        super(EngineShutdownState, self).__init__(constant.STATE_SHUTDOWN, engine)


class EngineTimeoutState(EngineState):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        super(EngineTimeoutState, self).__init__(constant.STATE_TIMEOUT, engine)


class EngineStateMachine(object):
    """
    classdocs
    """

    def __init__(self, engine: Engine) -> None:
        """
        Constructor
        """
        self._engine: Engine = engine
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, EngineState] = {
                                               constant.STATE_NEW: EngineNewState(self._engine),
                                               constant.STATE_INIT: EngineInitiatedState(self._engine),
                                               constant.STATE_RUNNING: EngineRunningState(self._engine),
                                               constant.STATE_STOPPED: EngineStoppedState(self._engine),
                                               constant.STATE_PAUSED: EnginePausedState(self._engine),
                                               constant.STATE_SHUTDOWN: EngineShutdownState(self._engine),
                                               constant.STATE_TIMEOUT: EngineTimeoutState(self._engine)
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
        self.machine: Machine = Machine(model=self._engine,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncEngine(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: EngineAsyncStateMachine = EngineAsyncStateMachine(self)
        self.enabled: bool = False
        self.log: LogAsyncService | None = None
        self.service: ServiceAsyncManager | None = None

    async def _load(self) -> None:
        super(AsyncEngine, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    async def _pause(self) -> None:
        raise NotImplementedError("Should implement _pause()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncEngine(id='{}')>".format(self.id)


class EngineAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EngineAsyncState, self).__init__(name=name)
        self.engine = engine


class EngineNewAsyncState(EngineAsyncState):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EngineNewAsyncState, self).__init__(constant.STATE_NEW, engine)


class EngineInitiatedAsyncState(EngineAsyncState):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EngineInitiatedAsyncState, self).__init__(constant.STATE_INIT, engine)

    async def enter(self, event_data: EventData) -> None:
        self.engine.log.logger.debug("The engine {} is loading".format(self.engine))
        await self.engine._load()
        self.engine.log.logger.debug("The engine {} is loaded".format(self.engine))
        await super(EngineInitiatedAsyncState, self).enter(event_data)


class EngineRunningAsyncState(EngineAsyncState):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EngineRunningAsyncState, self).__init__(constant.STATE_RUNNING, engine)

    async def enter(self, event_data):
        self.engine.log.logger.debug("The engine {} is starting".format(self.engine))
        await self.engine._start()
        self.engine.log.logger.debug("The engine {} is running".format(self.engine))
        await super(EngineRunningAsyncState, self).enter(event_data)


class EngineStoppedAsyncState(EngineAsyncState):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EngineStoppedAsyncState, self).__init__(constant.STATE_STOPPED, engine)

    async def enter(self, event_data: EventData) -> None:
        self.engine.log.logger.debug("The engine {} is stopping".format(self.engine))
        await self.engine._stop()
        self.engine.log.logger.debug("The engine {} is stopped".format(self.engine))
        await super(EngineStoppedAsyncState, self).enter(event_data)


class EnginePausedAsyncState(EngineAsyncState):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EnginePausedAsyncState, self).__init__(constant.STATE_PAUSED, engine)

    async def enter(self, event_data: EventData) -> None:
        self.engine.log.logger.debug("The engine {} is pausing".format(self.engine))
        await self.engine._pause()
        self.engine.log.logger.debug("The engine {} is paused".format(self.engine))
        await super(EnginePausedAsyncState, self).enter(event_data)


class EngineShutdownAsyncState(EngineAsyncState):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EngineShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, engine)


class EngineTimeoutAsyncState(EngineAsyncState):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        super(EngineTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, engine)


class EngineAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """
        Constructor
        """
        self._engine: AsyncEngine = engine
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, EngineAsyncState] = {
                                                    constant.STATE_NEW: EngineNewAsyncState(self._engine),
                                                    constant.STATE_INIT: EngineInitiatedAsyncState(self._engine),
                                                    constant.STATE_RUNNING: EngineRunningAsyncState(self._engine),
                                                    constant.STATE_STOPPED: EngineStoppedAsyncState(self._engine),
                                                    constant.STATE_SHUTDOWN: EngineShutdownAsyncState(self._engine),
                                                    constant.STATE_TIMEOUT: EngineTimeoutAsyncState(self._engine),
                                                    constant.STATE_PAUSED: EnginePausedAsyncState(self._engine)
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
