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
from sqlalchemy.schema import Table,                                    \
                              Column,                                   \
                              PrimaryKeyConstraint,                     \
                              ForeignKeyConstraint
from sqlalchemy.sql.expression import select,                           \
                                      delete,                           \
                                      insert,                           \
                                      update
from sqlalchemy.sql.sqltypes import String,                             \
                                    Integer
from sqlalchemy.sql import bindparam

from galaxy.data.db.db import DAO,                                      \
                              SQLAlchemyDAO,                            \
                              AsyncDAO,                                 \
                              SQLAlchemyAsyncDAO
from galaxy.data.model.institution import Bank,                         \
                                          BrokerGroup,                  \
                                          Broker,                       \
                                          RegulatoryAuthority,          \
                                          CentralBank,                  \
                                          CentralSecuritiesDepository,  \
                                          Subcustodian
from galaxy.perfo.decorator import timed,                               \
                                   async_timed


class BankDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BankDAO, self).__init__()


class SQlAlchemyBankDAO(BankDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        BankDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("bank"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("bic"), String(11), nullable=True),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("sort_code"), String(6), nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("building"), String(80), nullable=True),
                                   Column(self.get_column_name("street_num"), String(10), nullable=True),
                                   Column(self.get_column_name("street"), String(120), nullable=True),
                                   Column(self.get_column_name("address1"), String(250), nullable=True),
                                   Column(self.get_column_name("address2"), String(250), nullable=True),
                                   Column(self.get_column_name("address3"), String(250), nullable=True),
                                   Column(self.get_column_name("zip_code"), String(10), nullable=True),
                                   Column(self.get_column_name("city"), String(80), nullable=True),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("phone"), String(20), nullable=True),
                                   Column(self.get_column_name("phone_prefix_id"), Integer, nullable=True),
                                   Column(self.get_column_name("fax"), String(20), nullable=True),
                                   Column(self.get_column_name("fax_prefix_id"), Integer, nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("bank_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("bank_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("phone_prefix_id")],
                                                        ["{}.{}".format(self.get_table_name("phone_prefix", "iso"), self.get_column_name("id"))],
                                                        name=self.get_key_name("bank_fk2")),
                                   ForeignKeyConstraint([self.get_column_name("fax_prefix_id")],
                                                        ["{}.{}".format(self.get_table_name("phone_prefix", "iso"), self.get_column_name("id"))],
                                                        name=self.get_key_name("bank_fk3")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> Bank | dict[int, Bank] | None:
        if id_ is None:
            banks = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                bank = Bank(getattr(row, self.get_column_name("id")))
                bank.bic = getattr(row, self.get_column_name("bic"))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.sort_code = getattr(row, self.get_column_name("sort_code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.building = getattr(row, self.get_column_name("building"))
                bank.street_num = getattr(row, self.get_column_name("street_num"))
                bank.street = getattr(row, self.get_column_name("street"))
                bank.address1 = getattr(row, self.get_column_name("address1"))
                bank.address2 = getattr(row, self.get_column_name("address2"))
                bank.address3 = getattr(row, self.get_column_name("address3"))
                bank.zip_code = getattr(row, self.get_column_name("zip_code"))
                bank.city = getattr(row, self.get_column_name("city"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.phone = getattr(row, self.get_column_name("phone"))
                bank.phone_prefix_id = getattr(row, self.get_column_name("phone_prefix_id"))
                bank.fax = getattr(row, self.get_column_name("fax"))
                bank.fax_prefix_id = getattr(row, self.get_column_name("fax_prefix_id"))
                bank.website = getattr(row, self.get_column_name("website"))
                banks[bank.id] = bank
            return banks
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            bank = None
            if row is not None:
                bank = Bank(getattr(row, self.get_column_name("id")))
                bank.bic = getattr(row, self.get_column_name("bic"))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.sort_code = getattr(row, self.get_column_name("sort_code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.building = getattr(row, self.get_column_name("building"))
                bank.street_num = getattr(row, self.get_column_name("street_num"))
                bank.street = getattr(row, self.get_column_name("street"))
                bank.address1 = getattr(row, self.get_column_name("address1"))
                bank.address2 = getattr(row, self.get_column_name("address2"))
                bank.address3 = getattr(row, self.get_column_name("address3"))
                bank.zip_code = getattr(row, self.get_column_name("zip_code"))
                bank.city = getattr(row, self.get_column_name("city"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.phone = getattr(row, self.get_column_name("phone"))
                bank.phone_prefix_id = getattr(row, self.get_column_name("phone_prefix_id"))
                bank.fax = getattr(row, self.get_column_name("fax"))
                bank.fax_prefix_id = getattr(row, self.get_column_name("fax_prefix_id"))
                bank.website = getattr(row, self.get_column_name("website"))
            return bank

    @timed
    def create(self, banks: list[Bank]) -> None:
        if len(banks) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): bank.id,
                                                self.get_column_name("bic"): bank.bic,
                                                self.get_column_name("code"): bank.code,
                                                self.get_column_name("sort_code"): bank.sort_code,
                                                self.get_column_name("name"): bank.name,
                                                self.get_column_name("building"): bank.building,
                                                self.get_column_name("street_num"): bank.street_num,
                                                self.get_column_name("street"): bank.street,
                                                self.get_column_name("address1"): bank.address1,
                                                self.get_column_name("address2"): bank.address2,
                                                self.get_column_name("address3"): bank.address3,
                                                self.get_column_name("zip_code"): bank.zip_code,
                                                self.get_column_name("country_iso2"): bank.country_iso2,
                                                self.get_column_name("phone"): bank.phone,
                                                self.get_column_name("phone_prefix_id"): bank.phone_prefix_id,
                                                self.get_column_name("fax"): bank.fax,
                                                self.get_column_name("fax_prefix_id"): bank.fax_prefix_id,
                                                self.get_column_name("website"): bank.website
                                               } for bank in banks])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, banks: list[Bank]) -> None:
        if len(banks) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("bic"): bindparam("bic"),
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("sort_code"): bindparam("sort_code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("building"): bindparam("building"),
                                                                                                                             self.get_column_name("street_num"): bindparam("street_num"),
                                                                                                                             self.get_column_name("street"): bindparam("street"),
                                                                                                                             self.get_column_name("address1"): bindparam("address1"),
                                                                                                                             self.get_column_name("address2"): bindparam("address2"),
                                                                                                                             self.get_column_name("address3"): bindparam("address3"),
                                                                                                                             self.get_column_name("zip_code"): bindparam("zip_code"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("phone"): bindparam("phone"),
                                                                                                                             self.get_column_name("phone_prefix_id"): bindparam("phone_prefix_id"),
                                                                                                                             self.get_column_name("fax"): bindparam("fax"),
                                                                                                                             self.get_column_name("fax_prefix_id"): bindparam("fax_prefix_id"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": bank.id,
                                     "bic": bank.bic,
                                     "code": bank.code,
                                     "sort_code": bank.sort_code,
                                     "name": bank.name,
                                     "building": bank.building,
                                     "street_num": bank.street_num,
                                     "street": bank.street,
                                     "address1": bank.address1,
                                     "address2": bank.address2,
                                     "address3": bank.address3,
                                     "zip_code": bank.zip_code,
                                     "country_iso2": bank.country_iso2,
                                     "phone": bank.phone,
                                     "phone_prefix_id": bank.phone_prefix_id,
                                     "fax": bank.fax,
                                     "fax_prefix_id": bank.fax_prefix_id,
                                     "website": bank.website
                                    } for bank in banks])

    @timed
    def delete(self, banks: list[Bank]) -> None:
        if len(banks) > 0:
            ids = [bank.id for bank in banks]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class BankAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BankAsyncDAO, self).__init__()


class SQlAlchemyBankAsyncDAO(BankAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        BankAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("bank"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("bic"), String(11), nullable=True),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("sort_code"), String(6), nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("building"), String(80), nullable=True),
                                   Column(self.get_column_name("street_num"), String(10), nullable=True),
                                   Column(self.get_column_name("street"), String(120), nullable=True),
                                   Column(self.get_column_name("address1"), String(250), nullable=True),
                                   Column(self.get_column_name("address2"), String(250), nullable=True),
                                   Column(self.get_column_name("address3"), String(250), nullable=True),
                                   Column(self.get_column_name("zip_code"), String(10), nullable=True),
                                   Column(self.get_column_name("city"), String(80), nullable=True),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("phone"), String(20), nullable=True),
                                   Column(self.get_column_name("phone_prefix_id"), Integer, nullable=True),
                                   Column(self.get_column_name("fax"), String(20), nullable=True),
                                   Column(self.get_column_name("fax_prefix_id"), Integer, nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("bank_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("bank_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("phone_prefix_id")],
                                                        ["{}.{}".format(self.get_table_name("phone_prefix", "iso"), self.get_column_name("id"))],
                                                        name=self.get_key_name("bank_fk2")),
                                   ForeignKeyConstraint([self.get_column_name("fax_prefix_id")],
                                                        ["{}.{}".format(self.get_table_name("phone_prefix", "iso"), self.get_column_name("id"))],
                                                        name=self.get_key_name("bank_fk3")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> Bank | dict[int, Bank] | None:
        if id_ is None:
            banks = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                bank = Bank(getattr(row, self.get_column_name("id")))
                bank.bic = getattr(row, self.get_column_name("bic"))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.sort_code = getattr(row, self.get_column_name("sort_code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.building = getattr(row, self.get_column_name("building"))
                bank.street_num = getattr(row, self.get_column_name("street_num"))
                bank.street = getattr(row, self.get_column_name("street"))
                bank.address1 = getattr(row, self.get_column_name("address1"))
                bank.address2 = getattr(row, self.get_column_name("address2"))
                bank.address3 = getattr(row, self.get_column_name("address3"))
                bank.zip_code = getattr(row, self.get_column_name("zip_code"))
                bank.city = getattr(row, self.get_column_name("city"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.phone = getattr(row, self.get_column_name("phone"))
                bank.phone_prefix_id = getattr(row, self.get_column_name("phone_prefix_id"))
                bank.fax = getattr(row, self.get_column_name("fax"))
                bank.fax_prefix_id = getattr(row, self.get_column_name("fax_prefix_id"))
                bank.website = getattr(row, self.get_column_name("website"))
                banks[bank.id] = bank
            return banks
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            bank = None
            if row is not None:
                bank = Bank(getattr(row, self.get_column_name("id")))
                bank.bic = getattr(row, self.get_column_name("bic"))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.sort_code = getattr(row, self.get_column_name("sort_code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.building = getattr(row, self.get_column_name("building"))
                bank.street_num = getattr(row, self.get_column_name("street_num"))
                bank.street = getattr(row, self.get_column_name("street"))
                bank.address1 = getattr(row, self.get_column_name("address1"))
                bank.address2 = getattr(row, self.get_column_name("address2"))
                bank.address3 = getattr(row, self.get_column_name("address3"))
                bank.zip_code = getattr(row, self.get_column_name("zip_code"))
                bank.city = getattr(row, self.get_column_name("city"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.phone = getattr(row, self.get_column_name("phone"))
                bank.phone_prefix_id = getattr(row, self.get_column_name("phone_prefix_id"))
                bank.fax = getattr(row, self.get_column_name("fax"))
                bank.fax_prefix_id = getattr(row, self.get_column_name("fax_prefix_id"))
                bank.website = getattr(row, self.get_column_name("website"))
            return bank

    @async_timed
    async def create(self, banks: list[Bank]) -> None:
        if len(banks) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): bank.id,
                                                self.get_column_name("bic"): bank.bic,
                                                self.get_column_name("code"): bank.code,
                                                self.get_column_name("sort_code"): bank.sort_code,
                                                self.get_column_name("name"): bank.name,
                                                self.get_column_name("building"): bank.building,
                                                self.get_column_name("street_num"): bank.street_num,
                                                self.get_column_name("street"): bank.street,
                                                self.get_column_name("address1"): bank.address1,
                                                self.get_column_name("address2"): bank.address2,
                                                self.get_column_name("address3"): bank.address3,
                                                self.get_column_name("zip_code"): bank.zip_code,
                                                self.get_column_name("country_iso2"): bank.country_iso2,
                                                self.get_column_name("phone"): bank.phone,
                                                self.get_column_name("phone_prefix_id"): bank.phone_prefix_id,
                                                self.get_column_name("fax"): bank.fax,
                                                self.get_column_name("fax_prefix_id"): bank.fax_prefix_id,
                                                self.get_column_name("website"): bank.website
                                               } for bank in banks])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, banks: list[Bank]) -> None:
        if len(banks) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("bic"): bindparam("bic"),
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("sort_code"): bindparam("sort_code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("building"): bindparam("building"),
                                                                                                                             self.get_column_name("street_num"): bindparam("street_num"),
                                                                                                                             self.get_column_name("street"): bindparam("street"),
                                                                                                                             self.get_column_name("address1"): bindparam("address1"),
                                                                                                                             self.get_column_name("address2"): bindparam("address2"),
                                                                                                                             self.get_column_name("address3"): bindparam("address3"),
                                                                                                                             self.get_column_name("zip_code"): bindparam("zip_code"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("phone"): bindparam("phone"),
                                                                                                                             self.get_column_name("phone_prefix_id"): bindparam("phone_prefix_id"),
                                                                                                                             self.get_column_name("fax"): bindparam("fax"),
                                                                                                                             self.get_column_name("fax_prefix_id"): bindparam("fax_prefix_id"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": bank.id,
                                           "bic": bank.bic,
                                           "code": bank.code,
                                           "sort_code": bank.sort_code,
                                           "name": bank.name,
                                           "building": bank.building,
                                           "street_num": bank.street_num,
                                           "street": bank.street,
                                           "address1": bank.address1,
                                           "address2": bank.address2,
                                           "address3": bank.address3,
                                           "zip_code": bank.zip_code,
                                           "country_iso2": bank.country_iso2,
                                           "phone": bank.phone,
                                           "phone_prefix_id": bank.phone_prefix_id,
                                           "fax": bank.fax,
                                           "fax_prefix_id": bank.fax_prefix_id,
                                           "website": bank.website
                                          } for bank in banks])

    @async_timed
    async def delete(self, banks: list[Bank]) -> None:
        if len(banks) > 0:
            ids = [bank.id for bank in banks]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class BrokerGroupDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BrokerGroupDAO, self).__init__()


class SQlAlchemyBrokerGroupDAO(BrokerGroupDAO, SQLAlchemyDAO):
    """
        classdocs
        """

    def __init__(self) -> None:
        """
        Constructor
        """
        BrokerGroupDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("broker_group"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("lei"), String(20), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("broker_group_pk")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("broker_group_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> BrokerGroup | dict[int, BrokerGroup] | None:
        if id_ is None:
            groups = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                group = BrokerGroup(getattr(row, self.get_column_name("id")))
                group.code = getattr(row, self.get_column_name("code"))
                group.name = getattr(row, self.get_column_name("name"))
                group.bank_id = getattr(row, self.get_column_name("bank_id"))
                group.lei = getattr(row, self.get_column_name("lei"))
                groups[group.id] = group
            return groups
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            group = None
            if row is not None:
                group = BrokerGroup(getattr(row, self.get_column_name("id")))
                group.code = getattr(row, self.get_column_name("code"))
                group.name = getattr(row, self.get_column_name("name"))
                group.bank_id = getattr(row, self.get_column_name("bank_id"))
                group.lei = getattr(row, self.get_column_name("lei"))
            return group

    @timed
    def create(self, groups: list[BrokerGroup]) -> None:
        if len(groups) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): group.id,
                                                self.get_column_name("code"): group.code,
                                                self.get_column_name("name"): group.name,
                                                self.get_column_name("bank_id"): group.bank_id,
                                                self.get_column_name("lei"): group.lei
                                               } for group in groups])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, groups: list[BrokerGroup]) -> None:
        if len(groups) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("lei"): bindparam("lei")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": group.id,
                                     "code": group.code,
                                     "name": group.name,
                                     "bank_id": group.bank_id,
                                     "lei": group.lei
                                    } for group in groups])

    @timed
    def delete(self, groups: list[BrokerGroup]) -> None:
        if len(groups) > 0:
            ids = [group.id for group in groups]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class BrokerGroupAsyncDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BrokerGroupAsyncDAO, self).__init__()


