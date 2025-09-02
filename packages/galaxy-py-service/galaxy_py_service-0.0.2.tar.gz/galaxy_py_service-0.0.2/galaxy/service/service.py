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
import asyncio
from collections import OrderedDict
from transitions.core import Machine,                           \
                        EventData
from transitions.extensions.asyncio import AsyncMachine
from typing import Any

from galaxy.service import constant
from galaxy.utils.type import CompId
from galaxy.utils.base import Component,                        \
                              Configurable,                     \
                              TimestampedState,                 \
                              TimestampedAsyncState


class Service(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ServiceStateMachine = ServiceStateMachine(self)
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
        return "<Service(id='{}')>".format(self.id)


class LogService(Service, ABC):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(LogService, self).__init__()
        self.logger: Any | None = None

    def __repr__(self) -> str:
        return "<LogService(id='{}')>".format(self.id)


class ServiceState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, srv: Service) -> None:
        """
        Constructor
        """
        super(ServiceState, self).__init__(name=name)
        self.srv = srv


class ServiceNewState(ServiceState):
    """
    classdocs
    """

    def __init__(self, srv: Service) -> None:
        """
        Constructor
        """
        super(ServiceNewState, self).__init__(constant.STATE_NEW, srv)


class ServiceInitiatedState(ServiceState):
    """
    classdocs
    """

    def __init__(self, srv: Service) -> None:
        """
        Constructor
        """
        super(ServiceInitiatedState, self).__init__(constant.STATE_INIT, srv)

    def enter(self, event_data: EventData) -> None:
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is loading".format(self.srv))
        self.srv._load()
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is loaded".format(self.srv))
        super(ServiceInitiatedState, self).enter(event_data)


class ServiceRunningState(ServiceState):
    """
    classdocs
    """

    def __init__(self, srv: Service) -> None:
        """
        Constructor
        """
        super(ServiceRunningState, self).__init__(constant.STATE_RUNNING, srv)

    def enter(self, event_data: EventData) -> None:
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is starting".format(self.srv))
        self.srv._start()
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is running".format(self.srv))
        super(ServiceRunningState, self).enter(event_data)


class ServiceStoppedState(ServiceState):
    """
    classdocs
    """

    def __init__(self, srv: Service) -> None:
        """
        Constructor
        """
        super(ServiceStoppedState, self).__init__(constant.STATE_STOPPED, srv)

    def enter(self, event_data: EventData) -> None:
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is stopping".format(self.srv))
        self.srv._stop()
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is stopped".format(self.srv))
        super(ServiceStoppedState, self).enter(event_data)


class ServiceShutdownState(ServiceState):
    """
    classdocs
    """

    def __init__(self, srv: Service) -> None:
        """
        Constructor
        """
        super(ServiceShutdownState, self).__init__(constant.STATE_SHUTDOWN, srv)


class ServiceTimeoutState(ServiceState):
    """
    classdocs
    """

    def __init__(self, srv: Service) -> None:
        """
        Constructor
        """
        super(ServiceTimeoutState, self).__init__(constant.STATE_TIMEOUT, srv)


