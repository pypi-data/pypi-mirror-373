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

from abc import ABC
from sqlalchemy.sql.schema import Table,                            \
                                  Column,                           \
                                  UniqueConstraint,                 \
                                  PrimaryKeyConstraint,             \
                                  ForeignKeyConstraint,             \
                                  Index
from sqlalchemy.sql.expression import select,                       \
                                      delete,                       \
                                      insert,                       \
                                      update
from sqlalchemy.sql.sqltypes import String,                         \
                                    Integer,                        \
                                    Boolean,                        \
                                    Date
from sqlalchemy.sql import bindparam

from galaxy.data.db.db import DAO,                                  \
                              SQLAlchemyDAO,                        \
                              AsyncDAO,                             \
                              SQLAlchemyAsyncDAO
from galaxy.data.model.iso import Continent,                        \
                                  Country,                          \
                                  CountryContinent,                 \
                                  CurrencyType,                     \
                                  Currency,                         \
                                  CountryCurrency,                  \
                                  PhonePrefix,                      \
                                  Language,                         \
                                  MarketExchange,                   \
                                  InstrumentCategory,               \
                                  InstrumentGroup,                  \
                                  VotingRight,                      \
                                  InstrumentOwnership,              \
                                  PaymentStatus,                    \
                                  IncomeType,                       \
                                  RedemptionConversionType,         \
                                  DistributionType,                 \
                                  DistributionPolicy,               \
                                  ClosedOpenEnd,                    \
                                  GuaranteeType,                    \
                                  InterestType,                     \
                                  RedemptionReimbursementType,      \
                                  SecurityType,                     \
                                  OptionType,                       \
                                  WarrantType,                      \
                                  Termination,                      \
                                  DeliveryType,                     \
                                  WeightingType,                    \
                                  IndexReturnType,                  \
                                  BasketComposition,                \
                                  TimeFrequency,                    \
                                  EquityType
from galaxy.perfo.decorator import timed,                           \
                                   async_timed


class ContinentDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ContinentDAO, self).__init__()


class SQlAlchemyContinentDAO(ContinentDAO, SQLAlchemyDAO):
    """
    classdocs
    """
    
    def __init__(self) -> None:
        """
        Constructor
        """
        ContinentDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)
    
    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("continent"),
                                   self._metadata,
                                   Column(self.get_column_name("iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("iso2"), name=self.get_key_name("continent_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, iso2: str | None = None) -> Continent | dict[str, Continent] | None:
        if iso2 is None:
            continents = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                continent = Continent(getattr(row, self.get_column_name("iso2")))
                continent.name = getattr(row, self.get_column_name("name"))
                continents[continent.iso2] = continent
            return continents
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == iso2)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            continent = None
            if row is not None:
                continent = Continent(getattr(row, self.get_column_name("iso2")))
                continent.name = getattr(row, self.get_column_name("name"))
            return continent

    @timed
    def create(self, continents: list[Continent]) -> None:
        if len(continents) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso2"): continent.iso2,
                                                self.get_column_name("name"): continent.name
                                               } for continent in continents])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, continents: list[Continent]) -> None:
        if len(continents) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == bindparam("iso2")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "iso2": continent.iso2,
                                     "name": continent.name
                                    } for continent in continents])

    @timed
    def delete(self, continents: list[Continent]) -> None:
        if len(continents) > 0:
            iso2 = [con.iso2 for con in continents]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso2")).in_(iso2))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class ContinentAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ContinentAsyncDAO, self).__init__()


class SQlAlchemyContinentAsyncDAO(ContinentAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        ContinentAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("continent"),
                                   self._metadata,
                                   Column(self.get_column_name("iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("iso2"), name=self.get_key_name("continent_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, iso2: str | None = None) -> Continent | dict[str, Continent] | None:
        if iso2 is None:
            continents = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                continent = Continent(getattr(row, self.get_column_name("iso2")))
                continent.name = getattr(row, self.get_column_name("name"))
                continents[continent.iso2] = continent
            return continents
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == iso2)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            continent = None
            if row is not None:
                continent = Continent(getattr(row, self.get_column_name("iso2")))
                continent.name = getattr(row, self.get_column_name("name"))
            return continent

    @async_timed
    async def create(self, continents: list[Continent]) -> None:
        if len(continents) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso2"): continent.iso2,
                                                self.get_column_name("name"): continent.name
                                               } for continent in continents])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, continents: list[Continent]) -> None:
        if len(continents) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == bindparam("iso2")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "iso2": continent.iso2,
                                           "name": continent.name
                                          } for continent in continents])

    @async_timed
    async def delete(self, continents: list[Continent]) -> None:
        iso2 = [continent.iso2 for continent in continents]
        stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso2")).in_(iso2))
        async with self._engine.begin() as conn:
            await conn.execute(stmt)


class CountryDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryDAO, self).__init__()


class SQlAlchemyCountryDAO(CountryDAO, SQLAlchemyDAO):
    """
    classdocs
    """
    
    def __init__(self) -> None:
        """
        Constructor
        """
        CountryDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)
    
    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country"),
                                   self._metadata,
                                   Column(self.get_column_name("iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("iso3"), String(3), nullable=False),
                                   Column(self.get_column_name("iso_code"), Integer, nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=False),
                                   Column(self.get_column_name("iso_name"), String(80), nullable=False),
                                   Column(self.get_column_name("in_oecd"), Boolean, nullable=False, default=False),
                                   PrimaryKeyConstraint(self.get_column_name("iso2"), name=self.get_key_name("country_pk")),
                                   UniqueConstraint(self.get_column_name("iso_code"), name=self.get_constraint_name("country_con1")),
                                   Index(self.get_index_name("country_idx1"), self.get_column_name("iso3"), unique=True),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, iso2: str | None = None) -> Country | dict[str, Country] | None:
        if iso2 is None:
            countries = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                country = Country(getattr(row, self.get_column_name("iso2")))
                country.iso3 = getattr(row, self.get_column_name("iso3"))
                country.iso_code = getattr(row, self.get_column_name("iso_code"))
                country.name = getattr(row, self.get_column_name("name"))
                country.fullname = getattr(row, self.get_column_name("fullname"))
                country.iso_name = getattr(row, self.get_column_name("iso_name"))
                country.in_oecd = getattr(row, self.get_column_name("in_oecd"))
                countries[country.iso2] = country
            return countries
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == iso2)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            country = None
            if row is not None:
                country = Country(getattr(row, self.get_column_name("iso2")))
                country.iso3 = getattr(row, self.get_column_name("iso3"))
                country.iso_code = getattr(row, self.get_column_name("iso_code"))
                country.name = getattr(row, self.get_column_name("name"))
                country.fullname = getattr(row, self.get_column_name("fullname"))
                country.iso_name = getattr(row, self.get_column_name("iso_name"))
                country.in_oecd = getattr(row, self.get_column_name("in_oecd"))
            return country

    @timed
    def create(self, countries: list[Country]) -> None:
        if len(countries) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso2"): country.iso2,
                                                self.get_column_name("iso3"): country.iso3,
                                                self.get_column_name("iso_code"): country.iso_code,
                                                self.get_column_name("name"): country.name,
                                                self.get_column_name("fullname"): country.fullname,
                                                self.get_column_name("iso_name"): country.iso_name,
                                                self.get_column_name("in_oecd"): country.in_oecd
                                               } for country in countries])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, countries: list[Country]) -> None:
        if len(countries) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == bindparam("iso2")).values({
                                                                                                                                self.get_column_name("iso3"): bindparam("iso3"),
                                                                                                                                self.get_column_name("iso_code"): bindparam("iso_code"),
                                                                                                                                self.get_column_name("name"): bindparam("name"),
                                                                                                                                self.get_column_name("fullname"): bindparam("fullname"),
                                                                                                                                self.get_column_name("iso_name"): bindparam("iso_name"),
                                                                                                                                self.get_column_name("in_oecd"): bindparam("in_oecd")
                                                                                                                               })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "iso2": country.iso2,
                                     "iso3": country.iso3,
                                     "iso_code": country.iso_code,
                                     "name": country.name,
                                     "fullname": country.fullname,
                                     "iso_name": country.iso_name,
                                     "in_oecd": country.in_oecd
                                    } for country in countries])

    @timed
    def delete(self, countries: list[Country]) -> None:
        if len(countries) > 0:
            iso2 = [cty.iso2 for cty in countries]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso2")).in_(iso2))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CountryAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryAsyncDAO, self).__init__()


class SQlAlchemyCountryAsyncDAO(CountryAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CountryAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country"),
                                   self._metadata,
                                   Column(self.get_column_name("iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("iso3"), String(3), nullable=False),
                                   Column(self.get_column_name("iso_code"), Integer, nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=False),
                                   Column(self.get_column_name("iso_name"), String(80), nullable=False),
                                   Column(self.get_column_name("in_oecd"), Boolean, nullable=False, default=False),
                                   PrimaryKeyConstraint(self.get_column_name("iso2"), name=self.get_key_name("country_pk")),
                                   UniqueConstraint(self.get_column_name("iso_code"), name=self.get_constraint_name("country_con1")),
                                   Index(self.get_index_name("country_idx1"), self.get_column_name("iso3"), unique=True),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, iso2: str | None = None) -> Country | dict[str, Country] | None:
        if iso2 is None:
            countries = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                country = Country(getattr(row, self.get_column_name("iso2")))
                country.iso3 = getattr(row, self.get_column_name("iso3"))
                country.iso_code = getattr(row, self.get_column_name("iso_code"))
                country.name = getattr(row, self.get_column_name("name"))
                country.fullname = getattr(row, self.get_column_name("fullname"))
                country.iso_name = getattr(row, self.get_column_name("iso_name"))
                country.in_oecd = getattr(row, self.get_column_name("in_oecd"))
                countries[country.iso2] = country
            return countries
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == iso2)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            country = None
            if row is not None:
                country = Country(getattr(row, self.get_column_name("iso2")))
                country.iso3 = getattr(row, self.get_column_name("iso3"))
                country.iso_code = getattr(row, self.get_column_name("iso_code"))
                country.name = getattr(row, self.get_column_name("name"))
                country.fullname = getattr(row, self.get_column_name("fullname"))
                country.iso_name = getattr(row, self.get_column_name("iso_name"))
                country.in_oecd = getattr(row, self.get_column_name("in_oecd"))
            return country

    @async_timed
    async def create(self, countries: list[Country]) -> None:
        if len(countries) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso2"): country.iso2,
                                                self.get_column_name("iso3"): country.iso3,
                                                self.get_column_name("iso_code"): country.iso_code,
                                                self.get_column_name("name"): country.name,
                                                self.get_column_name("fullname"): country.fullname,
                                                self.get_column_name("iso_name"): country.iso_name,
                                                self.get_column_name("in_oecd"): country.in_oecd
                                               } for country in countries])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, countries: list[Country]) -> None:
        if len(countries) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso2")) == bindparam("iso2")).values({
                                                                                                                                self.get_column_name("iso3"): bindparam("iso3"),
                                                                                                                                self.get_column_name("iso_code"): bindparam("iso_code"),
                                                                                                                                self.get_column_name("name"): bindparam("name"),
                                                                                                                                self.get_column_name("fullname"): bindparam("fullname"),
                                                                                                                                self.get_column_name("iso_name"): bindparam("iso_name"),
                                                                                                                                self.get_column_name("in_oecd"): bindparam("in_oecd")
                                                                                                                               })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "iso2": country.iso2,
                                           "iso3": country.iso3,
                                           "iso_code": country.iso_code,
                                           "name": country.name,
                                           "fullname": country.fullname,
                                           "iso_name": country.iso_name,
                                           "in_oecd": country.in_oecd
                                          } for country in countries])

    @async_timed
    async def delete(self, countries: list[Country]) -> None:
        if len(countries) > 0:
            iso2 = [cty.iso2 for cty in countries]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso2")).in_(iso2))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class CountryContinentDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryContinentDAO, self).__init__()


class SQlAlchemyCountryContinentDAO(CountryContinentDAO, SQLAlchemyDAO):
    """
    classdocs
    """
    
    def __init__(self) -> None:
        """
        Constructor
        """
        CountryContinentDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country_continent"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("continent_iso2"), String(2), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("country_continent_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_continent_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("continent_iso2")],
                                                        ["{}.{}".format(self.get_table_name("continent", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_continent_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> CountryContinent | dict[int, CountryContinent] | None:
        if id_ is None:
            country_continents = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                country_continent = CountryContinent(getattr(row, self.get_column_name("id")))
                country_continent.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_continent.continent_iso2 = getattr(row, self.get_column_name("continent_iso2"))
                country_continents[country_continent.id] = country_continent
            return country_continents
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            country_continent = None
            if row is not None:
                country_continent = CountryContinent(getattr(row, self.get_column_name("id")))
                country_continent.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_continent.continent_iso2 = getattr(row, self.get_column_name("continent_iso2"))
            return country_continent

    @timed
    def create(self, country_continents: list[CountryContinent]) -> None:
        if len(country_continents) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): ctycon.id,
                                                self.get_column_name("country_iso2"): ctycon.country_iso2,
                                                self.get_column_name("continent_iso2"): ctycon.continent_iso2
                                               } for ctycon in country_continents])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, country_continents: list[CountryContinent]) -> None:
        if len(country_continents) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("continent_iso2"): bindparam("continent_iso2")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": ctycon.id,
                                     "country_iso2": ctycon.country_iso2,
                                     "continent_iso2": ctycon.continent_iso2
                                    } for ctycon in country_continents])

    @timed
    def delete(self, country_continents: list[CountryContinent]) -> None:
        if len(country_continents) > 0:
            ids = [ctycon.id for ctycon in country_continents]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CountryContinentAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryContinentAsyncDAO, self).__init__()