class SQlAlchemyBrokerGroupAsyncDAO(BrokerGroupAsyncDAO, SQLAlchemyAsyncDAO):
    """
        classdocs
        """

    def __init__(self) -> None:
        """
        Constructor
        """
        BrokerGroupAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("broker_group"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("lei"), String(20), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("broker_group_pk")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("broker_group_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> BrokerGroup | dict[int, BrokerGroup] | None:
        if id_ is None:
            groups = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                group = BrokerGroup(getattr(row, self.get_column_name("id")))
                group.code = getattr(row, self.get_column_name("code"))
                group.name = getattr(row, self.get_column_name("name"))
                group.bank_id = getattr(row, self.get_column_name("bank_id"))
                group.lei = getattr(row, self.get_column_name("lei"))
                groups[group.id] = group
            return groups
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            group = None
            if row is not None:
                group = BrokerGroup(getattr(row, self.get_column_name("id")))
                group.code = getattr(row, self.get_column_name("code"))
                group.name = getattr(row, self.get_column_name("name"))
                group.bank_id = getattr(row, self.get_column_name("bank_id"))
                group.lei = getattr(row, self.get_column_name("lei"))
            return group

    @async_timed
    async def create(self, groups: list[BrokerGroup]) -> None:
        if len(groups) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): group.id,
                                                self.get_column_name("code"): group.code,
                                                self.get_column_name("name"): group.name,
                                                self.get_column_name("bank_id"): group.bank_id,
                                                self.get_column_name("lei"): group.lei
                                               } for group in groups])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, groups: list[BrokerGroup]) -> None:
        if len(groups) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("lei"): bindparam("lei")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": group.id,
                                           "code": group.code,
                                           "name": group.name,
                                           "bank_id": group.bank_id,
                                           "lei": group.lei
                                          } for group in groups])

    @async_timed
    async def delete(self, groups: list[BrokerGroup]) -> None:
        if len(groups) > 0:
            ids = [group.id for group in groups]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class BrokerDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BrokerDAO, self).__init__()


