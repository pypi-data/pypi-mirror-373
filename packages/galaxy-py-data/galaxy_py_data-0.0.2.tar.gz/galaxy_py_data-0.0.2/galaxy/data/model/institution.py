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

from dataclasses import dataclass,                      \
                        field

from galaxy.data.model.model import DataModel,          \
                                    AsyncDataModel
from galaxy.data.model.iso import Country,              \
                                  Currency,             \
                                  PhonePrefix
from galaxy.perfo.decorator import timed,               \
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
class Bank(object):
    """
    classdocs
    """
    id: int
    bic: str | None = field(init=False, default=None)
    code: str | None = field(init=False, default=None)
    sort_code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    building: str | None = field(init=False, default=None)
    street_num: str | None = field(init=False, default=None)
    street: str | None = field(init=False, default=None)
    address1: str | None = field(init=False, default=None)
    address2: str | None = field(init=False, default=None)
    address3: str | None = field(init=False, default=None)
    zip_code: str | None = field(init=False, default=None)
    city: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    phone: str | None = field(init=False, default=None)
    phone_prefix_id: int | None = field(init=False, default=None)
    fax: str | None = field(init=False, default=None)
    fax_prefix_id: int | None = field(init=False, default=None)
    website: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)
    phone_prefix: PhonePrefix | None = field(init=False, default=None)
    fax_prefix: PhonePrefix | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.name


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
class BrokerGroup(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    bank_id: int | None = field(init=False, default=None)
    lei: str | None = field(init=False, default=None)

    bank: Bank | None = field(init=False, default=None)

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
class Broker(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    group_id: int | None = field(init=False, default=None)
    lei: str | None = field(init=False, default=None)

    group: BrokerGroup | None = field(init=False, default=None)

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
class RegulatoryAuthority(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    website: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)

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
class CentralBank(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    bank_id: int | None = field(init=False, default=None)
    currency_iso3: str | None = field(init=False, default=None)
    website: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)
    bank: Bank | None = field(init=False, default=None)
    currency: Currency | None = field(init=False, default=None)

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
class CentralSecuritiesDepository(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    bank_id: int | None = field(init=False, default=None)
    website: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)
    bank: Bank | None = field(init=False, default=None)

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
class Subcustodian(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    bank_id: int | None = field(init=False, default=None)
    website: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)
    bank: Bank | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.code


class InstitutionDataModel(DataModel):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(InstitutionDataModel, self).__init__()
        self.banks: dict[int, Bank] | None = None
        self.broker_groups: dict[int, BrokerGroup] | None = None
        self.brokers: dict[int, Broker] | None = None
        self.regulatory_authorities: dict[str, RegulatoryAuthority] | None = None
        self.central_banks: dict[int, CentralBank] | None = None
        self.csds: dict[int, CentralSecuritiesDepository] | None = None
        self.subcustodians: dict[int, Subcustodian] | None = None

    @timed
    def _load(self) -> None:
        super(InstitutionDataModel, self)._load()
        if self.daos is not None:
            self.banks = self.daos["bank"].get()
            self.broker_groups = self.daos["broker_group"].get()
            self.brokers = self.daos["broker"].get()
            self.regulatory_authorities = self.daos["regulatory_authority"].get()
            self.central_banks = self.daos["central_bank"].get()
            self.csds = self.daos["csd"].get()
            self.subcustodians = self.daos["subcustodian"].get()

    @timed
    def _clear(self) -> None:
        pass

    def __repr__(self):
        return "<InstitutionDataModel(id='{}')>".format(self.id)


class InstitutionAsyncDataModel(AsyncDataModel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InstitutionAsyncDataModel, self).__init__()
        self.banks: dict[int, Bank] | None = None
        self.broker_groups: dict[int, BrokerGroup] | None = None
        self.brokers: dict[int, Broker] | None = None
        self.regulatory_authorities: dict[str, RegulatoryAuthority] | None = None
        self.central_banks: dict[int, CentralBank] | None = None
        self.csds: dict[int, CentralSecuritiesDepository] | None = None
        self.subcustodians: dict[int, Subcustodian] | None = None

    @async_timed
    async def _load(self) -> None:
        await super(InstitutionAsyncDataModel, self)._load()
        if self.daos is not None:
            self.banks = await self.daos["bank"].get()
            self.broker_groups = await self.daos["broker_group"].get()
            self.brokers = await self.daos["broker"].get()
            self.regulatory_authorities = await self.daos["regulatory_authority"].get()
            self.central_banks = await self.daos["central_bank"].get()
            self.csds = await self.daos["csd"].get()
            self.subcustodians = await self.daos["subcustodian"].get()

    @async_timed
    def _clear(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<InstitutionAsyncDataModel(id='{}')>".format(self.id)