class SQlAlchemyCountryContinentAsyncDAO(CountryContinentAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CountryContinentAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country_continent"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("continent_iso2"), String(2), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("country_continent_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_continent_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("continent_iso2")],
                                                        ["{}.{}".format(self.get_table_name("continent", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_continent_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> CountryContinent | dict[int, CountryContinent] | None:
        if id_ is None:
            country_continents = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                country_continent = CountryContinent(getattr(row, self.get_column_name("id")))
                country_continent.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_continent.continent_iso2 = getattr(row, self.get_column_name("continent_iso2"))
                country_continents[country_continent.id] = country_continent
            return country_continents
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            country_continent = None
            if row is not None:
                country_continent = CountryContinent(getattr(row, self.get_column_name("id")))
                country_continent.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_continent.continent_iso2 = getattr(row, self.get_column_name("continent_iso2"))
            return country_continent

    @async_timed
    async def create(self, country_continents: list[CountryContinent]) -> None:
        if len(country_continents) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): ctycon.id,
                                                self.get_column_name("country_iso2"): ctycon.country_iso2,
                                                self.get_column_name("continent_iso2"): ctycon.continent_iso2
                                               } for ctycon in country_continents])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, country_continents: list[CountryContinent]) -> None:
        if len(country_continents) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("continent_iso2"): bindparam("continent_iso2")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": ctycon.id,
                                           "country_iso2": ctycon.country_iso2,
                                           "continent_iso2": ctycon.continent_iso2
                                          } for ctycon in country_continents])

    @async_timed
    async def delete(self, country_continents: list[CountryContinent]) -> None:
        if len(country_continents) > 0:
            ids = [ctycon.id for ctycon in country_continents]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class CurrencyTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CurrencyTypeDAO, self).__init__()


class SQlAlchemyCurrencyTypeDAO(CurrencyTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CurrencyTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("currency_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("currency_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> CurrencyType | dict[str, CurrencyType] | None:
        if cfi is None:
            curtypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                curtype = CurrencyType(getattr(row, self.get_column_name("cfi")))
                curtype.name = getattr(row, self.get_column_name("name"))
                curtypes[curtype.cfi] = curtype
            return curtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            curtype = None
            if row is not None:
                curtype = CurrencyType(getattr(row, self.get_column_name("cfi")))
                curtype.name = getattr(row, self.get_column_name("name"))
            return curtype

    @timed
    def create(self, currency_types: list[CurrencyType]) -> None:
        if len(currency_types) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): curtype.cfi,
                                                self.get_column_name("name"): curtype.name
                                               } for curtype in currency_types])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, currency_types: list[CurrencyType]) -> None:
        if len(currency_types) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": curtype.cfi,
                                     "name": curtype.name
                                    } for curtype in currency_types])

    @timed
    def delete(self, currency_types: list[CurrencyType]) -> None:
        if len(currency_types) > 0:
            cfi = [curtype.cfi for curtype in currency_types]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CurrencyTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CurrencyTypeAsyncDAO, self).__init__()


class SQlAlchemyCurrencyTypeAsyncDAO(CurrencyTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CurrencyTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("currency_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("currency_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> CurrencyType | dict[str, CurrencyType] | None:
        if cfi is None:
            curtypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                curtype = CurrencyType(getattr(row, self.get_column_name("cfi")))
                curtype.name = getattr(row, self.get_column_name("name"))
                curtypes[curtype.cfi] = curtype
            return curtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            curtype = None
            if row is not None:
                curtype = CurrencyType(getattr(row, self.get_column_name("cfi")))
                curtype.name = getattr(row, self.get_column_name("name"))
            return curtype

    @async_timed
    async def create(self, currency_types: list[CurrencyType]) -> None:
        if len(currency_types) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): curtype.cfi,
                                                self.get_column_name("name"): curtype.name
                                               } for curtype in currency_types])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, currency_types: list[CurrencyType]) -> None:
        if len(currency_types) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": curtype.cfi,
                                           "name": curtype.name
                                          } for curtype in currency_types])

    @async_timed
    async def delete(self, currency_types: list[CurrencyType]) -> None:
        if len(currency_types) > 0:
            cfi = [curtype.cfi for curtype in currency_types]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class CurrencyDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CurrencyDAO, self).__init__()


class SQlAlchemyCurrencyDAO(CurrencyDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CurrencyDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("currency"),
                                   self._metadata,
                                   Column(self.get_column_name("iso3"), String(3), nullable=False),
                                   Column(self.get_column_name("iso_code"), Integer, nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=False),
                                   Column(self.get_column_name("symbol"), String(5), nullable=True),
                                   Column(self.get_column_name("cfi"), String(1), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("iso3"), name=self.get_key_name("currency_pk")),
                                   ForeignKeyConstraint([self.get_column_name("cfi")],
                                                        ["{}.{}".format(self.get_table_name("currency_type", "iso"), self.get_column_name("cfi"))],
                                                        name=self.get_key_name("currency_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, iso3: str | None = None) -> Currency | dict[str, Currency] | None:
        if iso3 is None:
            currencies = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                currency = Currency(getattr(row, self.get_column_name("iso3")))
                currency.iso_code = getattr(row, self.get_column_name("iso_code"))
                currency.name = getattr(row, self.get_column_name("name"))
                currency.fullname = getattr(row, self.get_column_name("fullname"))
                currency.symbol = getattr(row, self.get_column_name("symbol"))
                currency.cfi = getattr(row, self.get_column_name("cfi"))
                currencies[currency.iso3] = currency
            return currencies
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == iso3)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            currency = None
            if row is not None:
                currency = Currency(getattr(row, self.get_column_name("iso3")))
                currency.iso_code = getattr(row, self.get_column_name("iso_code"))
                currency.name = getattr(row, self.get_column_name("name"))
                currency.fullname = getattr(row, self.get_column_name("fullname"))
                currency.symbol = getattr(row, self.get_column_name("symbol"))
                currency.cfi = getattr(row, self.get_column_name("cfi"))
            return currency

    @timed
    def create(self, currencies: list[Currency]) -> None:
        if len(currencies) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso3"): currency.iso3,
                                                self.get_column_name("iso_code"): currency.iso_code,
                                                self.get_column_name("name"): currency.name,
                                                self.get_column_name("fullname"): currency.fullname,
                                                self.get_column_name("symbol"): currency.symbol,
                                                self.get_column_name("cfi"): currency.cfi
                                               } for currency in currencies])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, currencies: list[Currency]) -> None:
        if len(currencies) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == bindparam("iso3")).values({
                                                                                                                                self.get_column_name("iso_code"): bindparam("iso_code"),
                                                                                                                                self.get_column_name("name"): bindparam("name"),
                                                                                                                                self.get_column_name("fullname"): bindparam("fullname"),
                                                                                                                                self.get_column_name("symbol"): bindparam("symbol"),
                                                                                                                                self.get_column_name("cfi"): bindparam("cfi")
                                                                                                                               })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "iso3": currency.iso3,
                                     "iso_code": currency.iso_code,
                                     "name": currency.name,
                                     "fullname": currency.name,
                                     "symbol": currency.symbol,
                                     "cfi": currency.cfi
                                    } for currency in currencies])

    @timed
    def delete(self, currencies: list[Currency]) -> None:
        if len(currencies) > 0:
            iso3 = [currency.iso3 for currency in currencies]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso3")).in_(iso3))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CurrencyAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CurrencyAsyncDAO, self).__init__()


class SQlAlchemyCurrencyAsyncDAO(CurrencyAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CurrencyAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("currency"),
                                   self._metadata,
                                   Column(self.get_column_name("iso3"), String(3), nullable=False),
                                   Column(self.get_column_name("iso_code"), Integer, nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=False),
                                   Column(self.get_column_name("symbol"), String(5), nullable=True),
                                   Column(self.get_column_name("cfi"), String(1), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("iso3"), name=self.get_key_name("currency_pk")),
                                   ForeignKeyConstraint([self.get_column_name("cfi")],
                                                        ["{}.{}".format(self.get_table_name("currency_type", "iso"), self.get_column_name("cfi"))],
                                                        name=self.get_key_name("currency_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, iso3: str | None = None) -> Currency | dict[str, Currency] | None:
        if iso3 is None:
            currencies = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                currency = Currency(getattr(row, self.get_column_name("iso3")))
                currency.iso_code = getattr(row, self.get_column_name("iso_code"))
                currency.name = getattr(row, self.get_column_name("name"))
                currency.fullname = getattr(row, self.get_column_name("fullname"))
                currency.symbol = getattr(row, self.get_column_name("symbol"))
                currency.cfi = getattr(row, self.get_column_name("cfi"))
                currencies[currency.iso3] = currency
            return currencies
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == iso3)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            currency = None
            if row is not None:
                currency = Currency(getattr(row, self.get_column_name("iso3")))
                currency.iso_code = getattr(row, self.get_column_name("iso_code"))
                currency.name = getattr(row, self.get_column_name("name"))
                currency.fullname = getattr(row, self.get_column_name("fullname"))
                currency.symbol = getattr(row, self.get_column_name("symbol"))
                currency.cfi = getattr(row, self.get_column_name("cfi"))
            return currency

    @async_timed
    async def create(self, currencies: list[Currency]) -> None:
        if len(currencies) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso3"): currency.iso3,
                                                self.get_column_name("iso_code"): currency.iso_code,
                                                self.get_column_name("name"): currency.name,
                                                self.get_column_name("fullname"): currency.fullname,
                                                self.get_column_name("symbol"): currency.symbol,
                                                self.get_column_name("cfi"): currency.cfi
                                               } for currency in currencies])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, currencies: list[Currency]) -> None:
        if len(currencies) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == bindparam("iso3")).values({
                                                                                                                                self.get_column_name("iso_code"): bindparam("iso_code"),
                                                                                                                                self.get_column_name("name"): bindparam("name"),
                                                                                                                                self.get_column_name("fullname"): bindparam("fullname"),
                                                                                                                                self.get_column_name("symbol"): bindparam("symbol"),
                                                                                                                                self.get_column_name("cfi"): bindparam("cfi")
                                                                                                                               })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "iso3": currency.iso3,
                                           "iso_code": currency.iso_code,
                                           "name": currency.name,
                                           "fullname": currency.name,
                                           "symbol": currency.symbol,
                                           "cfi": currency.cfi
                                          } for currency in currencies])

    @async_timed
    async def delete(self, currencies: list[Currency]) -> None:
        iso3 = [currency.iso3 for currency in currencies]
        stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso3")).in_(iso3))
        async with self._engine.begin() as conn:
            await conn.execute(stmt)


class CountryCurrencyDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryCurrencyDAO, self).__init__()


class SQlAlchemyCountryCurrencyDAO(CountryCurrencyDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CountryCurrencyDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country_currency"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("currency_iso3"), String(3), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("country_currency_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_currency_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("currency_iso3")],
                                                        ["{}.{}".format(self.get_table_name("currency", "iso"), self.get_column_name("iso3"))],
                                                        name=self.get_key_name("country_currency_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> CountryCurrency | dict[int, CountryCurrency] | None:
        if id_ is None:
            country_currencies = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                country_currency = CountryCurrency(getattr(row, self.get_column_name("id")))
                country_currency.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_currency.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
                country_currencies[country_currency.id] = country_currency
            return country_currencies
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            country_currency = None
            if row is not None:
                country_currency = CountryCurrency(getattr(row, self.get_column_name("id")))
                country_currency.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_currency.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
            return country_currency

    @timed
    def create(self, country_currencies: list[CountryCurrency]) -> None:
        if len(country_currencies) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): ctycur.id,
                                                self.get_column_name("country_iso2"): ctycur.country_iso2,
                                                self.get_column_name("currency_iso3"): ctycur.currency_iso3
                                               } for ctycur in country_currencies])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, country_currencies: list[CountryCurrency]) -> None:
        if len(country_currencies) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("currency_iso3"): bindparam("currency_iso3")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": ctycur.id,
                                     "country_iso2": ctycur.country_iso2,
                                     "currency_iso3": ctycur.currency_iso3
                                    } for ctycur in country_currencies])

    @timed
    def delete(self, country_currencies: list[CountryCurrency]) -> None:
        if len(country_currencies) > 0:
            ids = [ctycur.id for ctycur in country_currencies]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CountryCurrencyAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryCurrencyAsyncDAO, self).__init__()


class SQlAlchemyCountryCurrencyAsyncDAO(CountryCurrencyAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CountryCurrencyAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country_currency"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("currency_iso3"), String(3), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("country_currency_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_currency_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("currency_iso3")],
                                                        ["{}.{}".format(self.get_table_name("currency", "iso"), self.get_column_name("iso3"))],
                                                        name=self.get_key_name("country_currency_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> CountryCurrency | dict[int, CountryCurrency] | None:
        if id_ is None:
            country_currencies = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                country_currency = CountryCurrency(getattr(row, self.get_column_name("id")))
                country_currency.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_currency.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
                country_currencies[country_currency.id] = country_currency
            return country_currencies
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            country_currency = None
            if row is not None:
                country_currency = CountryCurrency(getattr(row, self.get_column_name("id")))
                country_currency.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                country_currency.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
            return country_currency

    @async_timed
    async def create(self, country_currencies: list[CountryCurrency]) -> None:
        if len(country_currencies) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): ctycur.id,
                                                self.get_column_name("country_iso2"): ctycur.country_iso2,
                                                self.get_column_name("currency_iso3"): ctycur.currency_iso3
                                               } for ctycur in country_currencies])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, country_currencies: list[CountryCurrency]) -> None:
        if len(country_currencies) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("currency_iso3"): bindparam("currency_iso3")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": ctycur.id,
                                           "country_iso2": ctycur.country_iso2,
                                           "currency_iso3": ctycur.currency_iso3
                                          } for ctycur in country_currencies])

    @async_timed
    async def delete(self, country_currencies: list[CountryCurrency]) -> None:
        if len(country_currencies) > 0:
            ids = [ctycur.id for ctycur in country_currencies]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class PhonePrefixDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PhonePrefixDAO, self).__init__()


class SQlAlchemyPhonePrefixDAO(PhonePrefixDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        PhonePrefixDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("phone_prefix"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("prefix"), Integer, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("phone_prefix_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("phone_prefix_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> PhonePrefix | dict[int, PhonePrefix] | None:
        if id_ is None:
            phoneprefixes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                phoneprefix = PhonePrefix(getattr(row, self.get_column_name("id")))
                phoneprefix.prefix = getattr(row, self.get_column_name("prefix"))
                phoneprefix.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                phoneprefixes[phoneprefix.id] = phoneprefix
            return phoneprefixes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            phoneprefix = None
            if row is not None:
                phoneprefix = PhonePrefix(getattr(row, self.get_column_name("id")))
                phoneprefix.prefix = getattr(row, self.get_column_name("prefix"))
                phoneprefix.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
            return phoneprefix

    @timed
    def create(self, phoneprefixes: list[PhonePrefix]) -> None:
        if len(phoneprefixes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): phoneprefix.id,
                                                self.get_column_name("prefix"): phoneprefix.prefix,
                                                self.get_column_name("country_iso2"): phoneprefix.country_iso2
                                               } for phoneprefix in phoneprefixes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, phoneprefixes: list[PhonePrefix]) -> None:
        if len(phoneprefixes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("prefix"): bindparam("prefix"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": phoneprefix.id,
                                     "prefix": phoneprefix.prefix,
                                     "country_iso2": phoneprefix.country_iso2
                                    } for phoneprefix in phoneprefixes])

    @timed
    def delete(self, phoneprefixes: list[PhonePrefix]) -> None:
        if len(phoneprefixes) > 0:
            ids = [phoneprefix.id for phoneprefix in phoneprefixes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class PhonePrefixAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PhonePrefixAsyncDAO, self).__init__()


class SQlAlchemyPhonePrefixAsyncDAO(PhonePrefixAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        PhonePrefixAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("phone_prefix"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("prefix"), Integer, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("phone_prefix_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("phone_prefix_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> PhonePrefix | dict[int, PhonePrefix] | None:
        if id_ is None:
            phoneprefixes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                phoneprefix = PhonePrefix(getattr(row, self.get_column_name("id")))
                phoneprefix.prefix = getattr(row, self.get_column_name("prefix"))
                phoneprefix.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                phoneprefixes[phoneprefix.id] = phoneprefix
            return phoneprefixes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            phoneprefix = None
            if row is not None:
                phoneprefix = PhonePrefix(getattr(row, self.get_column_name("id")))
                phoneprefix.prefix = getattr(row, self.get_column_name("prefix"))
                phoneprefix.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
            return phoneprefix

    @async_timed
    async def create(self, phoneprefixes: list[PhonePrefix]) -> None:
        if len(phoneprefixes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): phoneprefix.id,
                                                self.get_column_name("prefix"): phoneprefix.prefix,
                                                self.get_column_name("country_iso2"): phoneprefix.country_iso2
                                               } for phoneprefix in phoneprefixes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, phoneprefixes: list[PhonePrefix]) -> None:
        if len(phoneprefixes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("prefix"): bindparam("prefix"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": phoneprefix.id,
                                           "prefix": phoneprefix.prefix,
                                           "country_iso2": phoneprefix.country_iso2
                                          } for phoneprefix in phoneprefixes])

    @async_timed
    async def delete(self, phoneprefixes: list[PhonePrefix]) -> None:
        if len(phoneprefixes) > 0:
            ids = [phoneprefix.id for phoneprefix in phoneprefixes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class LanguageDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(LanguageDAO, self).__init__()


class SQlAlchemyLanguageDAO(LanguageDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        LanguageDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("language"),
                                   self._metadata,
                                   Column(self.get_column_name("iso3"), String(3), nullable=False),
                                   Column(self.get_column_name("iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("iso639_3"), String(3), nullable=True),
                                   Column(self.get_column_name("iso639_3_other"), String(3), nullable=True),
                                   Column(self.get_column_name("iso639_1"), String(3), nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=False),
                                   Column(self.get_column_name("scope_code"), String(1), nullable=True),
                                   Column(self.get_column_name("type_code"), String(1), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("iso3"), name=self.get_key_name("language_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)


    @timed
    def get(self, iso3: str | None = None) -> Language | dict[str, Language] | None:
        if iso3 is None:
            languages = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                language = Language(getattr(row, self.get_column_name("iso3")))
                language.iso2 = getattr(row, self.get_column_name("iso2"))
                language.iso639_3 = getattr(row, self.get_column_name("iso639_3"))
                language.iso639_3_other = getattr(row, self.get_column_name("iso639_3_other"))
                language.iso639_1 = getattr(row, self.get_column_name("iso639_1"))
                language.name = getattr(row, self.get_column_name("name"))
                language.fullname = getattr(row, self.get_column_name("fullname"))
                language.scope_code = getattr(row, self.get_column_name("scope_code"))
                language.type_code = getattr(row, self.get_column_name("type_code"))
                languages[language.iso3] = language
            return languages
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == iso3)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            language = None
            if row is not None:
                language = Language(getattr(row, self.get_column_name("iso3")))
                language.iso2 = getattr(row, self.get_column_name("iso2"))
                language.iso639_3 = getattr(row, self.get_column_name("iso639_3"))
                language.iso639_3_other = getattr(row, self.get_column_name("iso639_3_other"))
                language.iso639_1 = getattr(row, self.get_column_name("iso639_1"))
                language.name = getattr(row, self.get_column_name("name"))
                language.fullname = getattr(row, self.get_column_name("fullname"))
                language.scope_code = getattr(row, self.get_column_name("scope_code"))
                language.type_code = getattr(row, self.get_column_name("type_code"))
            return language

    @timed
    def create(self, languages: list[Language]) -> None:
        if len(languages) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso3"): language.iso3,
                                                self.get_column_name("iso2"): language.iso2,
                                                self.get_column_name("iso639_3"): language.iso639_3,
                                                self.get_column_name("iso639_3_other"): language.iso639_3_other,
                                                self.get_column_name("iso639_1"): language.iso639_1,
                                                self.get_column_name("name"): language.name,
                                                self.get_column_name("fullname"): language.fullname,
                                                self.get_column_name("scope_code"): language.scope_code,
                                                self.get_column_name("type_code"): language.type_code
                                               } for language in languages])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, languages: list[Language]) -> None:
        if len(languages) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == bindparam("iso3")).values({
                                                                                                                                self.get_column_name("iso2"): bindparam("iso2"),
                                                                                                                                self.get_column_name("iso639_3"): bindparam("iso639_3"),
                                                                                                                                self.get_column_name("iso639_3_other"): bindparam("iso639_3_other"),
                                                                                                                                self.get_column_name("iso639_1"): bindparam("iso639_1"),
                                                                                                                                self.get_column_name("name"): bindparam("name"),
                                                                                                                                self.get_column_name("fullname"): bindparam("fullname"),
                                                                                                                                self.get_column_name("scope_code"): bindparam("scope_code"),
                                                                                                                                self.get_column_name("type_code"): bindparam("type_code")
                                                                                                                               })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "iso3": language.iso3,
                                     "iso2": language.iso2,
                                     "iso639_3": language.iso639_3,
                                     "iso639_3_other": language.iso639_3_other,
                                     "iso639_1": language.iso639_1,
                                     "name": language.name,
                                     "fullname": language.fullname,
                                     "scope_code": language.scope_code,
                                     "type_code": language.type_code
                                    } for language in languages])

    @timed
    def delete(self, languages: list[Language]) -> None:
        if len(languages) > 0:
            iso3 = [language.iso3 for language in languages]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso3")).in_(iso3))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class LanguageAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(LanguageAsyncDAO, self).__init__()


class SQlAlchemyLanguageAsyncDAO(LanguageAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        LanguageAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("language"),
                                   self._metadata,
                                   Column(self.get_column_name("iso3"), String(3), nullable=False),
                                   Column(self.get_column_name("iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("iso639_3"), String(3), nullable=True),
                                   Column(self.get_column_name("iso639_3_other"), String(3), nullable=True),
                                   Column(self.get_column_name("iso639_1"), String(3), nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=False),
                                   Column(self.get_column_name("scope_code"), String(1), nullable=True),
                                   Column(self.get_column_name("type_code"), String(1), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("iso3"), name=self.get_key_name("language_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)


    @async_timed
    async def get(self, iso3: str | None = None) -> Language | dict[str, Language] | None:
        if iso3 is None:
            languages = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                language = Language(getattr(row, self.get_column_name("iso3")))
                language.iso2 = getattr(row, self.get_column_name("iso2"))
                language.iso639_3 = getattr(row, self.get_column_name("iso639_3"))
                language.iso639_3_other = getattr(row, self.get_column_name("iso639_3_other"))
                language.iso639_1 = getattr(row, self.get_column_name("iso639_1"))
                language.name = getattr(row, self.get_column_name("name"))
                language.fullname = getattr(row, self.get_column_name("fullname"))
                language.scope_code = getattr(row, self.get_column_name("scope_code"))
                language.type_code = getattr(row, self.get_column_name("type_code"))
                languages[language.iso3] = language
            return languages
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == iso3)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            language = None
            if row is not None:
                language = Language(getattr(row, self.get_column_name("iso3")))
                language.iso2 = getattr(row, self.get_column_name("iso2"))
                language.iso639_3 = getattr(row, self.get_column_name("iso639_3"))
                language.iso639_3_other = getattr(row, self.get_column_name("iso639_3_other"))
                language.iso639_1 = getattr(row, self.get_column_name("iso639_1"))
                language.name = getattr(row, self.get_column_name("name"))
                language.fullname = getattr(row, self.get_column_name("fullname"))
                language.scope_code = getattr(row, self.get_column_name("scope_code"))
                language.type_code = getattr(row, self.get_column_name("type_code"))
            return language

    @async_timed
    async def create(self, languages: list[Language]) -> None:
        if len(languages) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("iso3"): language.iso3,
                                                self.get_column_name("iso2"): language.iso2,
                                                self.get_column_name("iso639_3"): language.iso639_3,
                                                self.get_column_name("iso639_3_other"): language.iso639_3_other,
                                                self.get_column_name("iso639_1"): language.iso639_1,
                                                self.get_column_name("name"): language.name,
                                                self.get_column_name("fullname"): language.fullname,
                                                self.get_column_name("scope_code"): language.scope_code,
                                                self.get_column_name("type_code"): language.type_code
                                               } for language in languages])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, languages: list[Language]) -> None:
        if len(languages) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("iso3")) == bindparam("iso3")).values({
                                                                                                                                self.get_column_name("iso2"): bindparam("iso2"),
                                                                                                                                self.get_column_name("iso639_3"): bindparam("iso639_3"),
                                                                                                                                self.get_column_name("iso639_3_other"): bindparam("iso639_3_other"),
                                                                                                                                self.get_column_name("iso639_1"): bindparam("iso639_1"),
                                                                                                                                self.get_column_name("name"): bindparam("name"),
                                                                                                                                self.get_column_name("fullname"): bindparam("fullname"),
                                                                                                                                self.get_column_name("scope_code"): bindparam("scope_code"),
                                                                                                                                self.get_column_name("type_code"): bindparam("type_code")
                                                                                                                               })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "iso3": language.iso3,
                                           "iso2": language.iso2,
                                           "iso639_3": language.iso639_3,
                                           "iso639_3_other": language.iso639_3_other,
                                           "iso639_1": language.iso639_1,
                                           "name": language.name,
                                           "fullname": language.fullname,
                                           "scope_code": language.scope_code,
                                           "type_code": language.type_code
                                          } for language in languages])

    @async_timed
    async def delete(self, languages: list[Language]) -> None:
        if len(languages) > 0:
            iso3 = [language.iso3 for language in languages]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("iso3")).in_(iso3))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class MarketExchangeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MarketExchangeDAO, self).__init__()