class SQlAlchemyBrokerDAO(BrokerDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        BrokerDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("broker"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("group_id"), Integer, nullable=True),
                                   Column(self.get_column_name("lei"), String(20), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("broker_pk")),
                                   ForeignKeyConstraint([self.get_column_name("group_id")],
                                                        ["{}.{}".format(self.get_table_name("broker_group", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("broker_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> Broker | dict[int, Broker] | None:
        if id_ is None:
            brokers = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                broker = Broker(getattr(row, self.get_column_name("id")))
                broker.code = getattr(row, self.get_column_name("code"))
                broker.name = getattr(row, self.get_column_name("name"))
                broker.group_id = getattr(row, self.get_column_name("group_id"))
                broker.lei = getattr(row, self.get_column_name("lei"))
                brokers[broker.id] = broker
            return brokers
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            broker = None
            if row is not None:
                broker = Broker(getattr(row, self.get_column_name("id")))
                broker.code = getattr(row, self.get_column_name("code"))
                broker.name = getattr(row, self.get_column_name("name"))
                broker.group_id = getattr(row, self.get_column_name("group_id"))
                broker.lei = getattr(row, self.get_column_name("lei"))
            return broker

    @timed
    def create(self, brokers: list[Broker]) -> None:
        if len(brokers) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): broker.id,
                                                self.get_column_name("code"): broker.code,
                                                self.get_column_name("name"): broker.name,
                                                self.get_column_name("group_id"): broker.group_id,
                                                self.get_column_name("lei"): broker.lei
                                               } for broker in brokers])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, brokers: list[Broker]) -> None:
        if len(brokers) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("group_id"): bindparam("group_id"),
                                                                                                                             self.get_column_name("lei"): bindparam("lei")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": broker.id,
                                     "code": broker.code,
                                     "name": broker.name,
                                     "group_id": broker.group_id,
                                     "lei": broker.lei
                                    } for broker in brokers])

    @timed
    def delete(self, brokers: list[Broker]) -> None:
        if len(brokers) > 0:
            ids = [broker.id for broker in brokers]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class BrokerAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BrokerAsyncDAO, self).__init__()