class ServiceStateMachine(object):
    """
    classdocs
    """

    def __init__(self, srv: Service) -> None:
        """
        Constructor
        """
        self._srv: Service = srv
        self.enabled: bool = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ServiceState] = {
                                                constant.STATE_NEW: ServiceNewState(self._srv),
                                                constant.STATE_INIT: ServiceInitiatedState(self._srv),
                                                constant.STATE_RUNNING: ServiceRunningState(self._srv),
                                                constant.STATE_STOPPED: ServiceStoppedState(self._srv),
                                                constant.STATE_SHUTDOWN: ServiceShutdownState(self._srv),
                                                constant.STATE_TIMEOUT: ServiceTimeoutState(self._srv)
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
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: Machine = Machine(model=self._srv,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncService(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ServiceAsyncStateMachine = ServiceAsyncStateMachine(self)
        self.enabled: bool = False
        self.log: LogAsyncService | None = None

    async def _load(self):
        super(AsyncService, self)._load()

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
        return "<AsyncService(id='{}')>".format(self.id)


class LogAsyncService(AsyncService, ABC):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(LogAsyncService, self).__init__()
        self.logger: Any | None = None

    def __repr__(self) -> str:
        return "<LogAsyncService(id='{}')>".format(self.id)


class ServiceAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, srv: AsyncService) -> None:
        """
        Constructor
        """
        super(ServiceAsyncState, self).__init__(name=name)
        self.srv = srv


class ServiceNewAsyncState(ServiceAsyncState):
    """
    classdocs
    """

    def __init__(self, srv: AsyncService) -> None:
        """
        Constructor
        """
        super(ServiceNewAsyncState, self).__init__(constant.STATE_NEW, srv)


class ServiceInitiatedAsyncState(ServiceAsyncState):
    """
    classdocs
    """

    def __init__(self, srv: AsyncService) -> None:
        """
        Constructor
        """
        super(ServiceInitiatedAsyncState, self).__init__(constant.STATE_INIT, srv)

    async def enter(self, event_data: EventData) -> None:
        if not isinstance(self.srv, LogAsyncService):
            self.srv.log.logger.debug("The service {} is loading".format(self.srv))
        await self.srv._load()
        if not isinstance(self.srv, LogAsyncService):
            self.srv.log.logger.debug("The service {} is loaded".format(self.srv))
        await super(ServiceInitiatedAsyncState, self).enter(event_data)


class ServiceRunningAsyncState(ServiceAsyncState):
    """
    classdocs
    """

    def __init__(self, srv: AsyncService) -> None:
        """
        Constructor
        """
        super(ServiceRunningAsyncState, self).__init__(constant.STATE_RUNNING, srv)

    async def enter(self, event_data):
        if not isinstance(self.srv, LogAsyncService):
            self.srv.log.logger.debug("The service {} is starting".format(self.srv))
        await self.srv._start()
        if not isinstance(self.srv, LogAsyncService):
            self.srv.log.logger.debug("The service {} is running".format(self.srv))
        await super(ServiceRunningAsyncState, self).enter(event_data)


class ServiceStoppedAsyncState(ServiceAsyncState):
    """
    classdocs
    """

    def __init__(self, srv: AsyncService) -> None:
        """
        Constructor
        """
        super(ServiceStoppedAsyncState, self).__init__(constant.STATE_STOPPED, srv)

    async def enter(self, event_data: EventData) -> None:
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is stopping".format(self.srv))
        await self.srv._stop()
        if not isinstance(self.srv, LogService):
            self.srv.log.logger.debug("The service {} is stopped".format(self.srv))
        await super(ServiceStoppedAsyncState, self).enter(event_data)


class ServiceShutdownAsyncState(ServiceAsyncState):
    """
    classdocs
    """

    def __init__(self, srv: AsyncService) -> None:
        """
        Constructor
        """
        super(ServiceShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, srv)


class ServiceTimeoutAsyncState(ServiceAsyncState):
    """
    classdocs
    """

    def __init__(self, srv: AsyncService) -> None:
        """
        Constructor
        """
        super(ServiceTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, srv)


class ServiceAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, srv: AsyncService) -> None:
        """
        Constructor
        """
        self._srv: AsyncService = srv
        self.enabled = False
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ServiceAsyncState] = {
                                                      constant.STATE_NEW: ServiceNewAsyncState(self._srv),
                                                      constant.STATE_INIT: ServiceInitiatedAsyncState(self._srv),
                                                      constant.STATE_RUNNING: ServiceRunningAsyncState(self._srv),
                                                      constant.STATE_STOPPED: ServiceStoppedAsyncState(self._srv),
                                                      constant.STATE_SHUTDOWN: ServiceShutdownAsyncState(self._srv),
                                                      constant.STATE_TIMEOUT: ServiceTimeoutAsyncState(self._srv)
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
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: AsyncMachine = AsyncMachine(model=self._srv,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class Manager(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(Component, self).__init__()
        self._machine: ManagerStateMachine = ManagerStateMachine(self)
        self.enabled: bool = False
        self.log: LogService | None = None
        self.services: dict[str, Service] = {}

    def _start(self) -> None:
        [service.start() for service in self.services.values()]

    def _stop(self) -> None:
        [service.stop() for service in self.services.values()]

    def restart(self) -> None:
        self.stop()
        self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Manager(id='{}')>".format(self.id)


class ManagerState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, mgr: Manager) -> None:
        """
        Constructor
        """
        super(ManagerState, self).__init__(name=name)
        self.mgr: Manager = mgr


class ManagerNewState(ManagerState):
    """
    classdocs
    """

    def __init__(self, mgr: Manager) -> None:
        """
        Constructor
        """
        super(ManagerNewState, self).__init__(constant.STATE_NEW, mgr)


class ManagerRunningState(ManagerState):
    """
    classdocs
    """

    def __init__(self, mgr: Manager) -> None:
        """
        Constructor
        """
        super(ManagerRunningState, self).__init__(constant.STATE_RUNNING, mgr)

    def enter(self, event_data: EventData) -> None:
        self.mgr.log.logger.debug("The manager {} is starting".format(self.mgr))
        self.mgr._start()
        self.mgr.log.logger.debug("The manager {} is running".format(self.mgr))
        super(ManagerRunningState, self).enter(event_data)


class ManagerStoppedState(ManagerState):
    """
    classdocs
    """

    def __init__(self, mgr: Manager) -> None:
        """
        Constructor
        """
        super(ManagerStoppedState, self).__init__(constant.STATE_STOPPED, mgr)

    def enter(self, event_data: EventData) -> None:
        self.mgr.log.logger.debug("The manager {} is stopping".format(self.mgr))
        self.mgr._stop()
        self.mgr.log.logger.debug("The manager {} is stopped".format(self.mgr))
        super(ManagerStoppedState, self).enter(event_data)


class ManagerShutdownState(ManagerState):
    """
    classdocs
    """

    def __init__(self, mgr: Manager) -> None:
        """
        Constructor
        """
        super(ManagerShutdownState, self).__init__(constant.STATE_SHUTDOWN, mgr)


class ManagerTimeoutState(ManagerState):
    """
    classdocs
    """

    def __init__(self, mgr: Manager) -> None:
        """
        Constructor
        """
        super(ManagerTimeoutState, self).__init__(constant.STATE_TIMEOUT, mgr)


class ManagerStateMachine(object):
    """
    classdocs
    """

    def __init__(self, mgr: Manager) -> None:
        """
        Constructor
        """
        self._mgr: Manager = mgr
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ManagerState] = {
                                                constant.STATE_NEW: ManagerNewState(self._mgr),
                                                constant.STATE_RUNNING: ManagerRunningState(self._mgr),
                                                constant.STATE_STOPPED: ManagerStoppedState(self._mgr),
                                                constant.STATE_SHUTDOWN: ManagerShutdownState(self._mgr),
                                                constant.STATE_TIMEOUT: ManagerTimeoutState(self._mgr)
                                               }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "start",
                                                    "source": constant.STATE_NEW,
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
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: Machine = Machine(model=self._mgr,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncManager(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(Component, self).__init__()
        self._machine: ManagerAsyncStateMachine = ManagerAsyncStateMachine(self)
        self.enabled: bool = False
        self.log: LogAsyncService | None = None
        self.services: dict[str, AsyncService] = OrderedDict({})

    async def _start(self) -> None:
        # The services should be loaded synchronously due of dependencies between themselves
        [await service.start() for service in self.services.values()]
        #await asyncio.gather(*[service.start() for service in self.services.values()])

    async def _stop(self) -> None:
        await asyncio.gather(*[service.stop() for service in self.services.values()])

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncManager(id='{}')>".format(self.id)


class ManagerAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, mgr: AsyncManager) -> None:
        """
        Constructor
        """
        super(ManagerAsyncState, self).__init__(name=name)
        self.mgr: AsyncManager = mgr


class ManagerNewAsyncState(ManagerAsyncState):
    """
    classdocs
    """

    def __init__(self, mgr: AsyncManager) -> None:
        """
        Constructor
        """
        super(ManagerNewAsyncState, self).__init__(constant.STATE_NEW, mgr)


class ManagerRunningAsyncState(ManagerAsyncState):
    """
    classdocs
    """

    def __init__(self, mgr: AsyncManager) -> None:
        """
        Constructor
        """
        super(ManagerRunningAsyncState, self).__init__(constant.STATE_RUNNING, mgr)

    async def enter(self, event_data: EventData) -> None:
        self.mgr.log.logger.debug("The manager {} is starting".format(self.mgr))
        await self.mgr._start()
        self.mgr.log.logger.debug("The manager {} is running".format(self.mgr))
        await super(ManagerRunningAsyncState, self).enter(event_data)


class ManagerStoppedAsyncState(ManagerAsyncState):
    """
    classdocs
    """

    def __init__(self, mgr: AsyncManager) -> None:
        """
        Constructor
        """
        super(ManagerStoppedAsyncState, self).__init__(constant.STATE_STOPPED, mgr)

    async def enter(self, event_data: EventData) -> None:
        self.mgr.log.logger.debug("The manager {} is stopping".format(self.mgr))
        await self.mgr._stop()
        self.mgr.log.logger.debug("The manager {} is stopped".format(self.mgr))
        await super(ManagerStoppedAsyncState, self).enter(event_data)


class ManagerShutdownAsyncState(ManagerAsyncState):
    """
    classdocs
    """

    def __init__(self, mgr: AsyncManager) -> None:
        """
        Constructor
        """
        super(ManagerShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, mgr)


class ManagerTimeoutAsyncState(ManagerAsyncState):
    """
    classdocs
    """

    def __init__(self, mgr: AsyncManager) -> None:
        """
        Constructor
        """
        super(ManagerTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, mgr)


class ManagerAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, mgr: AsyncManager) -> None:
        """
        Constructor
        """
        self._mgr: AsyncManager = mgr
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ManagerAsyncState] = {
                                                     constant.STATE_NEW: ManagerNewAsyncState(self._mgr),
                                                     constant.STATE_RUNNING: ManagerRunningAsyncState(self._mgr),
                                                     constant.STATE_STOPPED: ManagerStoppedAsyncState(self._mgr),
                                                     constant.STATE_SHUTDOWN: ManagerShutdownAsyncState(self._mgr),
                                                     constant.STATE_TIMEOUT: ManagerTimeoutAsyncState(self._mgr)
                                                    }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "start",
                                                    "source": constant.STATE_NEW,
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
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: AsyncMachine = AsyncMachine(model=self._mgr,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class ServiceManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ServiceManager, self).__init__()
        self.managers: dict[str, Manager] = OrderedDict({})

    def load_all(self) -> None:
        #[service.load() for mgr in self.managers.values() for service in mgr.services.values()]
        for service in [service for mgr in self.managers.values() for service in mgr.services.values()]:
            print(service.id)
            service.load()

    def _start(self) -> None:
        [mgr.start() for mgr in self.managers.values()]

    def _stop(self) -> None:
        [mgr.stop() for mgr in self.managers.values()]

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<ServiceManager(id='{}')>".format(self.id)


class ServiceAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ServiceAsyncManager, self).__init__()
        self.managers: dict[str, AsyncManager] = OrderedDict({})

    async def load_all(self) -> None:
        # The services should be loaded synchronously due of dependencies between themselves
        # (for example, DatabaseAsyncService should be loaded before DataModelAsyncService).
        # The trade-off can be accepted during the loading phase.
        [await service.load() for mgr in self.managers.values() for service in mgr.services.values()]

    async def _start(self) -> None:
        await asyncio.gather(*[mgr.start() for mgr in self.managers.values()])

    async def _stop(self) -> None:
        await asyncio.gather(*[mgr.stop() for mgr in self.managers.values()])

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<ServiceAsyncManager(id='{}')>".format(self.id)