class SQlAlchemyMarketExchangeDAO(MarketExchangeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        MarketExchangeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("market_exchange"),
                                   self._metadata,
                                   Column(self.get_column_name("mic"), String(4), nullable=False),
                                   Column(self.get_column_name("operating_mic"), String(4), nullable=False),
                                   Column(self.get_column_name("lei"), String(20), nullable=True),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("name"), String(150), nullable=False),
                                   Column(self.get_column_name("acronym"), String(20), nullable=True),
                                   Column(self.get_column_name("city"), String(50), nullable=True),
                                   Column(self.get_column_name("website"), String(150), nullable=True),
                                   Column(self.get_column_name("open_date"), Date, nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("mic"), name=self.get_key_name("market_exchange_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("market_exchange_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, mic: str | None = None) -> MarketExchange | dict[str, MarketExchange] | None:
        if mic is None:
            exchanges = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                exchange = MarketExchange(getattr(row, self.get_column_name("mic")))
                exchange.operating_mic = getattr(row, self.get_column_name("operating_mic"))
                exchange.lei = getattr(row, self.get_column_name("lei"))
                exchange.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                exchange.name = getattr(row, self.get_column_name("name"))
                exchange.acronym = getattr(row, self.get_column_name("acronym"))
                exchange.city = getattr(row, self.get_column_name("city"))
                exchange.website = getattr(row, self.get_column_name("website"))
                exchange.open_date = getattr(row, self.get_column_name("open_date"))
                exchanges[exchange.mic] = exchange
            return exchanges
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("mic")) == mic)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            exchange = None
            if row is not None:
                exchange = MarketExchange(getattr(row, self.get_column_name("mic")))
                exchange.operating_mic = getattr(row, self.get_column_name("operating_mic"))
                exchange.lei = getattr(row, self.get_column_name("lei"))
                exchange.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                exchange.name = getattr(row, self.get_column_name("name"))
                exchange.acronym = getattr(row, self.get_column_name("acronym"))
                exchange.city = getattr(row, self.get_column_name("city"))
                exchange.website = getattr(row, self.get_column_name("website"))
                exchange.open_date = getattr(row, self.get_column_name("open_date"))
            return exchange

    @timed
    def create(self, exchanges: list[MarketExchange]) -> None:
        if len(exchanges) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("mic"): exchange.mic,
                                                self.get_column_name("operating_mic"): exchange.operating_mic,
                                                self.get_column_name("lei"): exchange.lei,
                                                self.get_column_name("country_iso2"): exchange.country_iso2,
                                                self.get_column_name("name"): exchange.name,
                                                self.get_column_name("acronym"): exchange.acronym,
                                                self.get_column_name("city"): exchange.city,
                                                self.get_column_name("website"): exchange.website,
                                                self.get_column_name("open_date"): exchange.open_date
                                               } for exchange in exchanges])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, exchanges: list[MarketExchange]) -> None:
        if len(exchanges) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("mic")) == bindparam("mic")).values({
                                                                                                                              self.get_column_name("operating_mic"): bindparam("operating_mic"),
                                                                                                                              self.get_column_name("lei"): bindparam("lei"),
                                                                                                                              self.get_column_name("name"): bindparam("name"),
                                                                                                                              self.get_column_name("acronym"): bindparam("acronym"),
                                                                                                                              self.get_column_name("city"): bindparam("city"),
                                                                                                                              self.get_column_name("website"): bindparam("website"),
                                                                                                                              self.get_column_name("open_date"): bindparam("open_date")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "mic": exchange.mic,
                                     "operating_mic": exchange.operating_mic,
                                     "lei": exchange.lei,
                                     "name": exchange.name,
                                     "acronym": exchange.acronym,
                                     "city": exchange.city,
                                     "website": exchange.website,
                                     "open_date": exchange.open_date
                                    } for exchange in exchanges])

    @timed
    def delete(self, exchanges: list[MarketExchange]) -> None:
        if len(exchanges) > 0:
            mics = [exchange.mic for exchange in exchanges]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("mic")).in_(mics))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class MarketExchangeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MarketExchangeAsyncDAO, self).__init__()


class SQlAlchemyMarketExchangeAsyncDAO(MarketExchangeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        MarketExchangeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("market_exchange"),
                                   self._metadata,
                                   Column(self.get_column_name("mic"), String(4), nullable=False),
                                   Column(self.get_column_name("operating_mic"), String(4), nullable=False),
                                   Column(self.get_column_name("lei"), String(20), nullable=True),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("name"), String(150), nullable=False),
                                   Column(self.get_column_name("acronym"), String(20), nullable=True),
                                   Column(self.get_column_name("city"), String(50), nullable=True),
                                   Column(self.get_column_name("website"), String(150), nullable=True),
                                   Column(self.get_column_name("open_date"), Date, nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("mic"), name=self.get_key_name("market_exchange_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("market_exchange_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, mic: str | None = None) -> MarketExchange | dict[str, MarketExchange] | None:
        if mic is None:
            exchanges = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                exchange = MarketExchange(getattr(row, self.get_column_name("mic")))
                exchange.operating_mic = getattr(row, self.get_column_name("operating_mic"))
                exchange.lei = getattr(row, self.get_column_name("lei"))
                exchange.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                exchange.name = getattr(row, self.get_column_name("name"))
                exchange.acronym = getattr(row, self.get_column_name("acronym"))
                exchange.city = getattr(row, self.get_column_name("city"))
                exchange.website = getattr(row, self.get_column_name("website"))
                exchange.open_date = getattr(row, self.get_column_name("open_date"))
                exchanges[exchange.mic] = exchange
            return exchanges
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("mic")) == mic)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            exchange = None
            if row is not None:
                exchange = MarketExchange(getattr(row, self.get_column_name("mic")))
                exchange.operating_mic = getattr(row, self.get_column_name("operating_mic"))
                exchange.lei = getattr(row, self.get_column_name("lei"))
                exchange.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                exchange.name = getattr(row, self.get_column_name("name"))
                exchange.acronym = getattr(row, self.get_column_name("acronym"))
                exchange.city = getattr(row, self.get_column_name("city"))
                exchange.website = getattr(row, self.get_column_name("website"))
                exchange.open_date = getattr(row, self.get_column_name("open_date"))
            return exchange

    @async_timed
    async def create(self, exchanges: list[MarketExchange]) -> None:
        if len(exchanges) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("mic"): exchange.mic,
                                                self.get_column_name("operating_mic"): exchange.operating_mic,
                                                self.get_column_name("lei"): exchange.lei,
                                                self.get_column_name("country_iso2"): exchange.country_iso2,
                                                self.get_column_name("name"): exchange.name,
                                                self.get_column_name("acronym"): exchange.acronym,
                                                self.get_column_name("city"): exchange.city,
                                                self.get_column_name("website"): exchange.website,
                                                self.get_column_name("open_date"): exchange.open_date
                                               } for exchange in exchanges])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, exchanges: list[MarketExchange]) -> None:
        if len(exchanges) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("mic")) == bindparam("mic")).values({
                                                                                                                              self.get_column_name("operating_mic"): bindparam("operating_mic"),
                                                                                                                              self.get_column_name("lei"): bindparam("lei"),
                                                                                                                              self.get_column_name("name"): bindparam("name"),
                                                                                                                              self.get_column_name("acronym"): bindparam("acronym"),
                                                                                                                              self.get_column_name("city"): bindparam("city"),
                                                                                                                              self.get_column_name("website"): bindparam("website"),
                                                                                                                              self.get_column_name("open_date"): bindparam("open_date")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "mic": exchange.mic,
                                           "operating_mic": exchange.operating_mic,
                                           "lei": exchange.lei,
                                           "name": exchange.name,
                                           "acronym": exchange.acronym,
                                           "city": exchange.city,
                                           "website": exchange.website,
                                           "open_date": exchange.open_date
                                          } for exchange in exchanges])

    @async_timed
    async def delete(self, exchanges: list[MarketExchange]) -> None:
        if len(exchanges) > 0:
            mics = [exchange.mic for exchange in exchanges]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("mic")).in_(mics))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class InstrumentCategoryDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InstrumentCategoryDAO, self).__init__()


class SQlAlchemyInstrumentCategoryDAO(InstrumentCategoryDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InstrumentCategoryDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("instrument_category"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("instrument_category_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> InstrumentCategory | dict[str, InstrumentCategory] | None:
        if cfi is None:
            categs = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                categ = InstrumentCategory(getattr(row, self.get_column_name("cfi")))
                categ.name = getattr(row, self.get_column_name("name"))
                categ.fullname = getattr(row, self.get_column_name("fullname"))
                categs[categ.cfi] = categ
            return categs
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            categ = None
            if row is not None:
                categ = InstrumentCategory(getattr(row, self.get_column_name("cfi")))
                categ.name = getattr(row, self.get_column_name("name"))
                categ.fullname = getattr(row, self.get_column_name("fullname"))
            return categ

    @timed
    def create(self, categs: list[InstrumentCategory]) -> None:
        if len(categs) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): categ.cfi,
                                                self.get_column_name("name"): categ.name,
                                                self.get_column_name("fullname"): categ.fullname
                                               } for categ in categs])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, categs: list[InstrumentCategory]) -> None:
        if len(categs) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name"),
                                                                                                                              self.get_column_name("fullname"): bindparam("fullname")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": categ.cfi,
                                     "name": categ.name,
                                     "fullname": categ.fullname
                                    } for categ in categs])

    @timed
    def delete(self, categs: list[InstrumentCategory]) -> None:
        if len(categs) > 0:
            cfi = [categ.cfi for categ in categs]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class InstrumentCategoryAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InstrumentCategoryAsyncDAO, self).__init__()


class SQlAlchemyInstrumentCategoryAsyncDAO(InstrumentCategoryAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InstrumentCategoryAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("instrument_category"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("instrument_category_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> InstrumentCategory | dict[str, InstrumentCategory] | None:
        if cfi is None:
            categs = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                categ = InstrumentCategory(getattr(row, self.get_column_name("cfi")))
                categ.name = getattr(row, self.get_column_name("name"))
                categ.fullname = getattr(row, self.get_column_name("fullname"))
                categs[categ.cfi] = categ
            return categs
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            categ = None
            if row is not None:
                categ = InstrumentCategory(getattr(row, self.get_column_name("cfi")))
                categ.name = getattr(row, self.get_column_name("name"))
                categ.fullname = getattr(row, self.get_column_name("fullname"))
            return categ

    @async_timed
    async def create(self, categs: list[InstrumentCategory]) -> None:
        if len(categs) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): categ.cfi,
                                                self.get_column_name("name"): categ.name,
                                                self.get_column_name("fullname"): categ.fullname
                                               } for categ in categs])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, categs: list[InstrumentCategory]) -> None:
        if len(categs) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name"),
                                                                                                                              self.get_column_name("fullname"): bindparam("fullname")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": categ.cfi,
                                           "name": categ.name,
                                           "fullname": categ.fullname
                                          } for categ in categs])

    @async_timed
    async def delete(self, categs: list[InstrumentCategory]) -> None:
        if len(categs) > 0:
            cfi = [categ.cfi for categ in categs]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class InstrumentGroupDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InstrumentGroupDAO, self).__init__()


class SQlAlchemyInstrumentGroupDAO(InstrumentGroupDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InstrumentGroupDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("instrument_group"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(2), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=True),
                                   Column(self.get_column_name("category_cfi"), String(1), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("instrument_group_pk")),
                                   ForeignKeyConstraint([self.get_column_name("category_cfi")],
                                                        ["{}.{}".format(self.get_table_name("instrument_category", "iso"), self.get_column_name("cfi"))],
                                                        name=self.get_key_name("instrument_group_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> InstrumentGroup | dict[str, InstrumentGroup] | None:
        if cfi is None:
            groups = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                group = InstrumentGroup(getattr(row, self.get_column_name("cfi")))
                group.name = getattr(row, self.get_column_name("name"))
                group.fullname = getattr(row, self.get_column_name("fullname"))
                group.category_cfi = getattr(row, self.get_column_name("category_cfi"))
                groups[group.cfi] = group
            return groups
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            group = None
            if row is not None:
                group = InstrumentGroup(getattr(row, self.get_column_name("cfi")))
                group.name = getattr(row, self.get_column_name("name"))
                group.fullname = getattr(row, self.get_column_name("fullname"))
                group.category_cfi = getattr(row, self.get_column_name("category_cfi"))
            return group

    @timed
    def create(self, groups: list[InstrumentGroup]) -> None:
        if len(groups) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): group.cfi,
                                                self.get_column_name("name"): group.name,
                                                self.get_column_name("fullname"): group.fullname,
                                                self.get_column_name("category_cfi"): group.category_cfi
                                               } for group in groups])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, groups: list[InstrumentGroup]) -> None:
        if len(groups) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name"),
                                                                                                                              self.get_column_name("category_cfi"): bindparam("category_cfi")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": group.cfi,
                                     "name": group.name,
                                     "category_cfi": group.name
                                    } for group in groups])

    @timed
    def delete(self, groups: list[InstrumentGroup]) -> None:
        if len(groups) > 0:
            cfi = [group.cfi for group in groups]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class InstrumentGroupAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InstrumentGroupAsyncDAO, self).__init__()


