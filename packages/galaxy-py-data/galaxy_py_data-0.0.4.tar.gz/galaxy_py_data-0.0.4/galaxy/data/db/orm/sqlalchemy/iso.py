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

from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

Base = declarative_base()


class SQLAlchemyContinent(Base):
    """
    classdocs
    """

    __tablename__ = "iso_continent"
    iso2: Column = Column("iso2",
                          String(2),
                          nullable=False,
                          primary_key=True)
    name: Column = Column("name",
                          String(80),
                          nullable=False)

    def __str__(self) -> str:
        return self.iso2

    def __repr__(self) -> str:
        return "<SQLAlchemyContinent(iso2='{}')>".format(self.iso2)


class SQLAlchemyCountry(Base):
    """
    classdocs
    """

    __tablename__ = "iso_country"
    iso2: Column = Column("iso2",
                          String(2),
                          nullable=False,
                          primary_key=True)

    def __str__(self) -> str:
        return self.iso2

    def __repr__(self) -> str:
        return "<SQLAlchemyCountry(iso2='{}')>".format(self.iso2)


class SQLAlchemyCountryContinent(Base):
    """
    classdocs
    """

    __tablename__ = "iso_country_continent"
    country_iso2: Column = Column("country_iso2",
                                  String(2),
                                  nullable=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyCountryContinent(id='{}')>".format(self.id)


class SQLAlchemyCurrency(Base):
    """
    classdocs
    """

    __tablename__ = "iso_currency"

    def __str__(self) -> str:
        return self.iso3

    def __repr__(self) -> str:
        return "<SQLAlchemyCurrency(iso3='{}')>".format(self.iso3)


class SQLAlchemyCountryCurrency(Base):
    """
    classdocs
    """

    __tablename__ = "iso_country_currency"
    country_iso2: Column = Column("country_iso2",
                                  String(2),
                                  nullable=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyCountryCurrency(id='{}')>".format(self.id)


class SQLAlchemyPhonePrefix(Base):
    """
    classdocs
    """

    __tablename__ = "iso_phone_prefix"

    def __str__(self) -> str:
        return self.iso3

    def __repr__(self) -> str:
        return "<SQLAlchemyPhonePrefix(id='{}')>".format(self.id)


class SQLAlchemyLanguage(Base):
    """
    classdocs
    """

    __tablename__ = "iso_language"

    def __str__(self) -> str:
        return self.iso3

    def __repr__(self) -> str:
        return "<SQLAlchemyLanguage(iso3='{}')>".format(self.iso3)


class SQLAlchemyMarketExchange(Base):
    """
    classdocs
    """

    __tablename__ = "iso_market_exchange"

    def __str__(self) -> str:
        return self.mic

    def __repr__(self) -> str:
        return "<SQLAlchemyMarketExchange(mic='{}')>".format(self.mic)