class SQlAlchemyBrokerAsyncDAO(BrokerAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        BrokerAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("broker"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("group_id"), Integer, nullable=True),
                                   Column(self.get_column_name("lei"), String(20), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("broker_pk")),
                                   ForeignKeyConstraint([self.get_column_name("group_id")],
                                                        ["{}.{}".format(self.get_table_name("broker_group", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("broker_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> Broker | dict[int, Broker] | None:
        if id_ is None:
            brokers = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                broker = Broker(getattr(row, self.get_column_name("id")))
                broker.code = getattr(row, self.get_column_name("code"))
                broker.name = getattr(row, self.get_column_name("name"))
                broker.group_id = getattr(row, self.get_column_name("group_id"))
                broker.lei = getattr(row, self.get_column_name("lei"))
                brokers[broker.id] = broker
            return brokers
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            broker = None
            if row is not None:
                broker = Broker(getattr(row, self.get_column_name("id")))
                broker.code = getattr(row, self.get_column_name("code"))
                broker.name = getattr(row, self.get_column_name("name"))
                broker.group_id = getattr(row, self.get_column_name("group_id"))
                broker.lei = getattr(row, self.get_column_name("lei"))
            return broker

    @async_timed
    async def create(self, brokers: list[Broker]) -> None:
        if len(brokers) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): broker.id,
                                                self.get_column_name("code"): broker.code,
                                                self.get_column_name("name"): broker.name,
                                                self.get_column_name("group_id"): broker.group_id,
                                                self.get_column_name("lei"): broker.lei
                                               } for broker in brokers])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, brokers: list[Broker]) -> None:
        if len(brokers) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("group_id"): bindparam("group_id"),
                                                                                                                             self.get_column_name("lei"): bindparam("lei")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": broker.id,
                                           "code": broker.code,
                                           "name": broker.name,
                                           "group_id": broker.group_id,
                                           "lei": broker.lei
                                          } for broker in brokers])

    @async_timed
    async def delete(self, brokers: list[Broker]) -> None:
        if len(brokers) > 0:
            ids = [broker.id for broker in brokers]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class RegulatoryAuthorityDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RegulatoryAuthorityDAO, self).__init__()