class SQlAlchemyInstrumentGroupAsyncDAO(InstrumentGroupAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InstrumentGroupAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("instrument_group"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(2), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("fullname"), String(80), nullable=True),
                                   Column(self.get_column_name("category_cfi"), String(1), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("instrument_group_pk")),
                                   ForeignKeyConstraint([self.get_column_name("category_cfi")],
                                                        ["{}.{}".format(self.get_table_name("instrument_category", "iso"), self.get_column_name("cfi"))],
                                                        name=self.get_key_name("instrument_group_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> InstrumentGroup | dict[str, InstrumentGroup] | None:
        if cfi is None:
            groups = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                group = InstrumentGroup(getattr(row, self.get_column_name("cfi")))
                group.name = getattr(row, self.get_column_name("name"))
                group.fullname = getattr(row, self.get_column_name("fullname"))
                group.category_cfi = getattr(row, self.get_column_name("category_cfi"))
                groups[group.cfi] = group
            return groups
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            group = None
            if row is not None:
                group = InstrumentGroup(getattr(row, self.get_column_name("cfi")))
                group.name = getattr(row, self.get_column_name("name"))
                group.fullname = getattr(row, self.get_column_name("fullname"))
                group.category_cfi = getattr(row, self.get_column_name("category_cfi"))
            return group

    @async_timed
    async def create(self, groups: list[InstrumentGroup]) -> None:
        if len(groups) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): group.cfi,
                                                self.get_column_name("name"): group.name,
                                                self.get_column_name("fullname"): group.fullname,
                                                self.get_column_name("category_cfi"): group.category_cfi
                                               } for group in groups])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, groups: list[InstrumentGroup]) -> None:
        if len(groups) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name"),
                                                                                                                              self.get_column_name("category_cfi"): bindparam("category_cfi")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": group.cfi,
                                           "name": group.name,
                                           "category_cfi": group.name
                                          } for group in groups])

    @async_timed
    async def delete(self, groups: list[InstrumentGroup]) -> None:
        if len(groups) > 0:
            cfi = [group.cfi for group in groups]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class VotingRightDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(VotingRightDAO, self).__init__()


class SQlAlchemyVotingRightDAO(VotingRightDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        VotingRightDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("voting_right"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("voting_right_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> VotingRight | dict[str, VotingRight] | None:
        if cfi is None:
            rights = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                right = VotingRight(getattr(row, self.get_column_name("cfi")))
                right.name = getattr(row, self.get_column_name("name"))
                rights[right.cfi] = rights
            return rights
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            right = None
            if row is not None:
                right = VotingRight(getattr(row, self.get_column_name("cfi")))
                right.name = getattr(row, self.get_column_name("name"))
            return right

    @timed
    def create(self, rights: list[VotingRight]) -> None:
        if len(rights) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): right.cfi,
                                                self.get_column_name("name"): right.name
                                               } for right in rights])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, rights: list[VotingRight]) -> None:
        if len(rights) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": right.cfi,
                                     "name": right.name
                                    } for right in rights])

    @timed
    def delete(self, rights: list[VotingRight]) -> None:
        if len(rights) > 0:
            cfi = [right.cfi for right in rights]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class VotingRightAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(VotingRightAsyncDAO, self).__init__()


class SQlAlchemyVotingRightAsyncDAO(VotingRightAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        VotingRightAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("voting_right"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("voting_right_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> VotingRight | dict[str, VotingRight] | None:
        if cfi is None:
            rights = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                right = VotingRight(getattr(row, self.get_column_name("cfi")))
                right.name = getattr(row, self.get_column_name("name"))
                rights[right.cfi] = rights
            return rights
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            right = None
            if row is not None:
                right = VotingRight(getattr(row, self.get_column_name("cfi")))
                right.name = getattr(row, self.get_column_name("name"))
            return right

    @async_timed
    async def create(self, rights: list[VotingRight]) -> None:
        if len(rights) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): right.cfi,
                                                self.get_column_name("name"): right.name
                                               } for right in rights])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, rights: list[VotingRight]) -> None:
        if len(rights) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": right.cfi,
                                           "name": right.name
                                          } for right in rights])

    @async_timed
    async def delete(self, rights: list[VotingRight]) -> None:
        if len(rights) > 0:
            cfi = [right.cfi for right in rights]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class InstrumentOwnershipDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InstrumentOwnershipDAO, self).__init__()


class SQlAlchemyInstrumentOwnershipDAO(InstrumentOwnershipDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InstrumentOwnershipDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("instrument_ownership"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("instrument_ownership_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> InstrumentOwnership | dict[str, InstrumentOwnership] | None:
        if cfi is None:
            ownerships = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                ownership = InstrumentOwnership(getattr(row, self.get_column_name("cfi")))
                ownership.name = getattr(row, self.get_column_name("name"))
                ownerships[ownership.cfi] = ownerships
            return ownerships
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            ownership = None
            if row is not None:
                ownership = InstrumentOwnership(getattr(row, self.get_column_name("cfi")))
                ownership.name = getattr(row, self.get_column_name("name"))
            return ownership

    @timed
    def create(self, ownerships: list[InstrumentOwnership]) -> None:
        if len(ownerships) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): ownership.cfi,
                                                self.get_column_name("name"): ownership.name
                                               } for ownership in ownerships])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, ownerships: list[InstrumentOwnership]) -> None:
        if len(ownerships) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": ownership.cfi,
                                     "name": ownership.name
                                    } for ownership in ownerships])

    @timed
    def delete(self, ownerships: list[InstrumentOwnership]) -> None:
        if len(ownerships) > 0:
            cfi = [ownership.cfi for ownership in ownerships]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class InstrumentOwnershipAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InstrumentOwnershipAsyncDAO, self).__init__()


class SQlAlchemyInstrumentOwnershipAsyncDAO(InstrumentOwnershipAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InstrumentOwnershipAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("instrument_ownership"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("instrument_ownership_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> InstrumentOwnership | dict[str, InstrumentOwnership] | None:
        if cfi is None:
            ownerships = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                ownership = InstrumentOwnership(getattr(row, self.get_column_name("cfi")))
                ownership.name = getattr(row, self.get_column_name("name"))
                ownerships[ownership.cfi] = ownerships
            return ownerships
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            ownership = None
            if row is not None:
                ownership = InstrumentOwnership(getattr(row, self.get_column_name("cfi")))
                ownership.name = getattr(row, self.get_column_name("name"))
            return ownership

    @async_timed
    async def create(self, ownerships: list[InstrumentOwnership]) -> None:
        if len(ownerships) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): ownership.cfi,
                                                self.get_column_name("name"): ownership.name
                                               } for ownership in ownerships])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, ownerships: list[InstrumentOwnership]) -> None:
        if len(ownerships) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": ownership.cfi,
                                           "name": ownership.name
                                          } for ownership in ownerships])

    @async_timed
    async def delete(self, ownerships: list[InstrumentOwnership]) -> None:
        if len(ownerships) > 0:
            cfi = [ownership.cfi for ownership in ownerships]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class PaymentStatusDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PaymentStatusDAO, self).__init__()


class SQlAlchemyPaymentStatusDAO(PaymentStatusDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        PaymentStatusDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("payment_status"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("payment_status_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> PaymentStatus | dict[str, PaymentStatus] | None:
        if cfi is None:
            statuses = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                status = PaymentStatus(getattr(row, self.get_column_name("cfi")))
                status.name = getattr(row, self.get_column_name("name"))
                statuses[status.cfi] = status
            return statuses
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            status = None
            if row is not None:
                status = PaymentStatus(getattr(row, self.get_column_name("cfi")))
                status.name = getattr(row, self.get_column_name("name"))
            return status

    @timed
    def create(self, statuses: list[PaymentStatus]) -> None:
        if len(statuses) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): status.cfi,
                                                self.get_column_name("name"): status.name
                                               } for status in statuses])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, statuses: list[PaymentStatus]) -> None:
        if len(statuses) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": status.cfi,
                                     "name": status.name
                                    } for status in statuses])

    @timed
    def delete(self, statuses: list[PaymentStatus]) -> None:
        if len(statuses) > 0:
            cfi = [status.cfi for status in statuses]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class PaymentStatusAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PaymentStatusAsyncDAO, self).__init__()


class SQlAlchemyPaymentStatusAsyncDAO(PaymentStatusAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        PaymentStatusAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("payment_status"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("payment_status_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> PaymentStatus | dict[str, PaymentStatus] | None:
        if cfi is None:
            statuses = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                status = PaymentStatus(getattr(row, self.get_column_name("cfi")))
                status.name = getattr(row, self.get_column_name("name"))
                statuses[status.cfi] = status
            return statuses
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            status = None
            if row is not None:
                status = PaymentStatus(getattr(row, self.get_column_name("cfi")))
                status.name = getattr(row, self.get_column_name("name"))
            return status

    @async_timed
    async def create(self, statuses: list[PaymentStatus]) -> None:
        if len(statuses) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): status.cfi,
                                                self.get_column_name("name"): status.name
                                               } for status in statuses])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, statuses: list[PaymentStatus]) -> None:
        if len(statuses) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": status.cfi,
                                           "name": status.name
                                          } for status in statuses])

    @async_timed
    async def delete(self, statuses: list[PaymentStatus]) -> None:
        if len(statuses) > 0:
            cfi = [status.cfi for status in statuses]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class IncomeTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(IncomeTypeDAO, self).__init__()


class SQlAlchemyIncomeTypeDAO(IncomeTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        IncomeTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("income_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("income_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> IncomeType | dict[str, IncomeType] | None:
        if cfi is None:
            incomes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                income = IncomeType(getattr(row, self.get_column_name("cfi")))
                income.name = getattr(row, self.get_column_name("name"))
                incomes[income.cfi] = income
            return incomes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            income = None
            if row is not None:
                income = IncomeType(getattr(row, self.get_column_name("cfi")))
                income.name = getattr(row, self.get_column_name("name"))
            return income

    @timed
    def create(self, incomes: list[IncomeType]) -> None:
        if len(incomes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): income.cfi,
                                                self.get_column_name("name"): income.name
                                               } for income in incomes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, incomes: list[IncomeType]) -> None:
        if len(incomes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": income.cfi,
                                     "name": income.name
                                    } for income in incomes])

    @timed
    def delete(self, incomes: list[IncomeType]) -> None:
        if len(incomes) > 0:
            cfi = [income.cfi for income in incomes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class IncomeTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(IncomeTypeAsyncDAO, self).__init__()


class SQlAlchemyIncomeTypeAsyncDAO(IncomeTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        IncomeTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("income_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("income_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> IncomeType | dict[str, IncomeType] | None:
        if cfi is None:
            incomes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                income = IncomeType(getattr(row, self.get_column_name("cfi")))
                income.name = getattr(row, self.get_column_name("name"))
                incomes[income.cfi] = income
            return incomes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            income = None
            if row is not None:
                income = IncomeType(getattr(row, self.get_column_name("cfi")))
                income.name = getattr(row, self.get_column_name("name"))
            return income

    @async_timed
    async def create(self, incomes: list[IncomeType]) -> None:
        if len(incomes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): income.cfi,
                                                self.get_column_name("name"): income.name
                                               } for income in incomes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, incomes: list[IncomeType]) -> None:
        if len(incomes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": income.cfi,
                                           "name": income.name
                                          } for income in incomes])

    @async_timed
    async def delete(self, incomes: list[IncomeType]) -> None:
        if len(incomes) > 0:
            cfi = [income.cfi for income in incomes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class RedemptionConversionTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RedemptionConversionTypeDAO, self).__init__()


class SQlAlchemyRedemptionConversionTypeDAO(RedemptionConversionTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        RedemptionConversionTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("redemption_conversion_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("redemption_conversion_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> RedemptionConversionType | dict[str, RedemptionConversionType] | None:
        if cfi is None:
            convtypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                convtype = RedemptionConversionType(getattr(row, self.get_column_name("cfi")))
                convtype.name = getattr(row, self.get_column_name("name"))
                convtypes[convtype.cfi] = convtype
            return convtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            convtype = None
            if row is not None:
                convtype = RedemptionConversionType(getattr(row, self.get_column_name("cfi")))
                convtype.name = getattr(row, self.get_column_name("name"))
            return convtype

    @timed
    def create(self, convtypes: list[RedemptionConversionType]) -> None:
        if len(convtypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): convtype.cfi,
                                                self.get_column_name("name"): convtype.name
                                               } for convtype in convtypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, convtypes: list[RedemptionConversionType]) -> None:
        if len(convtypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": convtype.cfi,
                                     "name": convtype.name
                                    } for convtype in convtypes])

    @timed
    def delete(self, convtypes: list[IncomeType]) -> None:
        if len(convtypes) > 0:
            cfi = [convtype.cfi for convtype in convtypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class RedemptionConversionTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RedemptionConversionTypeAsyncDAO, self).__init__()


class SQlAlchemyRedemptionConversionTypeAsyncDAO(RedemptionConversionTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        RedemptionConversionTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("redemption_conversion_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("redemption_conversion_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> RedemptionConversionType | dict[str, RedemptionConversionType] | None:
        if cfi is None:
            convtypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                convtype = RedemptionConversionType(getattr(row, self.get_column_name("cfi")))
                convtype.name = getattr(row, self.get_column_name("name"))
                convtypes[convtype.cfi] = convtype
            return convtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            convtype = None
            if row is not None:
                convtype = RedemptionConversionType(getattr(row, self.get_column_name("cfi")))
                convtype.name = getattr(row, self.get_column_name("name"))
            return convtype

    @async_timed
    async def create(self, convtypes: list[RedemptionConversionType]) -> None:
        if len(convtypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): convtype.cfi,
                                                self.get_column_name("name"): convtype.name
                                               } for convtype in convtypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, convtypes: list[RedemptionConversionType]) -> None:
        if len(convtypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": convtype.cfi,
                                           "name": convtype.name
                                          } for convtype in convtypes])

    @async_timed
    async def delete(self, convtypes: list[IncomeType]) -> None:
        if len(convtypes) > 0:
            cfi = [convtype.cfi for convtype in convtypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class DistributionTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DistributionTypeDAO, self).__init__()


