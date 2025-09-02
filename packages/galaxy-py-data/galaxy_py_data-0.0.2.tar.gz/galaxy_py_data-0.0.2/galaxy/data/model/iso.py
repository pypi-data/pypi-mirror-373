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
from dataclasses import dataclass,                          \
                        field

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
class Continent(object):
    """
    classdocs
    """
    iso2: str
    name: str | None = field(init=False, default=None)

    countries: dict[str, "Country"] = field(init=False, default_factory=dict)

    def __str__(self) -> str:
        return self.iso2


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
class Country(object):
    """
    classdocs
    """
    iso2: str
    iso3: str | None = field(init=False, default=None)
    iso_code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    iso_name: str | None = field(init=False, default=None)
    in_oecd: bool | None = field(init=False, default=None)

    continents: dict[str, Continent] = field(init=False, default_factory=dict)
    currencies: dict[str, "Currency"] = field(init=False, default_factory=dict)
    phone_prefixes: dict[int, "PhonePrefix"] = field(init=False, default_factory=dict)

    def __str__(self) -> str:
        return self.iso2


@dataclass(init=True,
           repr=True,
           eq=False,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class CountryContinent(object):
    """
    classdocs
    """
    id: int
    country_iso2: str | None = field(init=False, default=None)
    continent_iso2: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)
    continent: Continent | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)

    def __eq__(self, other: "CountryContinent") -> bool:
        return self.country_iso2 == other.country_iso2 and \
               self.continent_iso2 == other.continent_iso2

    def __ne__(self, other: "CountryContinent") -> bool:
        return self.country_iso2 != other.country_iso2 or \
               self.continent_iso2 != other.continent_iso2


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
class CurrencyType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class Currency(object):
    """
    classdocs
    """
    iso3: str
    iso_code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    symbol: str | None = field(init=False, default=None)
    cfi: str | None = field(init=False, default=None)

    countries: dict[str, Country] = field(init=False, default_factory=dict)

    def __str__(self) -> str:
        return self.iso3


@dataclass(init=True,
           repr=True,
           eq=False,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class CountryCurrency(object):
    """
    classdocs
    """
    id: int
    country_iso2: str | None = field(init=False, default=None)
    currency_iso3: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)
    currency: Currency | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)

    def __eq__(self, other: "CountryCurrency") -> bool:
        return self.country_iso2 == other.country_iso2 and self.currency_iso3 == other.currency_iso3

    def __ne__(self, other: "CountryCurrency") -> bool:
        return self.country_iso2 != other.country_iso2 or self.currency_iso3 != other.currency_iso3


@dataclass(init=True,
           repr=True,
           eq=False,
           order=False,
           unsafe_hash=False,
           frozen=False,
           match_args=True,
           kw_only=False,
           slots=True,
           weakref_slot=False)