class SQlAlchemyRegulatoryAuthorityDAO(RegulatoryAuthorityDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        RegulatoryAuthorityDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("regulatory_authority"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("regulatory_authority_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("regulatory_authority_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> RegulatoryAuthority | dict[int, RegulatoryAuthority] | None:
        if id_ is None:
            authorities = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                auth = RegulatoryAuthority(getattr(row, self.get_column_name("id")))
                auth.code = getattr(row, self.get_column_name("code"))
                auth.name = getattr(row, self.get_column_name("name"))
                auth.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                auth.website = getattr(row, self.get_column_name("website"))
                authorities[auth.id] = auth
            return authorities
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            auth = None
            if row is not None:
                auth = RegulatoryAuthority(getattr(row, self.get_column_name("id")))
                auth.code = getattr(row, self.get_column_name("code"))
                auth.name = getattr(row, self.get_column_name("name"))
                auth.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                auth.website = getattr(row, self.get_column_name("website"))
            return auth

    @timed
    def create(self, authorities: list[RegulatoryAuthority]) -> None:
        if len(authorities) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): auth.id,
                                                self.get_column_name("code"): auth.code,
                                                self.get_column_name("name"): auth.name,
                                                self.get_column_name("country_iso2"): auth.country_iso2,
                                                self.get_column_name("website"): auth.website
                                               } for auth in authorities])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, authorities: list[RegulatoryAuthority]) -> None:
        if len(authorities) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": auth.id,
                                     "code": auth.code,
                                     "name": auth.name,
                                     "country_iso2": auth.country_iso2,
                                     "website": auth.website
                                    } for auth in authorities])

    @timed
    def delete(self, authorities: list[RegulatoryAuthority]) -> None:
        if len(authorities) > 0:
            ids = [auth.id for auth in authorities]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class RegulatoryAuthorityAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RegulatoryAuthorityAsyncDAO, self).__init__()