class SQlAlchemyDistributionTypeDAO(DistributionTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DistributionTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("distribution_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("distribution_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> DistributionType | dict[str, DistributionType] | None:
        if cfi is None:
            disttypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                disttype = DistributionType(getattr(row, self.get_column_name("cfi")))
                disttype.name = getattr(row, self.get_column_name("name"))
                disttypes[disttype.cfi] = disttype
            return disttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            disttype = None
            if row is not None:
                disttype = DistributionType(getattr(row, self.get_column_name("cfi")))
                disttype.name = getattr(row, self.get_column_name("name"))
            return disttype

    @timed
    def create(self, disttypes: list[DistributionType]) -> None:
        if len(disttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): disttype.cfi,
                                                self.get_column_name("name"): disttype.name
                                               } for disttype in disttypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, disttypes: list[DistributionType]) -> None:
        if len(disttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": disttype.cfi,
                                     "name": disttype.name
                                    } for disttype in disttypes])

    @timed
    def delete(self, disttypes: list[DistributionType]) -> None:
        if len(disttypes) > 0:
            cfi = [disttype.cfi for disttype in disttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class DistributionTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DistributionTypeAsyncDAO, self).__init__()


class SQlAlchemyDistributionTypeAsyncDAO(DistributionTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DistributionTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("distribution_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("distribution_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> DistributionType | dict[str, DistributionType] | None:
        if cfi is None:
            disttypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                disttype = DistributionType(getattr(row, self.get_column_name("cfi")))
                disttype.name = getattr(row, self.get_column_name("name"))
                disttypes[disttype.cfi] = disttype
            return disttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            disttype = None
            if row is not None:
                disttype = DistributionType(getattr(row, self.get_column_name("cfi")))
                disttype.name = getattr(row, self.get_column_name("name"))
            return disttype

    @async_timed
    async def create(self, disttypes: list[DistributionType]) -> None:
        if len(disttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): disttype.cfi,
                                                self.get_column_name("name"): disttype.name
                                               } for disttype in disttypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, disttypes: list[DistributionType]) -> None:
        if len(disttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": disttype.cfi,
                                           "name": disttype.name
                                          } for disttype in disttypes])

    @async_timed
    async def delete(self, disttypes: list[DistributionType]) -> None:
        if len(disttypes) > 0:
            cfi = [disttype.cfi for disttype in disttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class DistributionPolicyDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DistributionPolicyDAO, self).__init__()


class SQlAlchemyDistributionPolicyDAO(DistributionPolicyDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DistributionPolicyDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("distribution_policy"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("distribution_policy_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> DistributionPolicy | dict[str, DistributionPolicy] | None:
        if cfi is None:
            distpolicies = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                distpolicy = DistributionPolicy(getattr(row, self.get_column_name("cfi")))
                distpolicy.name = getattr(row, self.get_column_name("name"))
                distpolicies[distpolicy.cfi] = distpolicy
            return distpolicies
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            distpolicy = None
            if row is not None:
                distpolicy = DistributionPolicy(getattr(row, self.get_column_name("cfi")))
                distpolicy.name = getattr(row, self.get_column_name("name"))
            return distpolicy

    @timed
    def create(self, distpolicies: list[DistributionPolicy]) -> None:
        if len(distpolicies) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): distpolicy.cfi,
                                                self.get_column_name("name"): distpolicy.name
                                               } for distpolicy in distpolicies])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, distpolicies: list[DistributionPolicy]) -> None:
        if len(distpolicies) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": distpolicy.cfi,
                                     "name": distpolicy.name
                                    } for distpolicy in distpolicies])

    @timed
    def delete(self, distpolicies: list[DistributionType]) -> None:
        if len(distpolicies) > 0:
            cfi = [distpolicy.cfi for distpolicy in distpolicies]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class DistributionPolicyAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DistributionPolicyAsyncDAO, self).__init__()


class SQlAlchemyDistributionPolicyAsyncDAO(DistributionPolicyAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DistributionPolicyAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("distribution_policy"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("distribution_policy_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> DistributionPolicy | dict[str, DistributionPolicy] | None:
        if cfi is None:
            distpolicies = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                distpolicy = DistributionPolicy(getattr(row, self.get_column_name("cfi")))
                distpolicy.name = getattr(row, self.get_column_name("name"))
                distpolicies[distpolicy.cfi] = distpolicy
            return distpolicies
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            distpolicy = None
            if row is not None:
                distpolicy = DistributionPolicy(getattr(row, self.get_column_name("cfi")))
                distpolicy.name = getattr(row, self.get_column_name("name"))
            return distpolicy

    @async_timed
    async def create(self, distpolicies: list[DistributionPolicy]) -> None:
        if len(distpolicies) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): distpolicy.cfi,
                                                self.get_column_name("name"): distpolicy.name
                                               } for distpolicy in distpolicies])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, distpolicies: list[DistributionPolicy]) -> None:
        if len(distpolicies) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": distpolicy.cfi,
                                           "name": distpolicy.name
                                          } for distpolicy in distpolicies])

    @async_timed
    async def delete(self, distpolicies: list[DistributionType]) -> None:
        if len(distpolicies) > 0:
            cfi = [distpolicy.cfi for distpolicy in distpolicies]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class ClosedOpenEndDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ClosedOpenEndDAO, self).__init__()


class SQlAlchemyClosedOpenEndDAO(ClosedOpenEndDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        ClosedOpenEndDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("closed_open_end"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("closed_open_end_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> ClosedOpenEnd | dict[str, ClosedOpenEnd] | None:
        if cfi is None:
            ends = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                end = ClosedOpenEnd(getattr(row, self.get_column_name("cfi")))
                end.name = getattr(row, self.get_column_name("name"))
                ends[end.cfi] = end
            return ends
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            end = None
            if row is not None:
                end = ClosedOpenEnd(getattr(row, self.get_column_name("cfi")))
                end.name = getattr(row, self.get_column_name("name"))
            return end

    @timed
    def create(self, ends: list[ClosedOpenEnd]) -> None:
        if len(ends) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): end.cfi,
                                                self.get_column_name("name"): end.name
                                               } for end in ends])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, ends: list[ClosedOpenEnd]) -> None:
        if len(ends) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": end.cfi,
                                     "name": end.name
                                    } for end in ends])

    @timed
    def delete(self, ends: list[ClosedOpenEnd]) -> None:
        if len(ends) > 0:
            cfi = [end.cfi for end in ends]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class ClosedOpenEndAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ClosedOpenEndAsyncDAO, self).__init__()


class SQlAlchemyClosedOpenEndAsyncDAO(ClosedOpenEndAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        ClosedOpenEndAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("closed_open_end"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("closed_open_end_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> ClosedOpenEnd | dict[str, ClosedOpenEnd] | None:
        if cfi is None:
            ends = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                end = ClosedOpenEnd(getattr(row, self.get_column_name("cfi")))
                end.name = getattr(row, self.get_column_name("name"))
                ends[end.cfi] = end
            return ends
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            end = None
            if row is not None:
                end = ClosedOpenEnd(getattr(row, self.get_column_name("cfi")))
                end.name = getattr(row, self.get_column_name("name"))
            return end

    @async_timed
    async def create(self, ends: list[ClosedOpenEnd]) -> None:
        if len(ends) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): end.cfi,
                                                self.get_column_name("name"): end.name
                                               } for end in ends])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, ends: list[ClosedOpenEnd]) -> None:
        if len(ends) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": end.cfi,
                                           "name": end.name
                                          } for end in ends])

    @async_timed
    async def delete(self, ends: list[ClosedOpenEnd]) -> None:
        if len(ends) > 0:
            cfi = [end.cfi for end in ends]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class GuaranteeTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GuaranteeTypeDAO, self).__init__()


class SQlAlchemyGuaranteeTypeDAO(GuaranteeTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        GuaranteeTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("guarantee_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("guarantee_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> GuaranteeType | dict[str, GuaranteeType] | None:
        if cfi is None:
            guartypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                guartype = GuaranteeType(getattr(row, self.get_column_name("cfi")))
                guartype.name = getattr(row, self.get_column_name("name"))
                guartypes[guartype.cfi] = guartype
            return guartypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            guartype = None
            if row is not None:
                guartype = GuaranteeType(getattr(row, self.get_column_name("cfi")))
                guartype.name = getattr(row, self.get_column_name("name"))
            return guartype

    @timed
    def create(self, guartypes: list[GuaranteeType]) -> None:
        if len(guartypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): guartype.cfi,
                                                self.get_column_name("name"): guartype.name
                                               } for guartype in guartypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, guartypes: list[GuaranteeType]) -> None:
        if len(guartypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": guartype.cfi,
                                     "name": guartype.name
                                    } for guartype in guartypes])

    @timed
    def delete(self, guartypes: list[GuaranteeType]) -> None:
        if len(guartypes) > 0:
            cfi = [guartype.cfi for guartype in guartypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class GuaranteeTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GuaranteeTypeAsyncDAO, self).__init__()


class SQlAlchemyGuaranteeTypeAsyncDAO(GuaranteeTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        GuaranteeTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("guarantee_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("guarantee_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> GuaranteeType | dict[str, GuaranteeType] | None:
        if cfi is None:
            guartypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                guartype = GuaranteeType(getattr(row, self.get_column_name("cfi")))
                guartype.name = getattr(row, self.get_column_name("name"))
                guartypes[guartype.cfi] = guartype
            return guartypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            guartype = None
            if row is not None:
                guartype = GuaranteeType(getattr(row, self.get_column_name("cfi")))
                guartype.name = getattr(row, self.get_column_name("name"))
            return guartype

    @async_timed
    async def create(self, guartypes: list[GuaranteeType]) -> None:
        if len(guartypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): guartype.cfi,
                                                self.get_column_name("name"): guartype.name
                                               } for guartype in guartypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, guartypes: list[GuaranteeType]) -> None:
        if len(guartypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                     "cfi": guartype.cfi,
                                     "name": guartype.name
                                    } for guartype in guartypes])

    @async_timed
    async def delete(self, guartypes: list[GuaranteeType]) -> None:
        if len(guartypes) > 0:
            cfi = [guartype.cfi for guartype in guartypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class InterestTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InterestTypeDAO, self).__init__()


class SQlAlchemyInterestTypeDAO(InterestTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InterestTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("interest_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("interest_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> InterestType | dict[str, InterestType] | None:
        if cfi is None:
            inttypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                inttype = InterestType(getattr(row, self.get_column_name("cfi")))
                inttype.name = getattr(row, self.get_column_name("name"))
                inttypes[inttype.cfi] = inttype
            return inttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            inttype = None
            if row is not None:
                inttype = InterestType(getattr(row, self.get_column_name("cfi")))
                inttype.name = getattr(row, self.get_column_name("name"))
            return inttype

    @timed
    def create(self, inttypes: list[InterestType]) -> None:
        if len(inttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): inttype.cfi,
                                                self.get_column_name("name"): inttype.name
                                               } for inttype in inttypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, inttypes: list[InterestType]) -> None:
        if len(inttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": inttype.cfi,
                                     "name": inttype.name
                                    } for inttype in inttypes])

    @timed
    def delete(self, inttypes: list[InterestType]) -> None:
        if len(inttypes) > 0:
            cfi = [inttype.cfi for inttype in inttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class InterestTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(InterestTypeAsyncDAO, self).__init__()


class SQlAlchemyInterestTypeAsyncDAO(InterestTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        InterestTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("interest_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("interest_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> InterestType | dict[str, InterestType] | None:
        if cfi is None:
            inttypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                inttype = InterestType(getattr(row, self.get_column_name("cfi")))
                inttype.name = getattr(row, self.get_column_name("name"))
                inttypes[inttype.cfi] = inttype
            return inttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            inttype = None
            if row is not None:
                inttype = InterestType(getattr(row, self.get_column_name("cfi")))
                inttype.name = getattr(row, self.get_column_name("name"))
            return inttype

    @async_timed
    async def create(self, inttypes: list[InterestType]) -> None:
        if len(inttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): inttype.cfi,
                                                self.get_column_name("name"): inttype.name
                                               } for inttype in inttypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, inttypes: list[InterestType]) -> None:
        if len(inttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": inttype.cfi,
                                           "name": inttype.name
                                          } for inttype in inttypes])

    @async_timed
    async def delete(self, inttypes: list[InterestType]) -> None:
        if len(inttypes) > 0:
            cfi = [inttype.cfi for inttype in inttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class RedemptionReimbursementTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RedemptionReimbursementTypeDAO, self).__init__()


class SQlAlchemyRedemptionReimbursementTypeDAO(RedemptionReimbursementTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        RedemptionReimbursementTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("redemption_reimbursement_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("redemption_reimbursement_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> RedemptionReimbursementType | dict[str, RedemptionReimbursementType] | None:
        if cfi is None:
            reimbtypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                reimbtype = RedemptionReimbursementType(getattr(row, self.get_column_name("cfi")))
                reimbtype.name = getattr(row, self.get_column_name("name"))
                reimbtypes[reimbtype.cfi] = reimbtype
            return reimbtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            reimbtype = None
            if row is not None:
                reimbtype = RedemptionReimbursementType(getattr(row, self.get_column_name("cfi")))
                reimbtype.name = getattr(row, self.get_column_name("name"))
            return reimbtype

    @timed
    def create(self, reimbtypes: list[RedemptionReimbursementType]) -> None:
        if len(reimbtypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): reimbtype.cfi,
                                                self.get_column_name("name"): reimbtype.name
                                               } for reimbtype in reimbtypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, reimbtypes: list[RedemptionReimbursementType]) -> None:
        if len(reimbtypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": reimbtype.cfi,
                                     "name": reimbtype.name
                                    } for reimbtype in reimbtypes])

    @timed
    def delete(self, reimbtypes: list[RedemptionReimbursementType]) -> None:
        if len(reimbtypes) > 0:
            cfi = [reimbtype.cfi for reimbtype in reimbtypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class RedemptionReimbursementTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RedemptionReimbursementTypeAsyncDAO, self).__init__()


