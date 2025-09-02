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
from typing import Any
from dataclasses import dataclass,          \
                        field

from galaxy.utils.type import Id


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
class CommandRequest(object):
    """
    classdocs
    """
    id: Id
    cmd_name: str | None = field(init=False, default=None)
    cmd_args: list | None = field(init=False, default=None)
    req_date: datetime | None = field(init=False, default=None)
    req_by: Id | None = field(init=False, default=None)

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
class CommandResponse(object):
    """
    classdocs
    """
    id: Id
    req_id: Id | None = field(init=False, default=None)
    rep_date: datetime | None = field(init=False, default=None)
    rep_by: str | None = field(init=False, default=None)
    code: int | None = field(init=False, default=None)
    msg: str | None = field(init=False, default=None)
    result: Any | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)