class SQlAlchemyRegulatoryAuthorityAsyncDAO(RegulatoryAuthorityAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        RegulatoryAuthorityAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("regulatory_authority"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=True),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("regulatory_authority_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("regulatory_authority_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> RegulatoryAuthority | dict[int, RegulatoryAuthority] | None:
        if id_ is None:
            authorities = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                auth = RegulatoryAuthority(getattr(row, self.get_column_name("id")))
                auth.code = getattr(row, self.get_column_name("code"))
                auth.name = getattr(row, self.get_column_name("name"))
                auth.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                auth.website = getattr(row, self.get_column_name("website"))
                authorities[auth.id] = auth
            return authorities
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            auth = None
            if row is not None:
                auth = RegulatoryAuthority(getattr(row, self.get_column_name("id")))
                auth.code = getattr(row, self.get_column_name("code"))
                auth.name = getattr(row, self.get_column_name("name"))
                auth.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                auth.website = getattr(row, self.get_column_name("website"))
            return auth

    @async_timed
    async def create(self, authorities: list[RegulatoryAuthority]) -> None:
        if len(authorities) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): auth.id,
                                                self.get_column_name("code"): auth.code,
                                                self.get_column_name("name"): auth.name,
                                                self.get_column_name("country_iso2"): auth.country_iso2,
                                                self.get_column_name("website"): auth.website
                                               } for auth in authorities])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, authorities: list[RegulatoryAuthority]) -> None:
        if len(authorities) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": auth.id,
                                           "code": auth.code,
                                           "name": auth.name,
                                           "country_iso2": auth.country_iso2,
                                           "website": auth.website
                                          } for auth in authorities])

    @async_timed
    async def delete(self, authorities: list[RegulatoryAuthority]) -> None:
        if len(authorities) > 0:
            ids = [auth.id for auth in authorities]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class CentralBankDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CentralBankDAO, self).__init__()


class SQlAlchemyCentralBankDAO(CentralBankDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CentralBankDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("central_bank"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("currency_iso3"), String(3), nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("central_bank_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("central_bank_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("central_bank_fk2")),
                                   ForeignKeyConstraint([self.get_column_name("currency_iso3")],
                                                        ["{}.{}".format(self.get_table_name("currency", "iso"), self.get_column_name("iso3"))],
                                                        name=self.get_key_name("central_bank_fk3")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> CentralBank | dict[int, CentralBank] | None:
        if id_ is None:
            banks = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                bank = CentralBank(getattr(row, self.get_column_name("id")))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.bank_id = getattr(row, self.get_column_name("bank_id"))
                bank.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
                bank.website = getattr(row, self.get_column_name("website"))
                banks[bank.id] = bank
            return banks
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            bank = None
            if row is not None:
                bank = CentralBank(getattr(row, self.get_column_name("id")))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.bank_id = getattr(row, self.get_column_name("bank_id"))
                bank.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
                bank.website = getattr(row, self.get_column_name("website"))
            return bank

    @timed
    def create(self, banks: list[CentralBank]) -> None:
        if len(banks) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): bank.id,
                                                self.get_column_name("code"): bank.code,
                                                self.get_column_name("name"): bank.name,
                                                self.get_column_name("country_iso2"): bank.country_iso2,
                                                self.get_column_name("bank_id"): bank.bank_id,
                                                self.get_column_name("currency_iso3"): bank.currency_iso3,
                                                self.get_column_name("website"): bank.website
                                               } for bank in banks])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, banks: list[CentralBank]) -> None:
        if len(banks) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("currency_iso3"): bindparam("currency_iso3"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": bank.id,
                                     "code": bank.code,
                                     "name": bank.name,
                                     "country_iso2": bank.country_iso2,
                                     "bank_id": bank.bank_id,
                                     "currency_iso3": bank.currency_iso3,
                                     "website": bank.website
                                    } for bank in banks])

    @timed
    def delete(self, banks: list[CentralBank]) -> None:
        if len(banks) > 0:
            ids = [bank.id for bank in banks]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CentralBankAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CentralBankAsyncDAO, self).__init__()