class SQlAlchemyRedemptionReimbursementTypeAsyncDAO(RedemptionReimbursementTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        RedemptionReimbursementTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("redemption_reimbursement_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("redemption_reimbursement_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> RedemptionReimbursementType | dict[str, RedemptionReimbursementType] | None:
        if cfi is None:
            reimbtypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                reimbtype = RedemptionReimbursementType(getattr(row, self.get_column_name("cfi")))
                reimbtype.name = getattr(row, self.get_column_name("name"))
                reimbtypes[reimbtype.cfi] = reimbtype
            return reimbtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            reimbtype = None
            if row is not None:
                reimbtype = RedemptionReimbursementType(getattr(row, self.get_column_name("cfi")))
                reimbtype.name = getattr(row, self.get_column_name("name"))
            return reimbtype

    @async_timed
    async def create(self, reimbtypes: list[RedemptionReimbursementType]) -> None:
        if len(reimbtypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): reimbtype.cfi,
                                                self.get_column_name("name"): reimbtype.name
                                               } for reimbtype in reimbtypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, reimbtypes: list[RedemptionReimbursementType]) -> None:
        if len(reimbtypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": reimbtype.cfi,
                                           "name": reimbtype.name
                                          } for reimbtype in reimbtypes])

    @async_timed
    async def delete(self, reimbtypes: list[RedemptionReimbursementType]) -> None:
        if len(reimbtypes) > 0:
            cfi = [reimbtype.cfi for reimbtype in reimbtypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class SecurityTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SecurityTypeDAO, self).__init__()


class SQlAlchemySecurityTypeDAO(SecurityTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        SecurityTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("security_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("security_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> SecurityType | dict[str, SecurityType] | None:
        if cfi is None:
            sectypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                sectype = SecurityType(getattr(row, self.get_column_name("cfi")))
                sectype.name = getattr(row, self.get_column_name("name"))
                sectypes[sectype.cfi] = sectype
            return sectypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            sectype = None
            if row is not None:
                sectype = SecurityType(getattr(row, self.get_column_name("cfi")))
                sectype.name = getattr(row, self.get_column_name("name"))
            return sectype

    @timed
    def create(self, sectypes: list[SecurityType]) -> None:
        if len(sectypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): sectype.cfi,
                                                self.get_column_name("name"): sectype.name
                                               } for sectype in sectypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, sectypes: list[SecurityType]) -> None:
        if len(sectypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": sectype.cfi,
                                     "name": sectype.name
                                    } for sectype in sectypes])

    @timed
    def delete(self, sectypes: list[SecurityType]) -> None:
        if len(sectypes) > 0:
            cfi = [sectype.cfi for sectype in sectypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class SecurityTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SecurityTypeAsyncDAO, self).__init__()


class SQlAlchemySecurityTypeAsyncDAO(SecurityTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        SecurityTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("security_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("security_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> SecurityType | dict[str, SecurityType] | None:
        if cfi is None:
            sectypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                sectype = SecurityType(getattr(row, self.get_column_name("cfi")))
                sectype.name = getattr(row, self.get_column_name("name"))
                sectypes[sectype.cfi] = sectype
            return sectypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            sectype = None
            if row is not None:
                sectype = SecurityType(getattr(row, self.get_column_name("cfi")))
                sectype.name = getattr(row, self.get_column_name("name"))
            return sectype

    @async_timed
    async def create(self, sectypes: list[SecurityType]) -> None:
        if len(sectypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): sectype.cfi,
                                                self.get_column_name("name"): sectype.name
                                               } for sectype in sectypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, sectypes: list[SecurityType]) -> None:
        if len(sectypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": sectype.cfi,
                                           "name": sectype.name
                                          } for sectype in sectypes])

    @async_timed
    async def delete(self, sectypes: list[SecurityType]) -> None:
        if len(sectypes) > 0:
            cfi = [sectype.cfi for sectype in sectypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class OptionTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(OptionTypeDAO, self).__init__()


class SQlAlchemyOptionTypeDAO(OptionTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        OptionTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("option_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("option_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> OptionType | dict[str, OptionType] | None:
        if cfi is None:
            opttypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                opttype = OptionType(getattr(row, self.get_column_name("cfi")))
                opttype.name = getattr(row, self.get_column_name("name"))
                opttypes[opttype.cfi] = opttype
            return opttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            opttype = None
            if row is not None:
                opttype = OptionType(getattr(row, self.get_column_name("cfi")))
                opttype.name = getattr(row, self.get_column_name("name"))
            return opttype

    @timed
    def create(self, opttypes: list[OptionType]) -> None:
        if len(opttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): opttype.cfi,
                                                self.get_column_name("name"): opttype.name
                                               } for opttype in opttypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, opttypes: list[OptionType]) -> None:
        if len(opttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": opttype.cfi,
                                     "name": opttype.name
                                    } for opttype in opttypes])

    @timed
    def delete(self, opttypes: list[OptionType]) -> None:
        if len(opttypes) > 0:
            cfi = [opttype.cfi for opttype in opttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class OptionTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(OptionTypeAsyncDAO, self).__init__()


class SQlAlchemyOptionTypeAsyncDAO(OptionTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        OptionTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("option_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("option_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> OptionType | dict[str, OptionType] | None:
        if cfi is None:
            opttypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                opttype = OptionType(getattr(row, self.get_column_name("cfi")))
                opttype.name = getattr(row, self.get_column_name("name"))
                opttypes[opttype.cfi] = opttype
            return opttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            opttype = None
            if row is not None:
                opttype = OptionType(getattr(row, self.get_column_name("cfi")))
                opttype.name = getattr(row, self.get_column_name("name"))
            return opttype

    @async_timed
    async def create(self, opttypes: list[OptionType]) -> None:
        if len(opttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): opttype.cfi,
                                                self.get_column_name("name"): opttype.name
                                               } for opttype in opttypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, opttypes: list[OptionType]) -> None:
        if len(opttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": opttype.cfi,
                                           "name": opttype.name
                                          } for opttype in opttypes])

    @async_timed
    async def delete(self, opttypes: list[OptionType]) -> None:
        if len(opttypes) > 0:
            cfi = [opttype.cfi for opttype in opttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class WarrantTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(WarrantTypeDAO, self).__init__()


class SQlAlchemyWarrantTypeDAO(WarrantTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        WarrantTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("warrant_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("warrant_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> WarrantType | dict[str, WarrantType] | None:
        if cfi is None:
            wartypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                wartype = WarrantType(getattr(row, self.get_column_name("cfi")))
                wartype.name = getattr(row, self.get_column_name("name"))
                wartypes[wartype.cfi] = wartype
            return wartypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            wartype = None
            if row is not None:
                wartype = WarrantType(getattr(row, self.get_column_name("cfi")))
                wartype.name = getattr(row, self.get_column_name("name"))
            return wartype

    @timed
    def create(self, wartypes: list[WarrantType]) -> None:
        if len(wartypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): wartype.cfi,
                                                self.get_column_name("name"): wartype.name
                                               } for wartype in wartypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, wartypes: list[WarrantType]) -> None:
        if len(wartypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": wartype.cfi,
                                     "name": wartype.name
                                    } for wartype in wartypes])

    @timed
    def delete(self, wartypes: list[WarrantType]) -> None:
        if len(wartypes) > 0:
            cfi = [wartype.cfi for wartype in wartypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class WarrantTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(WarrantTypeAsyncDAO, self).__init__()


class SQlAlchemyWarrantTypeAsyncDAO(WarrantTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        WarrantTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("warrant_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("warrant_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> WarrantType | dict[str, WarrantType] | None:
        if cfi is None:
            wartypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                wartype = WarrantType(getattr(row, self.get_column_name("cfi")))
                wartype.name = getattr(row, self.get_column_name("name"))
                wartypes[wartype.cfi] = wartype
            return wartypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            wartype = None
            if row is not None:
                wartype = WarrantType(getattr(row, self.get_column_name("cfi")))
                wartype.name = getattr(row, self.get_column_name("name"))
            return wartype

    @async_timed
    async def create(self, wartypes: list[WarrantType]) -> None:
        if len(wartypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): wartype.cfi,
                                                self.get_column_name("name"): wartype.name
                                               } for wartype in wartypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, wartypes: list[WarrantType]) -> None:
        if len(wartypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": wartype.cfi,
                                           "name": wartype.name
                                          } for wartype in wartypes])

    @async_timed
    async def delete(self, wartypes: list[WarrantType]) -> None:
        if len(wartypes) > 0:
            cfi = [wartype.cfi for wartype in wartypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class TerminationDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(TerminationDAO, self).__init__()


class SQlAlchemyTerminationDAO(TerminationDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        TerminationDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("termination"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("termination_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> Termination | dict[str, Termination] | None:
        if cfi is None:
            terms = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                term = Termination(getattr(row, self.get_column_name("cfi")))
                term.name = getattr(row, self.get_column_name("name"))
                terms[term.cfi] = term
            return terms
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            term = None
            if row is not None:
                term = Termination(getattr(row, self.get_column_name("cfi")))
                term.name = getattr(row, self.get_column_name("name"))
            return term

    @timed
    def create(self, terms: list[Termination]) -> None:
        if len(terms) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): term.cfi,
                                                self.get_column_name("name"): term.name
                                               } for term in terms])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, terms: list[Termination]) -> None:
        if len(terms) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": term.cfi,
                                     "name": term.name
                                    } for term in terms])

    @timed
    def delete(self, terms: list[Termination]) -> None:
        if len(terms) > 0:
            cfi = [term.cfi for term in terms]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class TerminationAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(TerminationAsyncDAO, self).__init__()


class SQlAlchemyTerminationAsyncDAO(TerminationAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        TerminationAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("termination"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("termination_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> Termination | dict[str, Termination] | None:
        if cfi is None:
            terms = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                term = Termination(getattr(row, self.get_column_name("cfi")))
                term.name = getattr(row, self.get_column_name("name"))
                terms[term.cfi] = term
            return terms
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            term = None
            if row is not None:
                term = Termination(getattr(row, self.get_column_name("cfi")))
                term.name = getattr(row, self.get_column_name("name"))
            return term

    @async_timed
    async def create(self, terms: list[Termination]) -> None:
        if len(terms) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): term.cfi,
                                                self.get_column_name("name"): term.name
                                               } for term in terms])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, terms: list[Termination]) -> None:
        if len(terms) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": term.cfi,
                                           "name": term.name
                                          } for term in terms])

    @async_timed
    async def delete(self, terms: list[Termination]) -> None:
        if len(terms) > 0:
            cfi = [term.cfi for term in terms]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class DeliveryTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DeliveryTypeDAO, self).__init__()


class SQlAlchemyDeliveryTypeDAO(DeliveryTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DeliveryTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("delivery_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("delivery_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> DeliveryType | dict[str, DeliveryType] | None:
        if cfi is None:
            deltypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                deltype = DeliveryType(getattr(row, self.get_column_name("cfi")))
                deltype.name = getattr(row, self.get_column_name("name"))
                deltypes[deltype.cfi] = deltype
            return deltypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            deltype = None
            if row is not None:
                deltype = DeliveryType(getattr(row, self.get_column_name("cfi")))
                deltype.name = getattr(row, self.get_column_name("name"))
            return deltype

    @timed
    def create(self, deltypes: list[DeliveryType]) -> None:
        if len(deltypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): deltype.cfi,
                                                self.get_column_name("name"): deltype.name
                                               } for deltype in deltypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, deltypes: list[DeliveryType]) -> None:
        if len(deltypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": deltype.cfi,
                                     "name": deltype.name
                                    } for deltype in deltypes])

    @timed
    def delete(self, deltypes: list[DeliveryType]) -> None:
        if len(deltypes) > 0:
            cfi = [deltype.cfi for deltype in deltypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class DeliveryTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DeliveryTypeAsyncDAO, self).__init__()


