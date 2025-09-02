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

from datetime import date
from dataclasses import dataclass,                                  \
                        field

from galaxy.utils.type import Id
from galaxy.data.model.company import Employee,                     \
                                      SoftwareVendor
from galaxy.data.model.finance import DataProviderSystem


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
class OSIModelLayer(object):
    """
    classdocs
    """
    id: int
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.id


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
class Protocol(object):
    """
    classdocs
    """
    code: str
    name: str | None = field(init=False, default=None)
    rfc_num: int | None = field(init=False, default=None)
    layer_id: int | None = field(init=False, default=None)
    default_port: int | None = field(init=False, default=None)

    layer: OSIModelLayer | None = field(init=False, default=None)

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
class Environment(object):
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
class HashingAlgorithm(object):
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
class DataProviderServer(object):
    """
    classdocs
    """
    id: Id
    host: str | None = field(init=False, default=None)
    port: int | None = field(init=False, default=None)
    env_code: str | None = field(init=False, default=None)
    protocol_code: str | None = field(init=False, default=None)
    sys_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    env: Environment | None = field(init=False, default=None)
    protocol: Protocol | None = field(init=False, default=None)
    sys: DataProviderSystem | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.id


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
class DataProviderCredential(object):
    """
    classdocs
    """
    id: int
    username: str | None = field(init=False, default=None)
    password: str | None = field(init=False, default=None)
    public_key_file: str | None = field(init=False, default=None)
    private_key_file: str | None = field(init=False, default=None)
    passphrase: str | None = field(init=False, default=None)
    fingerprint: str | None = field(init=False, default=None)
    rsa_key_len: int | None = field(init=False, default=None)
    server_id: Id | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    server: DataProviderServer | None = field(init=False, default=None)

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
class Domain(object):
    """
    classdocs
    """
    id: int
    name: str | None = field(init=False, default=None)
    netbios: str | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

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
class DomainUser(object):
    """
    classdocs
    """
    id: int
    username: str | None = field(init=False, default=None)
    domain_id: int | None = field(init=False, default=None)
    email: str | None = field(init=False, default=None)
    employee_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    domain: Domain | None = field(init=False, default=None)
    employee: Employee | None = field(init=False, default=None)

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
class TradingPlatform(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    vendor_id: int | None = field(init=False, default=None)

    vendor: SoftwareVendor | None = field(init=False, default=None)

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
class TradingServer(object):
    """
    classdocs
    """
    id: Id
    host: str | None = field(init=False, default=None)
    domain_id: int | None = field(init=False, default=None)
    env_code: str | None = field(init=False, default=None)
    platform_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    domain: Domain | None = field(init=False, default=None)
    env: Environment | None = field(init=False, default=None)
    platform: TradingPlatform | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.id
