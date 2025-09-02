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
class Message(object):
    """
    classdocs
    """
    id: Id
    create_date: datetime | None = field(init=False, default=None)
    create_by: Id | None = field(init=False, default=None)
    send_date: datetime | None = field(init=False, default=None)
    send_by: Id | None = field(init=False, default=None)
    payload: list | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)