class SQlAlchemyCentralBankAsyncDAO(CentralBankAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CentralBankAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("central_bank"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("currency_iso3"), String(3), nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("central_bank_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("central_bank_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("central_bank_fk2")),
                                   ForeignKeyConstraint([self.get_column_name("currency_iso3")],
                                                        ["{}.{}".format(self.get_table_name("currency", "iso"), self.get_column_name("iso3"))],
                                                        name=self.get_key_name("central_bank_fk3")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> CentralBank | dict[int, CentralBank] | None:
        if id_ is None:
            banks = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                bank = CentralBank(getattr(row, self.get_column_name("id")))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.bank_id = getattr(row, self.get_column_name("bank_id"))
                bank.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
                bank.website = getattr(row, self.get_column_name("website"))
                banks[bank.id] = bank
            return banks
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            bank = None
            if row is not None:
                bank = CentralBank(getattr(row, self.get_column_name("id")))
                bank.code = getattr(row, self.get_column_name("code"))
                bank.name = getattr(row, self.get_column_name("name"))
                bank.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                bank.bank_id = getattr(row, self.get_column_name("bank_id"))
                bank.currency_iso3 = getattr(row, self.get_column_name("currency_iso3"))
                bank.website = getattr(row, self.get_column_name("website"))
            return bank

    @async_timed
    async def create(self, banks: list[CentralBank]) -> None:
        if len(banks) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): bank.id,
                                                self.get_column_name("code"): bank.code,
                                                self.get_column_name("name"): bank.name,
                                                self.get_column_name("country_iso2"): bank.country_iso2,
                                                self.get_column_name("bank_id"): bank.bank_id,
                                                self.get_column_name("currency_iso3"): bank.currency_iso3,
                                                self.get_column_name("website"): bank.website
                                               } for bank in banks])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, banks: list[CentralBank]) -> None:
        if len(banks) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("currency_iso3"): bindparam("currency_iso3"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": bank.id,
                                           "code": bank.code,
                                           "name": bank.name,
                                           "country_iso2": bank.country_iso2,
                                           "bank_id": bank.bank_id,
                                           "currency_iso3": bank.currency_iso3,
                                           "website": bank.website
                                          } for bank in banks])

    @async_timed
    async def delete(self, banks: list[CentralBank]) -> None:
        if len(banks) > 0:
            ids = [bank.id for bank in banks]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class CentralSecuritiesDepositoryDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CentralSecuritiesDepositoryDAO, self).__init__()


class SQlAlchemyCentralSecuritiesDepositoryDAO(CentralSecuritiesDepositoryDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CentralSecuritiesDepositoryDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("central_securities_depository"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("central_securities_depository_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("central_securities_depository_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("central_securities_depository_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> CentralSecuritiesDepository | dict[int, CentralSecuritiesDepository] | None:
        if id_ is None:
            csds = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                csd = CentralSecuritiesDepository(getattr(row, self.get_column_name("id")))
                csd.code = getattr(row, self.get_column_name("code"))
                csd.name = getattr(row, self.get_column_name("name"))
                csd.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                csd.bank_id = getattr(row, self.get_column_name("bank_id"))
                csd.website = getattr(row, self.get_column_name("website"))
                csds[csd.id] = csd
            return csds
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            csd = None
            if row is not None:
                csd = CentralSecuritiesDepository(getattr(row, self.get_column_name("id")))
                csd.code = getattr(row, self.get_column_name("code"))
                csd.name = getattr(row, self.get_column_name("name"))
                csd.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                csd.bank_id = getattr(row, self.get_column_name("bank_id"))
                csd.website = getattr(row, self.get_column_name("website"))
            return csd

    @timed
    def create(self, csds: list[CentralSecuritiesDepository]) -> None:
        if len(csds) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): csd.id,
                                                self.get_column_name("code"): csd.code,
                                                self.get_column_name("name"): csd.name,
                                                self.get_column_name("country_iso2"): csd.country_iso2,
                                                self.get_column_name("bank_id"): csd.bank_id,
                                                self.get_column_name("website"): csd.website
                                               } for csd in csds])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, csds: list[CentralSecuritiesDepository]) -> None:
        if len(csds) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": csd.id,
                                     "code": csd.code,
                                     "name": csd.name,
                                     "country_iso2": csd.country_iso2,
                                     "bank_id": csd.bank_id,
                                     "website": csd.website
                                    } for csd in csds])

    @timed
    def delete(self, csds: list[CentralSecuritiesDepository]) -> None:
        if len(csds) > 0:
            ids = [csd.id for csd in csds]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CentralSecuritiesDepositoryAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CentralSecuritiesDepositoryAsyncDAO, self).__init__()


class SQlAlchemyCentralSecuritiesDepositoryAsyncDAO(CentralSecuritiesDepositoryAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CentralSecuritiesDepositoryAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("central_securities_depository"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("central_securities_depository_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("central_securities_depository_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("central_securities_depository_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> CentralSecuritiesDepository | dict[int, CentralSecuritiesDepository] | None:
        if id_ is None:
            csds = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                csd = CentralSecuritiesDepository(getattr(row, self.get_column_name("id")))
                csd.code = getattr(row, self.get_column_name("code"))
                csd.name = getattr(row, self.get_column_name("name"))
                csd.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                csd.bank_id = getattr(row, self.get_column_name("bank_id"))
                csd.website = getattr(row, self.get_column_name("website"))
                csds[csd.id] = csd
            return csds
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            csd = None
            if row is not None:
                csd = CentralSecuritiesDepository(getattr(row, self.get_column_name("id")))
                csd.code = getattr(row, self.get_column_name("code"))
                csd.name = getattr(row, self.get_column_name("name"))
                csd.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                csd.bank_id = getattr(row, self.get_column_name("bank_id"))
                csd.website = getattr(row, self.get_column_name("website"))
            return csd

    @async_timed
    async def create(self, csds: list[CentralSecuritiesDepository]) -> None:
        if len(csds) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): csd.id,
                                                self.get_column_name("code"): csd.code,
                                                self.get_column_name("name"): csd.name,
                                                self.get_column_name("country_iso2"): csd.country_iso2,
                                                self.get_column_name("bank_id"): csd.bank_id,
                                                self.get_column_name("website"): csd.website
                                               } for csd in csds])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, csds: list[CentralSecuritiesDepository]) -> None:
        if len(csds) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": csd.id,
                                           "code": csd.code,
                                           "name": csd.name,
                                           "country_iso2": csd.country_iso2,
                                           "bank_id": csd.bank_id,
                                           "website": csd.website
                                          } for csd in csds])

    @async_timed
    async def delete(self, csds: list[CentralSecuritiesDepository]) -> None:
        if len(csds) > 0:
            ids = [csd.id for csd in csds]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class SubcustodianDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SubcustodianDAO, self).__init__()


