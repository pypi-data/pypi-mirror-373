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

from abc import ABC,                                        \
                abstractmethod
from transitions.core import Machine,                       \
                             EventData
import asyncio
from transitions.extensions.asyncio import AsyncMachine
from typing import TYPE_CHECKING
from collections import OrderedDict

from galaxy.utils.base import Component,                    \
                              TimestampedState,             \
                              TimestampedAsyncState,        \
                              Configurable
from galaxy.service.service import Manager,                 \
                                   AsyncManager,            \
                                   Service,                 \
                                   AsyncService,            \
                                   LogService,              \
                                   LogAsyncService
from galaxy.service import constant
from galaxy.utils.type import CompId

if TYPE_CHECKING:
    from galaxy.data.db.db import DAO,                      \
                                  AsyncDAO


class DataModelManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DataModelManager, self).__init__()

    def __repr__(self) -> str:
        return "<DataModelManager(id='{}')>".format(self.id)


class DataModelAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DataModelAsyncManager, self).__init__()

    def __repr__(self) -> str:
        return "<DataModelAsyncManager(id='{}')>".format(self.id)


class DataModelService(Service):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DataModelService, self).__init__()
        self.models: dict[str, AsyncDataModel] = OrderedDict({})

    def _load(self) -> None:
        super(DataModelService, self)._load()
        [model.load() for model in self.models.values()]

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        [model.clear() for model in self.models.values()]

    def __repr__(self) -> str:
        return "<DataModelService(id='{}')>".format(self.id)


class DataModelAsyncService(AsyncService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DataModelAsyncService, self).__init__()
        self.models: dict[str, AsyncDataModel] = OrderedDict({})

    async def _load(self) -> None:
        await super(DataModelAsyncService, self)._load()

        # The data models should be loaded synchronously due of dependencies between themselves.
        # The trade-off can be accepted during the loading phase.
        [await model.load() for model in self.models.values()]

    async def _start(self) -> None:
        pass

    async def _stop(self) -> None:
        await asyncio.gather(*[model.clear() for model in self.models.values()])

    def __repr__(self) -> str:
        return "<DataModelService(id='{}')>".format(self.id)


class SnowflakeDataModelAsyncService(DataModelAsyncService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SnowflakeDataModelAsyncService, self).__init__()
        self.models: dict[str, DataModel] = OrderedDict({})

    async def _load(self) -> None:
        await super(DataModelAsyncService, self)._load()

        # The data models should be loaded synchronously due of dependencies between themselves.
        # The trade-off can be accepted during the loading phase.
        [model.load() for model in self.models.values()]

    async def _stop(self) -> None:
        [model.clear() for model in self.models.values()]

    def __repr__(self) -> str:
        return "<SnowflakeDataModelAsyncService(id='{}')>".format(self.id)


class DataModel(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: DataModelStateMachine = DataModelStateMachine(self)
        self.daos: dict[CompId, DAO] | None = None
        self.models: dict[str, DataModel] | None = None
        self.log: LogService | None = None

    def _load(self):
        super(DataModel, self)._load()

    @abstractmethod
    def _clear(self) -> None:
        raise NotImplementedError("Should implement clear()")

    def __repr__(self) -> str:
        return "<DataModel(id='{}')>".format(self.id)


class DataModelState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, model: DataModel) -> None:
        """
        Constructor
        """
        super(DataModelState, self).__init__(name=name)
        self.model: DataModel = model


class DataModelNewState(DataModelState):
    """
    classdocs
    """

    def __init__(self, model: DataModel) -> None:
        """
        Constructor
        """
        super(DataModelNewState, self).__init__(constant.STATE_NEW, model)


class DataModelInitiatedState(DataModelState):
    """
    classdocs
    """

    def __init__(self, model: DataModel) -> None:
        """
        Constructor
        """
        super(DataModelInitiatedState, self).__init__(constant.STATE_INIT, model)

    def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The data model {} is loading".format(self.model))
        self.model._load()
        self.model.log.logger.debug("The data model {} is loaded".format(self.model))
        super(DataModelInitiatedState, self).enter(event_data)