class SQlAlchemyDeliveryTypeAsyncDAO(DeliveryTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DeliveryTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("delivery_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("delivery_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> DeliveryType | dict[str, DeliveryType] | None:
        if cfi is None:
            deltypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                deltype = DeliveryType(getattr(row, self.get_column_name("cfi")))
                deltype.name = getattr(row, self.get_column_name("name"))
                deltypes[deltype.cfi] = deltype
            return deltypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            deltype = None
            if row is not None:
                deltype = DeliveryType(getattr(row, self.get_column_name("cfi")))
                deltype.name = getattr(row, self.get_column_name("name"))
            return deltype

    @async_timed
    async def create(self, deltypes: list[DeliveryType]) -> None:
        if len(deltypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): deltype.cfi,
                                                self.get_column_name("name"): deltype.name
                                               } for deltype in deltypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, deltypes: list[DeliveryType]) -> None:
        if len(deltypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": deltype.cfi,
                                           "name": deltype.name
                                          } for deltype in deltypes])

    @async_timed
    async def delete(self, deltypes: list[DeliveryType]) -> None:
        if len(deltypes) > 0:
            cfi = [deltype.cfi for deltype in deltypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class WeightingTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(WeightingTypeDAO, self).__init__()


class SQlAlchemyWeightingTypeDAO(WeightingTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        WeightingTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("weighting_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("weighting_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> WeightingType | dict[str, WeightingType] | None:
        if cfi is None:
            weighttypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                weighttype = WeightingType(getattr(row, self.get_column_name("cfi")))
                weighttype.name = getattr(row, self.get_column_name("name"))
                weighttypes[weighttype.cfi] = weighttype
            return weighttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            weighttype = None
            if row is not None:
                weighttype = WeightingType(getattr(row, self.get_column_name("cfi")))
                weighttype.name = getattr(row, self.get_column_name("name"))
            return weighttype

    @timed
    def create(self, weighttypes: list[WeightingType]) -> None:
        if len(weighttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): weighttype.cfi,
                                                self.get_column_name("name"): weighttype.name
                                               } for weighttype in weighttypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, weighttypes: list[WeightingType]) -> None:
        if len(weighttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": weighttype.cfi,
                                     "name": weighttype.name
                                    } for weighttype in weighttypes])

    @timed
    def delete(self, weighttypes: list[WeightingType]) -> None:
        if len(weighttypes) > 0:
            cfi = [weighttype.cfi for weighttype in weighttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class WeightingTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(WeightingTypeAsyncDAO, self).__init__()


class SQlAlchemyWeightingTypeAsyncDAO(WeightingTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        WeightingTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("weighting_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("weighting_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> WeightingType | dict[str, WeightingType] | None:
        if cfi is None:
            weighttypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                weighttype = WeightingType(getattr(row, self.get_column_name("cfi")))
                weighttype.name = getattr(row, self.get_column_name("name"))
                weighttypes[weighttype.cfi] = weighttype
            return weighttypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            weighttype = None
            if row is not None:
                weighttype = WeightingType(getattr(row, self.get_column_name("cfi")))
                weighttype.name = getattr(row, self.get_column_name("name"))
            return weighttype

    @async_timed
    async def create(self, weighttypes: list[WeightingType]) -> None:
        if len(weighttypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): weighttype.cfi,
                                                self.get_column_name("name"): weighttype.name
                                               } for weighttype in weighttypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, weighttypes: list[WeightingType]) -> None:
        if len(weighttypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": weighttype.cfi,
                                           "name": weighttype.name
                                          } for weighttype in weighttypes])

    @async_timed
    async def delete(self, weighttypes: list[WeightingType]) -> None:
        if len(weighttypes) > 0:
            cfi = [weighttype.cfi for weighttype in weighttypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class IndexReturnTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(IndexReturnTypeDAO, self).__init__()


class SQlAlchemyIndexReturnTypeDAO(IndexReturnTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        IndexReturnTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("index_return_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("index_return_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> IndexReturnType | dict[str, IndexReturnType] | None:
        if cfi is None:
            idxrettypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                idxrettype = IndexReturnType(getattr(row, self.get_column_name("cfi")))
                idxrettype.name = getattr(row, self.get_column_name("name"))
                idxrettypes[idxrettype.cfi] = idxrettype
            return idxrettypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            idxrettype = None
            if row is not None:
                idxrettype = IndexReturnType(getattr(row, self.get_column_name("cfi")))
                idxrettype.name = getattr(row, self.get_column_name("name"))
            return idxrettype

    @timed
    def create(self, idxrettypes: list[IndexReturnType]) -> None:
        if len(idxrettypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): idxrettype.cfi,
                                                self.get_column_name("name"): idxrettype.name
                                               } for idxrettype in idxrettypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, idxrettypes: list[IndexReturnType]) -> None:
        if len(idxrettypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": idxrettype.cfi,
                                     "name": idxrettype.name
                                    } for idxrettype in idxrettypes])

    @timed
    def delete(self, idxrettypes: list[IndexReturnType]) -> None:
        if len(idxrettypes) > 0:
            cfi = [idxrettype.cfi for idxrettype in idxrettypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class IndexReturnTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(IndexReturnTypeAsyncDAO, self).__init__()


class SQlAlchemyIndexReturnTypeAsyncDAO(IndexReturnTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        IndexReturnTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("index_return_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("index_return_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> IndexReturnType | dict[str, IndexReturnType] | None:
        if cfi is None:
            idxrettypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                idxrettype = IndexReturnType(getattr(row, self.get_column_name("cfi")))
                idxrettype.name = getattr(row, self.get_column_name("name"))
                idxrettypes[idxrettype.cfi] = idxrettype
            return idxrettypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            idxrettype = None
            if row is not None:
                idxrettype = IndexReturnType(getattr(row, self.get_column_name("cfi")))
                idxrettype.name = getattr(row, self.get_column_name("name"))
            return idxrettype

    @async_timed
    async def create(self, idxrettypes: list[IndexReturnType]) -> None:
        if len(idxrettypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): idxrettype.cfi,
                                                self.get_column_name("name"): idxrettype.name
                                               } for idxrettype in idxrettypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, idxrettypes: list[IndexReturnType]) -> None:
        if len(idxrettypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": idxrettype.cfi,
                                           "name": idxrettype.name
                                          } for idxrettype in idxrettypes])

    @async_timed
    async def delete(self, idxrettypes: list[IndexReturnType]) -> None:
        if len(idxrettypes) > 0:
            cfi = [idxrettype.cfi for idxrettype in idxrettypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class BasketCompositionDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BasketCompositionDAO, self).__init__()


class SQlAlchemyBasketCompositionDAO(BasketCompositionDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        BasketCompositionDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("basket_composition"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("basket_composition_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> BasketComposition | dict[str, BasketComposition] | None:
        if cfi is None:
            baskets = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                basket = BasketComposition(getattr(row, self.get_column_name("cfi")))
                basket.name = getattr(row, self.get_column_name("name"))
                baskets[basket.cfi] = basket
            return baskets
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            basket = None
            if row is not None:
                basket = BasketComposition(getattr(row, self.get_column_name("cfi")))
                basket.name = getattr(row, self.get_column_name("name"))
            return basket

    @timed
    def create(self, baskets: list[BasketComposition]) -> None:
        if len(baskets) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): basket.cfi,
                                                self.get_column_name("name"): basket.name
                                               } for basket in baskets])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, baskets: list[BasketComposition]) -> None:
        if len(baskets) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": basket.cfi,
                                     "name": basket.name
                                    } for basket in baskets])

    @timed
    def delete(self, baskets: list[BasketComposition]) -> None:
        if len(baskets) > 0:
            cfi = [basket.cfi for basket in baskets]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class BasketCompositionAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BasketCompositionAsyncDAO, self).__init__()


class SQlAlchemyBasketCompositionAsyncDAO(BasketCompositionAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        BasketCompositionAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("basket_composition"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("basket_composition_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> BasketComposition | dict[str, BasketComposition] | None:
        if cfi is None:
            baskets = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                basket = BasketComposition(getattr(row, self.get_column_name("cfi")))
                basket.name = getattr(row, self.get_column_name("name"))
                baskets[basket.cfi] = basket
            return baskets
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            basket = None
            if row is not None:
                basket = BasketComposition(getattr(row, self.get_column_name("cfi")))
                basket.name = getattr(row, self.get_column_name("name"))
            return basket

    @async_timed
    async def create(self, baskets: list[BasketComposition]) -> None:
        if len(baskets) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): basket.cfi,
                                                self.get_column_name("name"): basket.name
                                               } for basket in baskets])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, baskets: list[BasketComposition]) -> None:
        if len(baskets) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": basket.cfi,
                                           "name": basket.name
                                          } for basket in baskets])

    @async_timed
    async def delete(self, baskets: list[BasketComposition]) -> None:
        if len(baskets) > 0:
            cfi = [basket.cfi for basket in baskets]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class TimeFrequencyDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(TimeFrequencyDAO, self).__init__()


class SQlAlchemyTimeFrequencyDAO(TimeFrequencyDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        TimeFrequencyDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("time_frequency"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("time_frequency_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> TimeFrequency | dict[str, TimeFrequency] | None:
        if cfi is None:
            timefreqs = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                timefreq = TimeFrequency(getattr(row, self.get_column_name("cfi")))
                timefreq.name = getattr(row, self.get_column_name("name"))
                timefreqs[timefreq.cfi] = timefreq
            return timefreqs
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            timefreq = None
            if row is not None:
                timefreq = TimeFrequency(getattr(row, self.get_column_name("cfi")))
                timefreq.name = getattr(row, self.get_column_name("name"))
            return timefreq

    @timed
    def create(self, timefreqs: list[TimeFrequency]) -> None:
        if len(timefreqs) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): timefreq.cfi,
                                                self.get_column_name("name"): timefreq.name
                                               } for timefreq in timefreqs])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, timefreqs: list[TimeFrequency]) -> None:
        if len(timefreqs) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": timefreq.cfi,
                                     "name": timefreq.name
                                    } for timefreq in timefreqs])

    @timed
    def delete(self, timefreqs: list[TimeFrequency]) -> None:
        if len(timefreqs) > 0:
            cfi = [timefreq.cfi for timefreq in timefreqs]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class TimeFrequencyAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(TimeFrequencyAsyncDAO, self).__init__()


class SQlAlchemyTimeFrequencyAsyncDAO(TimeFrequencyAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        TimeFrequencyAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("time_frequency"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("time_frequency_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> TimeFrequency | dict[str, TimeFrequency] | None:
        if cfi is None:
            timefreqs = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                timefreq = TimeFrequency(getattr(row, self.get_column_name("cfi")))
                timefreq.name = getattr(row, self.get_column_name("name"))
                timefreqs[timefreq.cfi] = timefreq
            return timefreqs
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            timefreq = None
            if row is not None:
                timefreq = TimeFrequency(getattr(row, self.get_column_name("cfi")))
                timefreq.name = getattr(row, self.get_column_name("name"))
            return timefreq

    @async_timed
    async def create(self, timefreqs: list[TimeFrequency]) -> None:
        if len(timefreqs) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): timefreq.cfi,
                                                self.get_column_name("name"): timefreq.name
                                               } for timefreq in timefreqs])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, timefreqs: list[TimeFrequency]) -> None:
        if len(timefreqs) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": timefreq.cfi,
                                           "name": timefreq.name
                                          } for timefreq in timefreqs])

    @async_timed
    async def delete(self, timefreqs: list[TimeFrequency]) -> None:
        if len(timefreqs) > 0:
            cfi = [timefreq.cfi for timefreq in timefreqs]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class EquityTypeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(EquityTypeDAO, self).__init__()


class SQlAlchemyEquityTypeDAO(EquityTypeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        EquityTypeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("equity_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("equity_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, cfi: str | None = None) -> EquityType | dict[str, EquityType] | None:
        if cfi is None:
            eqtypes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                eqtype = EquityType(getattr(row, self.get_column_name("cfi")))
                eqtype.name = getattr(row, self.get_column_name("name"))
                eqtypes[eqtype.cfi] = eqtype
            return eqtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            eqtype = None
            if row is not None:
                eqtype = EquityType(getattr(row, self.get_column_name("cfi")))
                eqtype.name = getattr(row, self.get_column_name("name"))
            return eqtype

    @timed
    def create(self, eqtypes: list[EquityType]) -> None:
        if len(eqtypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): eqtype.cfi,
                                                self.get_column_name("name"): eqtype.name
                                               } for eqtype in eqtypes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, eqtypes: list[EquityType]) -> None:
        if len(eqtypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "cfi": eqtype.cfi,
                                     "name": eqtype.name
                                    } for eqtype in eqtypes])

    @timed
    def delete(self, eqtypes: list[EquityType]) -> None:
        if len(eqtypes) > 0:
            cfi = [eqtype.cfi for eqtype in eqtypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class EquityTypeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(EquityTypeAsyncDAO, self).__init__()


class SQlAlchemyEquityTypeAsyncDAO(EquityTypeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        EquityTypeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("equity_type"),
                                   self._metadata,
                                   Column(self.get_column_name("cfi"), String(1), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("cfi"), name=self.get_key_name("equity_type_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, cfi: str | None = None) -> EquityType | dict[str, EquityType] | None:
        if cfi is None:
            eqtypes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                eqtype = EquityType(getattr(row, self.get_column_name("cfi")))
                eqtype.name = getattr(row, self.get_column_name("name"))
                eqtypes[eqtype.cfi] = eqtype
            return eqtypes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == cfi)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            eqtype = None
            if row is not None:
                eqtype = EquityType(getattr(row, self.get_column_name("cfi")))
                eqtype.name = getattr(row, self.get_column_name("name"))
            return eqtype

    @async_timed
    async def create(self, eqtypes: list[EquityType]) -> None:
        if len(eqtypes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("cfi"): eqtype.cfi,
                                                self.get_column_name("name"): eqtype.name
                                               } for eqtype in eqtypes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, eqtypes: list[EquityType]) -> None:
        if len(eqtypes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("cfi")) == bindparam("cfi")).values({
                                                                                                                              self.get_column_name("name"): bindparam("name")
                                                                                                                             })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "cfi": eqtype.cfi,
                                           "name": eqtype.name
                                          } for eqtype in eqtypes])

    @async_timed
    async def delete(self, eqtypes: list[EquityType]) -> None:
        if len(eqtypes) > 0:
            cfi = [eqtype.cfi for eqtype in eqtypes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("cfi")).in_(cfi))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)
