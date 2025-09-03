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

from datetime import datetime
from dataclasses import dataclass,                          \
                        field

from galaxy.utils.type import Id
from galaxy.data import constant
from galaxy.data.model.model import DataModel,              \
                                    AsyncDataModel
from galaxy.perfo.decorator import timed,                   \
                                   async_timed


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class Extension(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    extension: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class Format(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    is_proprietary: bool | None = field(init=False, default=None)
    create_by: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class Location(object):
    """
    classdocs
    """
    id: Id
    path: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class File(object):
    """
    classdocs
    """
    id: Id
    name: str | None = field(init=False, default=None)
    path_id: Id | None = field(init=False, default=None)
    extension_id: int | None = field(init=False, default=None)
    format_id: int | None = field(init=False, default=None)
    create_date: datetime | None = field(init=False, default=None)
    create_by: str | None = field(init=False, default=None)
    last_modif_date: datetime | None = field(init=False, default=None)
    last_modif_by: str | None = field(init=False, default=None)
    delete_date: datetime | None = field(init=False, default=None)
    delete_by: str | None = field(init=False, default=None)
    is_readable: bool | None = field(init=False, default=None)
    is_writeable: bool | None = field(init=False, default=None)
    is_executable: bool | None = field(init=False, default=None)
    posix_permission: str | None = field(init=False, default=None)

    path: Location | None = field(init=False, default=None)
    extension: Extension | None = field(init=False, default=None)
    format: Format | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class EventLevel(object):
    """
    classdocs
    """
    code: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.code


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class EventGroup(object):
    """
    classdocs
    """
    code: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.code


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class Action(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class Event(object):
    """
    classdocs
    """
    id: Id
    level_code: str | None = field(init=False, default=None)
    group_code: str | None = field(init=False, default=None)
    action_id: int | None = field(init=False, default=None)
    msg: str | None = field(init=False, default=None)
    source: str | None = field(init=False, default=None)
    create_date: datetime | None = field(init=False, default=None)
    create_by: str | None = field(init=False, default=None)

    level: EventLevel | None = field(init=False, default=None)
    group: EventGroup | None = field(init=False, default=None)
    action: Action | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


class FileDataModel(DataModel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FileDataModel, self).__init__()
        self.extensions: dict[int, Extension] | None = None
        self.formats: dict[int, Format] | None = None
        self.locations: dict[Id, Location] | None = None
        self.files: dict[Id, File] | None = None
        self.event_levels: dict[str, EventLevel] | None = None
        self.event_groups: dict[str, EventGroup] | None = None
        self.actions: dict[int, Action] | None = None
        self.events: dict[Id, Event] | None = None

    @timed
    def _load(self) -> None:
        super(FileDataModel, self)._load()
        if self.daos is not None:
            self.extensions = self.daos["extension"].get()
            self.formats = self.daos["format"].get()
            self.locations = self.daos["location"].get()
            self.files = self.daos["file"].get()
            self.event_levels = self.daos["event_level"].get()
            self.event_groups = self.daos["event_group"].get()
            self.actions = self.daos["action"].get()
            self.events = self.daos["event"].get()
            self._init_data()

    def _init_data(self):
        for file in list(self.files.values()):
            file.path = self.locations[file.path_id]


    def update_locations(self, locations: list[Location]) -> dict[str, list]:
        res = {constant.DB_OPE_CREATE: [],
               constant.DB_OPE_UPDATE: [],
               constant.DB_OPE_DELETE: []}

        for location in locations:
            if location.id not in self.locations:
                res[constant.DB_OPE_CREATE].append(location)
            self.locations[location.id] = location

        return res

    def update_files(self, files: list[File]) -> dict[str, list]:
        res = {constant.DB_OPE_CREATE: [],
               constant.DB_OPE_UPDATE: [],
               constant.DB_OPE_DELETE: []}

        for file in files:
            if file.id in self.files:
                res[constant.DB_OPE_UPDATE].append(file)
            else:
                res[constant.DB_OPE_CREATE].append(file)
            self.files[file.id] = file

        return res

    def update_events(self, events: list[Event]) -> dict[str, list]:
        res = {constant.DB_OPE_CREATE: [],
               constant.DB_OPE_UPDATE: [],
               constant.DB_OPE_DELETE: []}

        for event in events:
            if event.id not in self.events:
                res[constant.DB_OPE_CREATE].append(event)
            self.events[event.id] = event

        return res

    @timed
    def _clear(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<FileDataModel(id='{}')>".format(self.id)


class FileAsyncDataModel(AsyncDataModel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FileAsyncDataModel, self).__init__()
        self.extensions: dict[int, Extension] | None = None
        self.formats: dict[int, Format] | None = None
        self.locations: dict[Id, Location] | None = None
        self.files: dict[Id, File] | None = None
        self.event_levels: dict[str, EventLevel] | None = None
        self.event_groups: dict[str, EventGroup] | None = None
        self.actions: dict[int, Action] | None = None
        self.events: dict[Id, Event] | None = None

    @async_timed
    async def _load(self) -> None:
        await super(FileAsyncDataModel, self)._load()
        if self.daos is not None:
            self.extensions = await self.daos["extension"].get()
            self.formats = await self.daos["format"].get()
            self.locations = await self.daos["location"].get()
            self.files = await self.daos["file"].get()
            self.event_levels = await self.daos["event_level"].get()
            self.event_groups = await self.daos["event_group"].get()
            self.actions = await self.daos["action"].get()
            self.events = await self.daos["event"].get()
            self._init_data()

    def _init_data(self):
        for file in list(self.files.values()):
            file.path = self.locations[file.path_id]

    def update_locations(self, locations: list[Location]) -> dict[str, list]:
        res = {constant.DB_OPE_CREATE: [],
               constant.DB_OPE_UPDATE: [],
               constant.DB_OPE_DELETE: []}

        for location in locations:
            if location.id not in self.locations:
                res[constant.DB_OPE_CREATE].append(location)
            self.locations[location.id] = location

        return res

    def update_files(self, files: list[File]) -> dict[str, list]:
        res = {constant.DB_OPE_CREATE: [],
               constant.DB_OPE_UPDATE: [],
               constant.DB_OPE_DELETE: []}

        for file in files:
            if file.id in self.files:
                res[constant.DB_OPE_UPDATE].append(file)
            else:
                res[constant.DB_OPE_CREATE].append(file)
            self.files[file.id] = file

        return res

    def update_events(self, events: list[Event]) -> dict[str, list]:
        res = {constant.DB_OPE_CREATE: [],
               constant.DB_OPE_UPDATE: [],
               constant.DB_OPE_DELETE: []}

        for event in events:
            if event.id not in self.events:
                res[constant.DB_OPE_CREATE].append(event)
            self.events[event.id] = event

        return res

    @async_timed
    def _clear(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<FileAsyncDataModel(id='{}')>".format(self.id)