class SQlAlchemySubcustodianDAO(SubcustodianDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        SubcustodianDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("subcustodian"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("subcustodian_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iro"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("subcustodian_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("subcustodian_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> Subcustodian | dict[int, Subcustodian] | None:
        if id_ is None:
            custos = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                custo = Subcustodian(getattr(row, self.get_column_name("id")))
                custo.code = getattr(row, self.get_column_name("code"))
                custo.name = getattr(row, self.get_column_name("name"))
                custo.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                custo.bank_id = getattr(row, self.get_column_name("bank_id"))
                custo.website = getattr(row, self.get_column_name("website"))
                custos[custo.id] = custo
            return custos
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            custo = None
            if row is not None:
                custo = Subcustodian(getattr(row, self.get_column_name("id")))
                custo.code = getattr(row, self.get_column_name("code"))
                custo.name = getattr(row, self.get_column_name("name"))
                custo.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                custo.bank_id = getattr(row, self.get_column_name("bank_id"))
                custo.website = getattr(row, self.get_column_name("website"))
            return custo

    @timed
    def create(self, custos: list[Subcustodian]) -> None:
        if len(custos) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): custo.id,
                                                self.get_column_name("code"): custo.code,
                                                self.get_column_name("name"): custo.name,
                                                self.get_column_name("country_iso2"): custo.country_iso2,
                                                self.get_column_name("bank_id"): custo.bank_id,
                                                self.get_column_name("website"): custo.website
                                               } for custo in custos])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, custos: list[Subcustodian]) -> None:
        if len(custos) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": custo.id,
                                     "code": custo.code,
                                     "name": custo.name,
                                     "country_iso2": custo.country_iso2,
                                     "bank_id": custo.bank_id,
                                     "website": custo.website
                                    } for custo in custos])

    @timed
    def delete(self, custos: list[Subcustodian]) -> None:
        if len(custos) > 0:
            ids = [custo.id for custo in custos]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class SubcustodianAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SubcustodianAsyncDAO, self).__init__()


class SQlAlchemySubcustodianAsyncDAO(SubcustodianAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        SubcustodianAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("subcustodian"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("code"), String(10), nullable=False),
                                   Column(self.get_column_name("name"), String(80), nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=False),
                                   Column(self.get_column_name("bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("website"), String(250), nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("subcustodian_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("subcustodian_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("bank_id")],
                                                        ["{}.{}".format(self.get_table_name("bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("subcustodian_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> Subcustodian | dict[int, Subcustodian] | None:
        if id_ is None:
            custos = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                custo = Subcustodian(getattr(row, self.get_column_name("id")))
                custo.code = getattr(row, self.get_column_name("code"))
                custo.name = getattr(row, self.get_column_name("name"))
                custo.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                custo.bank_id = getattr(row, self.get_column_name("bank_id"))
                custo.website = getattr(row, self.get_column_name("website"))
                custos[custo.id] = custo
            return custos
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            custo = None
            if row is not None:
                custo = Subcustodian(getattr(row, self.get_column_name("id")))
                custo.code = getattr(row, self.get_column_name("code"))
                custo.name = getattr(row, self.get_column_name("name"))
                custo.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                custo.bank_id = getattr(row, self.get_column_name("bank_id"))
                custo.website = getattr(row, self.get_column_name("website"))
            return custo

    @async_timed
    async def create(self, custos: list[Subcustodian]) -> None:
        if len(custos) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): custo.id,
                                                self.get_column_name("code"): custo.code,
                                                self.get_column_name("name"): custo.name,
                                                self.get_column_name("country_iso2"): custo.country_iso2,
                                                self.get_column_name("bank_id"): custo.bank_id,
                                                self.get_column_name("website"): custo.website
                                               } for custo in custos])
            with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, custos: list[Subcustodian]) -> None:
        if len(custos) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("code"): bindparam("code"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("bank_id"): bindparam("bank_id"),
                                                                                                                             self.get_column_name("website"): bindparam("website")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": custo.id,
                                           "code": custo.code,
                                           "name": custo.name,
                                           "country_iso2": custo.country_iso2,
                                           "bank_id": custo.bank_id,
                                           "website": custo.website
                                          } for custo in custos])

    @async_timed
    async def delete(self, custos: list[Subcustodian]) -> None:
        if len(custos) > 0:
            ids = [custo.id for custo in custos]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)