class PhonePrefix(object):
    """
    classdocs
    """
    id: int
    prefix: int | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.prefix

    def __eq__(self, other: "PhonePrefix") -> bool:
        return self.prefix == other.prefix and self.country_iso2 == other.country_iso2

    def __ne__(self, other: "PhonePrefix") -> bool:
        return self.prefix != other.prefix or self.country_iso2 != other.country_iso2


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
class Language(object):
    """
    classdocs
    """
    iso3: str
    iso2: str | None = field(init=False, default=None)
    iso639_3: str | None = field(init=False, default=None)
    iso639_3_other: str | None = field(init=False, default=None)
    iso639_1: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    scope_code: str | None = field(init=False, default=None)
    type_code: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.iso3


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
class MarketExchange(object):
    """
    classdocs
    """
    mic: str
    operating_mic: str | None = field(init=False, default=None)
    lei: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    acronym: str | None = field(init=False, default=None)
    city: str | None = field(init=False, default=None)
    website: str | None = field(init=False, default=None)
    open_date: date | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.mic


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
class InstrumentCategory(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)

    groups: dict[str, "InstrumentGroup"] = field(init=False, default_factory=dict)

    def __str__(self) -> str:
        return self.cfi

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
class InstrumentGroup(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    category_cfi: str | None = field(init=False, default=None)

    category: InstrumentCategory | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class VotingRight(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class InstrumentOwnership(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class PaymentStatus(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class IncomeType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class RedemptionConversionType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class DistributionType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class DistributionPolicy(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class ClosedOpenEnd(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class GuaranteeType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class InterestType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class RedemptionReimbursementType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class SecurityType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class OptionType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class WarrantType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class Termination(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class DeliveryType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class WeightingType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class IndexReturnType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class BasketComposition(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class TimeFrequency(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


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
class EquityType(object):
    """
    classdocs
    """
    cfi: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.cfi


class ISODataModel(DataModel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ISODataModel, self).__init__()
        self.continents: dict[str, Continent] | None = None
        self.countries: dict[str, Country] | None = None
        self.country_continents: dict[int, CountryContinent] | None = None
        self.currencies: dict[str, Currency] | None = None
        self.country_currencies: dict[int, CountryCurrency] | None = None
        self.phone_prefixes: dict[int, PhonePrefix] | None = None
        self.languages: dict[str, Language] | None = None
        self.market_exchanges: dict[str, MarketExchange] | None = None
        self.instrument_categories: dict[str, InstrumentCategory] | None = None
        self.instrument_groups: dict[str, InstrumentGroup] | None = None
        self.voting_rights: dict[str, VotingRight] | None = None
        self.instrument_ownerships: dict[str, InstrumentOwnership] | None = None
        self.payment_statuses: dict[str, PaymentStatus] | None = None
        self.income_types: dict[str, IncomeType] | None = None
        self.redemption_conversion_types: dict[str, RedemptionConversionType] | None = None
        self.distribution_types: dict[str, DistributionType] | None = None
        self.distribution_policies: dict[str, DistributionPolicy] | None = None
        self.closed_open_ends: dict[str, ClosedOpenEnd] | None = None
        self.guarantee_types: dict[str, GuaranteeType] | None = None
        self.interest_types: dict[str, InterestType] | None = None
        self.redemption_reimbursement_types: dict[str, RedemptionReimbursementType] | None = None
        self.security_types: dict[str, SecurityType] | None = None
        self.option_types: dict[str, OptionType] | None = None
        self.warrant_types: dict[str, WarrantType] | None = None
        self.terminations: dict[str, Termination] | None = None
        self.delivery_types: dict[str, DeliveryType] | None = None
        self.weighting_types: dict[str, WeightingType] | None = None
        self.index_return_types: dict[str, IndexReturnType] | None = None
        self.basket_compositions: dict[str, BasketComposition] | None = None
        self.time_frequencies: dict[str, TimeFrequency] | None = None
        self.equity_types: dict[str, EquityType] | None = None

    @timed
    def _load(self) -> None:
        super(ISODataModel, self)._load()
        if self.daos is not None:
            self.continents = self.daos["continent"].get()
            self.countries = self.daos["country"].get()
            self.country_continents = self.daos["country_continent"].get()
            self.currencies = self.daos["currency"].get()
            self.country_currencies = self.daos["country_currency"].get()
            self.phone_prefixes = self.daos["phone_prefix"].get()
            self.languages = self.daos["language"].get()
            self.market_exchanges = self.daos["market_exchange"].get()
            self.instrument_categories = self.daos["instrument_category"].get()
            self.instrument_groups = self.daos["instrument_group"].get()
            self.voting_rights = self.daos["voting_right"].get()
            self.instrument_ownerships = self.daos["market_exchange"].get()
            self.payment_statuses = self.daos["payment_status"].get()
            self.income_types = self.daos["income_type"].get()
            self.redemption_conversion_types = self.daos["redemption_conversion_type"].get()
            self.distribution_types = self.daos["distribution_type"].get()
            self.distribution_policies = self.daos["distribution_policy"].get()
            self.closed_open_ends = self.daos["closed_open_end"].get()
            self.guarantee_types = self.daos["guarantee_type"].get()
            self.interest_types = self.daos["interest_type"].get()
            self.redemption_reimbursement_types = self.daos["redemption_reimbursement_type"].get()
            self.security_types = self.daos["security_type"].get()
            self.option_types = self.daos["option_type"].get()
            self.warrant_types = self.daos["warrant_type"].get()
            self.terminations = self.daos["termination"].get()
            self.delivery_types = self.daos["delivery_type"].get()
            self.weighting_types = self.daos["weighting_type"].get()
            self.index_return_types = self.daos["index_return_type"].get()
            self.basket_compositions = self.daos["basket_composition"].get()
            self.time_frequencies = self.daos["time_frequency"].get()
            self.equity_types = self.daos["equity_type"].get()

    @timed
    def _clear(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<ISODataModel(id='{}')>".format(self.id)


class ISOAsyncDataModel(AsyncDataModel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ISOAsyncDataModel, self).__init__()
        self.continents: dict[str, Continent] | None = None
        self.countries: dict[str, Country] | None = None
        self.country_continents: dict[int, CountryContinent] | None = None
        self.currencies: dict[str, Currency] | None = None
        self.country_currencies: dict[int, CountryCurrency] | None = None
        self.phone_prefixes: dict[int, PhonePrefix] | None = None
        self.languages: dict[str, Language] | None = None
        self.market_exchanges: dict[str, MarketExchange] | None = None
        self.instrument_categories: dict[str, InstrumentCategory] | None = None
        self.instrument_groups: dict[str, InstrumentGroup] | None = None
        self.voting_rights: dict[str, VotingRight] | None = None
        self.instrument_ownerships: dict[str, InstrumentOwnership] | None = None
        self.payment_statuses: dict[str, PaymentStatus] | None = None
        self.income_types: dict[str, IncomeType] | None = None
        self.redemption_conversion_types: dict[str, RedemptionConversionType] | None = None
        self.distribution_types: dict[str, DistributionType] | None = None
        self.distribution_policies: dict[str, DistributionPolicy] | None = None
        self.closed_open_ends: dict[str, ClosedOpenEnd] | None = None
        self.guarantee_types: dict[str, GuaranteeType] | None = None
        self.interest_types: dict[str, InterestType] | None = None
        self.redemption_reimbursement_types: dict[str, RedemptionReimbursementType] | None = None
        self.security_types: dict[str, SecurityType] | None = None
        self.option_types: dict[str, OptionType] | None = None
        self.warrant_types: dict[str, WarrantType] | None = None
        self.terminations: dict[str, Termination] | None = None
        self.delivery_types: dict[str, DeliveryType] | None = None
        self.weighting_types: dict[str, WeightingType] | None = None
        self.index_return_types: dict[str, IndexReturnType] | None = None
        self.basket_compositions: dict[str, BasketComposition] | None = None
        self.time_frequencies: dict[str, TimeFrequency] | None = None
        self.equity_types: dict[str, EquityType] | None = None

    @async_timed
    async def _load(self) -> None:
        await super(ISOAsyncDataModel, self)._load()
        if self.daos is not None:
            self.continents = await self.daos["continent"].get()
            self.countries = await self.daos["country"].get()
            self.country_continents = await self.daos["country_continent"].get()
            self.currencies = await self.daos["currency"].get()
            self.country_currencies = await self.daos["country_currency"].get()
            self.phone_prefixes = await self.daos["phone_prefix"].get()
            self.languages = await self.daos["language"].get()
            self.market_exchanges = await self.daos["market_exchange"].get()
            self.instrument_categories = await self.daos["instrument_category"].get()
            self.instrument_groups = await self.daos["instrument_group"].get()
            self.voting_rights = await self.daos["voting_right"].get()
            self.instrument_ownerships = await self.daos["market_exchange"].get()
            self.payment_statuses = await self.daos["payment_status"].get()
            self.income_types = await self.daos["income_type"].get()
            self.redemption_conversion_types = await self.daos["redemption_conversion_type"].get()
            self.distribution_types = await self.daos["distribution_type"].get()
            self.distribution_policies = await self.daos["distribution_policy"].get()
            self.closed_open_ends = await self.daos["closed_open_end"].get()
            self.guarantee_types = await self.daos["guarantee_type"].get()
            self.interest_types = await self.daos["interest_type"].get()
            self.redemption_reimbursement_types = await self.daos["redemption_reimbursement_type"].get()
            self.security_types = await self.daos["security_type"].get()
            self.option_types = await self.daos["option_type"].get()
            self.warrant_types = await self.daos["warrant_type"].get()
            self.terminations = await self.daos["termination"].get()
            self.delivery_types = await self.daos["delivery_type"].get()
            self.weighting_types = await self.daos["weighting_type"].get()
            self.index_return_types = await self.daos["index_return_type"].get()
            self.basket_compositions = await self.daos["basket_composition"].get()
            self.time_frequencies = await self.daos["time_frequency"].get()
            self.equity_types = await self.daos["equity_type"].get()
            self._init_data()

    def _init_data(self):
        pass

    def _init_countries(self):
        pass

    @async_timed
    def _clear(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<ISOAsyncDataModel(id='{}')>".format(self.id)
