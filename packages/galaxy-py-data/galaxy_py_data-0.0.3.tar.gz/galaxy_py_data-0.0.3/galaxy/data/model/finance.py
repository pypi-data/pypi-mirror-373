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

from datetime import date,                                          \
                     datetime
from dataclasses import dataclass,                                  \
                        field
from typing import Optional

from galaxy.utils.type import Id
from galaxy.data.model.iso import Country,                          \
                                  Currency,                         \
                                  MarketExchange
from galaxy.data.model.institution import Bank,                     \
                                          RegulatoryAuthority
from galaxy.data.model.company import Company,                      \
                                      SoftwareVendor,               \
                                      DataVendor


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
class ExerciseStyle(object):
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
class OptionType(object):
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
class ExpirationType(object):
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
class PayoffType(object):
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
class DeliveryType(object):
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
class DeliveryMonth(object):
    """
    classdocs
    """
    code: str
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)

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
class InstrumentClass(object):
    """
    classdocs
    """
    code: str
    cfi: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    derivative: bool | None = field(init=False, default=None)

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
class IssuerType(object):
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
class STIRColor(object):
    """
    classdocs
    """
    id: int
    year_nb: int | None = field(init=False, default=None)
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
class ProductFamily(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    clearing_name: str | None = field(init=False, default=None)

    products: dict[int, "Product"] = field(init=False, default_factory=dict)
    stir_groups: dict[int, "STIRProductGroup"] = field(init=False, default_factory=dict)

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
class STIRProductGroup(object):
    """
    classdocs
    """
    id: int
    name: str | None = field(init=False, default=None)
    trading_name: str | None = field(init=False, default=None)
    color_id: int | None = field(init=False, default=None)
    class_code: str | None = field(init=False, default=None)
    family_id: int | None = field(init=False, default=None)
    expiration_code: str | None = field(init=False, default=None)
    nb_expiration: int | None = field(init=False, default=None)

    color: STIRColor | None = field(init=False, default=None)
    instrument_class: InstrumentClass | None = field(init=False, default=None)
    family: ProductFamily | None = field(init=False, default=None)
    expiration: ExpirationType | None = field(init=False, default=None)
    series: dict[Id, "ProductSerie"] = field(init=False, default_factory=dict)

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
class Product(object):
    """
    classdocs
    """
    id: int
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    nickname: str | None = field(init=False, default=None)
    cfi: str | None = field(init=False, default=None)
    isin: str | None = field(init=False, default=None)
    cusip: str | None = field(init=False, default=None)
    nsin: str | None = field(init=False, default=None)
    sedol: str | None = field(init=False, default=None)
    ric: str | None = field(init=False, default=None)
    symbol: str | None = field(init=False, default=None)
    class_code: str | None = field(init=False, default=None)
    family_id: int | None = field(init=False, default=None)
    parent_id: int | None = field(init=False, default=None)
    underlying_id: int | None = field(init=False, default=None)
    currency_iso3: str | None = field(init=False, default=None)
    exercise_code: str | None = field(init=False, default=None)
    payoff_code: str | None = field(init=False, default=None)
    delivery_code: str | None = field(init=False, default=None)
    contract_size: float | None = field(init=False, default=None)
    coupon_rate: float | None = field(init=False, default=None)
    notional_value: int | None = field(init=False, default=None)
    tick_size: float | None = field(init=False, default=None)
    tick_value: float | None = field(init=False, default=None)
    max_price: float | None = field(init=False, default=None)
    quote_min_quantity: float | None = field(init=False, default=None)
    max_order_quantity: float | None = field(init=False, default=None)
    max_tes_quantity: float | None = field(init=False, default=None)
    max_future_spread_quantity: int | None = field(init=False, default=None)
    max_market_order_quantity: int | None = field(init=False, default=None)
    position_limit: int | None = field(init=False, default=None)

    instrument_class: InstrumentClass | None = field(init=False, default=None)
    family: ProductFamily | None = field(init=False, default=None)
    parent: Optional["Product"] = field(init=False, default=None)
    underlying: Optional["Product"] = field(init=False, default=None)
    currency: Currency | None = field(init=False, default=None)
    exercise: ExerciseStyle | None = field(init=False, default=None)
    payoff: PayoffType | None = field(init=False, default=None)
    delivery: DeliveryType | None = field(init=False, default=None)
    children: dict[int, "Product"] = field(init=False, default_factory=dict)
    derivatives: dict[int, "Product"] = field(init=False, default_factory=dict)
    series: dict[int, "ProductSerie"] = field(init=False, default_factory=dict)

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
class ProductSerie(object):
    """
    classdocs
    """
    id: Id
    name: str | None = field(init=False, default=None)
    product_id: int | None = field(init=False, default=None)
    class_code: str | None = field(init=False, default=None)
    underlying_id: Id | None = field(init=False, default=None)
    expiration_date: datetime | None = field(init=False, default=None)
    expiration_month: date | None = field(init=False, default=None)
    delivery_date: date | None = field(init=False, default=None)
    last_trading_date: datetime | None = field(init=False, default=None)
    stir_group_id: int | None = field(init=False, default=None)
    exercise_code: str | None = field(init=False, default=None)

    product: Product | None = field(init=False, default=None)
    instrument_class: str | None = field(init=False, default=None)
    underlying: Optional["ProductSerie"] = field(init=False, default=None)
    stir_group: STIRProductGroup | None = field(init=False, default=None)
    exercise: ExerciseStyle | None = field(init=False, default=None)
    derivatives: dict[Id, "ProductSerie"] = field(init=False, default_factory=dict)
    instruments: dict[Id, "Instrument"] = field(init=False, default_factory=dict)

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
class Issuer(object):
    """
    classdocs
    """
    id: int
    type_code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)

    type: IssuerType | None = field(init=False, default=None)
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
class Instrument(object):
    """
    classdocs
    """
    id: Id
    class_code: str | None = field(init=False, default=None)
    exchange_mic: str | None = field(init=False, default=None)
    cfi: str | None = field(init=False, default=None)
    isin: str | None = field(init=False, default=None)
    cusip: str | None = field(init=False, default=None)
    nsin: str | None = field(init=False, default=None)
    sedol: str | None = field(init=False, default=None)
    ric: str | None = field(init=False, default=None)
    symbol: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    product_id: int | None = field(init=False, default=None)
    serie_id: Id | None = field(init=False, default=None)
    currency_iso3: str | None = field(init=False, default=None)
    issuer_id: int | None = field(init=False, default=None)
    underlying_id: Id | None = field(init=False, default=None)
    expiration_date: datetime | None = field(init=False, default=None)
    delivery_date: date | None = field(init=False, default=None)
    maturity_date: date | None = field(init=False, default=None)
    strike_price: float | None = field(init=False, default=None)
    option_type_code: str | None = field(init=False, default=None)

    instrument_class: InstrumentClass | None = field(init=False, default=None)
    exchange: MarketExchange | None = field(init=False, default=None)
    product: Product | None = field(init=False, default=None)
    serie: ProductSerie | None = field(init=False, default=None)
    currency: Currency | None = field(init=False, default=None)
    issuer: Issuer | None = field(init=False, default=None)
    underlying: Optional["Instrument"] = field(init=False, default=None)
    option_type: OptionType | None = field(init=False, default=None)
    # Use default_factory for mutable default
    derivatives: dict[Id, "Instrument"] = field(init=False, default_factory=dict)

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
class Straddle(object):
    """
    classdocs
    """
    id: Id
    call_id: Id | None = field(init=False, default=None)
    put_id: Id | None = field(init=False, default=None)
    exchange_mic: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    serie_id: Id | None = field(init=False, default=None)
    currency_iso3: str | None = field(init=False, default=None)
    underlying_id: Id | None = field(init=False, default=None)
    expiration_date: datetime | None = field(init=False, default=None)
    delivery_date: date | None = field(init=False, default=None)
    maturity_date: date | None = field(init=False, default=None)
    strike_price: float | None = field(init=False, default=None)

    call: Instrument | None = field(init=False, default=None)
    put: Instrument | None = field(init=False, default=None)
    exchange: MarketExchange | None = field(init=False, default=None)
    serie: ProductSerie | None = field(init=False, default=None)
    currency: Currency | None = field(init=False, default=None)
    underlying: Instrument | None = field(init=False, default=None)

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
class StrategyType(object):
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
class Strategy(object):
    """
    classdocs
    """
    id: Id
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)
    strategy_type_code: str | None = field(init=False, default=None)

    strategy_type: StrategyType | None = field(init=False, default=None)

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
class StrategyInstrument(object):
    """
    classdocs
    """
    id: Id
    strategy_id: Id | None = field(init=False, default=None)
    instrument_id: Id | None = field(init=False, default=None)
    quantity: int | None = field(init=False, default=None)

    strategy: Strategy | None = field(init=False, default=None)
    instrument: Instrument | None = field(init=False, default=None)

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
class DataProvider(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    exchange_mic: str | None = field(init=False, default=None)
    bank_id: int | None = field(init=False, default=None)
    software_vendor_id: int | None = field(init=False, default=None)
    data_vendor_id: int | None = field(init=False, default=None)
    authority_code: str | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    exchange: MarketExchange | None = field(init=False, default=None)
    bank: Bank | None = field(init=False, default=None)
    software_vendor: SoftwareVendor | None = field(init=False, default=None)
    data_vendor: DataVendor | None = field(init=False, default=None)
    reg_authority: RegulatoryAuthority | None = field(init=False, default=None)

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
class DataProviderSystem(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    account_id: str | None = field(init=False, default=None)
    company_id: int | None = field(init=False, default=None)
    provider_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company | None = field(init=False, default=None)
    provider: DataProvider | None = field(init=False, default=None)

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
class InstrumentClassMap(object):
    """
    classdocs
    """
    class_code: str
    provider_id: int
    id: str | None = field(init=False, default=None)

    instrument_class: InstrumentClass | None = field(init=False, default=None)
    provider: DataProvider | None = field(init=False, default=None)

    def __str__(self) -> str:
        return "{}_{}".format(self.class_code, self.provider_id)


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
class ProductMap(object):
    """
    classdocs
    """
    product_id: int
    provider_id: int
    id: str | None = field(init=False, default=None)

    product: Product | None = field(init=False, default=None)
    provider: DataProvider | None = field(init=False, default=None)

    def __str__(self) -> str:
        return "{}_{}".format(self.product_id, self.provider_id)


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
class ProductSerieMap(object):
    """
    classdocs
    """
    serie_id: Id
    provider_id: int
    id: str | None = field(init=False, default=None)

    serie: ProductSerie | None = field(init=False, default=None)
    provider: DataProvider | None = field(init=False, default=None)

    def __str__(self) -> str:
        return "{}_{}".format(self.serie_id, self.provider_id)


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
class InstrumentMap(object):
    """
    classdocs
    """
    instrument_id: Id
    provider_id: int
    id: str | None = field(init=False, default=None)

    instrument: Instrument | None = field(init=False, default=None)
    provider: DataProvider | None = field(init=False, default=None)

    def __str__(self) -> str:
        return "{}_{}".format(self.instrument_id, self.provider_id)


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
class StrategyMap(object):
    """
    classdocs
    """
    strategy_id: Id
    provider_id: int
    id: str | None = field(init=False, default=None)

    strategy: Strategy | None = field(init=False, default=None)
    provider: DataProvider | None = field(init=False, default=None)

    def __str__(self) -> str:
        return "{}_{}".format(self.strategy_id, self.provider_id)