class DataModelClearedState(DataModelState):
    """
    classdocs
    """

    def __init__(self, model: DataModel) -> None:
        """
        Constructor
        """
        super(DataModelClearedState, self).__init__(constant.STATE_CLEARED, model)

    def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The data model {} is clearing".format(self.model))
        self.model._clear()
        self.model.log.logger.debug("The data model {} is cleared".format(self.model))
        super(DataModelClearedState, self).enter(event_data)


class DataModelShutdownState(DataModelState):
    """
    classdocs
    """

    def __init__(self, model: DataModel) -> None:
        """
        Constructor
        """
        super(DataModelShutdownState, self).__init__(constant.STATE_SHUTDOWN, model)


class DataModelStateMachine(object):
    """
    classdocs
    """

    def __init__(self, model: DataModel) -> None:
        """
        Constructor
        """
        self._model: DataModel = model
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, DataModelState] = {
                                                  constant.STATE_NEW: DataModelNewState(self._model),
                                                  constant.STATE_INIT: DataModelInitiatedState(self._model),
                                                  constant.STATE_CLEARED: DataModelClearedState(self._model),
                                                  constant.STATE_SHUTDOWN: DataModelShutdownState(self._model)
                                                 }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "clear",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_CLEARED
                                                   },
                                                   {
                                                    "trigger": "load",
                                                    "source": constant.STATE_CLEARED,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: Machine = Machine(model=self._model,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncDataModel(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: DataModelAsyncStateMachine = DataModelAsyncStateMachine(self)
        self.daos: dict[str, AsyncDAO] | None = None
        self.models: dict[str, AsyncDataModel] | None = None
        self.log: LogAsyncService | None = None

    async def _load(self):
        super(AsyncDataModel, self)._load()

    @abstractmethod
    def _clear(self) -> None:
        raise NotImplementedError("Should implement clear()")

    def __repr__(self) -> str:
        return "<AsyncDataModel(id='{}')>".format(self.id)


class DataModelAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, model: AsyncDataModel) -> None:
        """
        Constructor
        """
        super(DataModelAsyncState, self).__init__(name=name)
        self.model: AsyncDataModel = model


class DataModelNewAsyncState(DataModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: AsyncDataModel) -> None:
        """
        Constructor
        """
        super(DataModelNewAsyncState, self).__init__(constant.STATE_NEW, model)


class DataModelInitiatedAsyncState(DataModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: AsyncDataModel) -> None:
        """
        Constructor
        """
        super(DataModelInitiatedAsyncState, self).__init__(constant.STATE_INIT, model)

    async def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The data model {} is loading".format(self.model))
        await self.model._load()
        self.model.log.logger.debug("The data model {} is loaded".format(self.model))
        await super(DataModelInitiatedAsyncState, self).enter(event_data)


class DataModelClearedAsyncState(DataModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: AsyncDataModel) -> None:
        """
        Constructor
        """
        super(DataModelClearedAsyncState, self).__init__(constant.STATE_CLEARED, model)

    async def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The data model {} is clearing".format(self.model))
        self.model._clear()
        self.model.log.logger.debug("The data model {} is cleared".format(self.model))
        await super(DataModelClearedAsyncState, self).enter(event_data)


class DataModelShutdownAsyncState(DataModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: AsyncDataModel) -> None:
        """
        Constructor
        """
        super(DataModelShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, model)


class DataModelAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, model: AsyncDataModel) -> None:
        """
        Constructor
        """
        self._model: AsyncDataModel = model
        self._init_states()
        self._init_machine()

    def _init_states(self):
        self.states: dict[str, DataModelAsyncState] = {
                                                       constant.STATE_NEW: DataModelNewAsyncState(self._model),
                                                       constant.STATE_INIT: DataModelInitiatedAsyncState(self._model),
                                                       constant.STATE_CLEARED: DataModelClearedAsyncState(self._model),
                                                       constant.STATE_SHUTDOWN: DataModelShutdownAsyncState(self._model)
                                                      }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "clear",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_CLEARED
                                                   },
                                                   {
                                                    "trigger": "load",
                                                    "source": constant.STATE_CLEARED,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: AsyncMachine = AsyncMachine(model=self._model,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])
