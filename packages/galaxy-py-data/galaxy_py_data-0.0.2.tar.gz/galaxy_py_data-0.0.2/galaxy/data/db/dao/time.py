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

from abc import ABC,                                            \
                abstractmethod
from datetime import datetime
from sqlalchemy.schema import Table,                            \
                              Column,                           \
                              PrimaryKeyConstraint,             \
                              ForeignKeyConstraint
from sqlalchemy.sql.expression import select,                   \
                                      delete,                   \
                                      insert,                   \
                                      update
from sqlalchemy.sql.sqltypes import String,                     \
                                    Integer,                    \
                                    Date,                       \
                                    Boolean,                    \
                                    Time
from sqlalchemy.sql import bindparam

from galaxy.data.db.db import DAO,                              \
                              SQLAlchemyDAO,                    \
                              AsyncDAO,                         \
                              SQLAlchemyAsyncDAO
from galaxy.data.model.time import Period,                      \
                                   Interval,                    \
                                   DayTime,                     \
                                   CountryHoliday,              \
                                   FinancialCountryHoliday,     \
                                   FinancialHoliday
from galaxy.perfo.decorator import timed,                       \
                                   async_timed


class PeriodDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PeriodDAO, self).__init__()


class SQlAlchemyPeriodDAO(PeriodDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        PeriodDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("period"),
                                   self._metadata,
                                   Column(self.get_column_name("code"), String(3), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("code"), name=self.get_key_name("period_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, code: str | None = None) -> Period | dict[str, Period] | None:
        if code is None:
            periods = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                period = Period(getattr(row, self.get_column_name("code")))
                period.name = getattr(row, self.get_column_name("name"))
                periods[period.code] = period
            return periods
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("code")) == code)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            period = None
            if row is not None:
                period = Period(getattr(row, self.get_column_name("code")))
                period.name = getattr(row, self.get_column_name("name"))
            return period

    @timed
    def create(self, periods: list[Period]) -> None:
        if len(periods) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("code"): period.code,
                                                self.get_column_name("name"): period.name
                                               } for period in periods])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, periods: list[Period]) -> None:
        if len(periods) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("code")) == bindparam("code")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "code": period.code,
                                     "name": period.name
                                    } for period in periods])

    @timed
    def delete(self, periods: list[Period]) -> None:
        if len(periods) > 0:
            codes = [period.code for period in periods]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("code")).in_(codes))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class PeriodAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PeriodAsyncDAO, self).__init__()


class SQlAlchemyPeriodAsyncDAO(PeriodAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        PeriodAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("period"),
                                   self._metadata,
                                   Column(self.get_column_name("code"), String(3), nullable=False),
                                   Column(self.get_column_name("name"), String(20), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("code"), name=self.get_key_name("period_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, code: str | None = None) -> Period | dict[str, Period] | None:
        if code is None:
            periods = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                period = Period(getattr(row, self.get_column_name("code")))
                period.name = getattr(row, self.get_column_name("name"))
                periods[period.code] = period
            return periods
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("code")) == code)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            period = None
            if row is not None:
                period = Period(getattr(row, self.get_column_name("code")))
                period.name = getattr(row, self.get_column_name("name"))
            return period

    @async_timed
    async def create(self, periods: list[Period]) -> None:
        if len(periods) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("code"): period.code,
                                                self.get_column_name("name"): period.name
                                               } for period in periods])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, periods: list[Period]) -> None:
        if len(periods) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("code")) == bindparam("code")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "code": period.code,
                                           "name": period.name
                                          } for period in periods])

    @async_timed
    async def delete(self, periods: list[Period]) -> None:
        if len(periods) > 0:
            codes = [period.code for period in periods]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("code")).in_(codes))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class IntervalDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(IntervalDAO, self).__init__()


class SQlAlchemyIntervalDAO(IntervalDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        IntervalDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("interval"),
                                   self._metadata,
                                   Column(self.get_column_name("code"), String(3), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("code"), name=self.get_key_name("interval_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, code: str | None = None) -> Interval | dict[str, Interval] | None:
        if code is None:
            intervals = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                interval = Interval(getattr(row, self.get_column_name("code")))
                interval.name = getattr(row, self.get_column_name("name"))
                intervals[interval.code] = interval
            return intervals
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("code")) == code)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            interval = None
            if row is not None:
                interval = Interval(getattr(row, self.get_column_name("code")))
                interval.name = getattr(row, self.get_column_name("name"))
            return interval

    @timed
    def create(self, intervals: list[Interval]) -> None:
        if len(intervals) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("code"): interval.code,
                                                self.get_column_name("name"): interval.name
                                               } for interval in intervals])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, intervals: list[Interval]) -> None:
        if len(intervals) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("code")) == bindparam("code")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "code": interval.code,
                                     "name": interval.name,
                                    } for interval in intervals])

    @timed
    def delete(self, intervals: list[Interval]) -> None:
        if len(intervals) > 0:
            codes = [interval.code for interval in intervals]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("code")).in_(codes))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class IntervalAsyncDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(IntervalAsyncDAO, self).__init__()


class SQlAlchemyIntervalAsyncDAO(IntervalAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        IntervalAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("interval"),
                                   self._metadata,
                                   Column(self.get_column_name("code"), String(3), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("code"), name=self.get_key_name("interval_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, code: str | None = None) -> Interval | dict[str, Interval] | None:
        if code is None:
            intervals = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                interval = Interval(getattr(row, self.get_column_name("code")))
                interval.name = getattr(row, self.get_column_name("name"))
                intervals[interval.code] = interval
            return intervals
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("code")) == code)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            interval = None
            if row is not None:
                interval = Interval(getattr(row, self.get_column_name("code")))
                interval.name = getattr(row, self.get_column_name("name"))
            return interval

    @async_timed
    async def create(self, intervals: list[Interval]) -> None:
        if len(intervals) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("code"): interval.code,
                                                self.get_column_name("name"): interval.name
                                               } for interval in intervals])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, intervals: list[Interval]) -> None:
        if len(intervals) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("code")) == bindparam("code")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "code": interval.code,
                                           "name": interval.name,
                                          } for interval in intervals])

    @async_timed
    async def delete(self, intervals: list[Interval]) -> None:
        if len(intervals) > 0:
            codes = [interval.code for interval in intervals]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("code")).in_(codes))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class DayTimeDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DayTimeDAO, self).__init__()


class SQlAlchemyDayTimeDAO(DayTimeDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DayTimeDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("day_time"),
                                   self._metadata,
                                   Column(self.get_column_name("code"), String(3), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("code"), name=self.get_key_name("day_time_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, code: str | None = None) -> DayTime | dict[str, DayTime] | None:
        if code is None:
            daytimes = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                daytime = DayTime(getattr(row, self.get_column_name("code")))
                daytime.name = getattr(row, self.get_column_name("name"))
                daytimes[daytime.code] = daytime
            return daytimes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("code")) == code)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            daytime = None
            if row is not None:
                daytime = DayTime(getattr(row, self.get_column_name("code")))
                daytime.name = getattr(row, self.get_column_name("name"))
            return daytime

    @timed
    def create(self, daytimes: list[DayTime]) -> None:
        if len(daytimes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("code"): daytime.code,
                                                self.get_column_name("name"): daytime.name
                                               } for daytime in daytimes])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, daytimes: list[DayTime]) -> None:
        if len(daytimes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("code")) == bindparam("code")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "code": daytime.code,
                                     "name": daytime.name
                                    } for daytime in daytimes])

    @timed
    def delete(self, daytimes: list[DayTime]) -> None:
        if len(daytimes) > 0:
            codes = [daytime.code for daytime in daytimes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("code")).in_(codes))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class DayTimeAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DayTimeAsyncDAO, self).__init__()


class SQlAlchemyDayTimeAsyncDAO(DayTimeAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        DayTimeAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("day_time"),
                                   self._metadata,
                                   Column(self.get_column_name("code"), String(3), nullable=False),
                                   Column(self.get_column_name("name"), String(50), nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("code"), name=self.get_key_name("day_time_pk")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, code: str | None = None) -> DayTime | dict[str, DayTime] | None:
        if code is None:
            daytimes = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                daytime = DayTime(getattr(row, self.get_column_name("code")))
                daytime.name = getattr(row, self.get_column_name("name"))
                daytimes[daytime.code] = daytime
            return daytimes
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("code")) == code)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            daytime = None
            if row is not None:
                daytime = DayTime(getattr(row, self.get_column_name("code")))
                daytime.name = getattr(row, self.get_column_name("name"))
            return daytime

    @async_timed
    async def create(self, daytimes: list[DayTime]) -> None:
        if len(daytimes) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("code"): daytime.code,
                                                self.get_column_name("name"): daytime.name
                                               } for daytime in daytimes])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, daytimes: list[DayTime]) -> None:
        if len(daytimes) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("code")) == bindparam("code")).values({
                                                                                                                                self.get_column_name("name"): bindparam("name")
                                                                                                                               })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "code": daytime.code,
                                           "name": daytime.name
                                          } for daytime in daytimes])

    @async_timed
    async def delete(self, daytimes: list[DayTime]) -> None:
        if len(daytimes) > 0:
            codes = [daytime.code for daytime in daytimes]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("code")).in_(codes))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class CountryHolidayDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryHolidayDAO, self).__init__()

    @abstractmethod
    def get_nexts(self) -> dict[int, CountryHoliday]:
        raise NotImplementedError("Should implement get_nexts()")


class SQlAlchemyCountryHolidayDAO(CountryHolidayDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CountryHolidayDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country_holiday"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("holiday_date"), Date, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("subdivision"), String(20), nullable=True),
                                   Column(self.get_column_name("name"), String(50), nullable=True),
                                   Column(self.get_column_name("is_public"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_bank"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_armed_forces"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_gov"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_opt"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_school"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_workday"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_half"), Boolean, nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("country_holiday_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_holiday_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> CountryHoliday | dict[int, CountryHoliday] | None:
        if id_ is None:
            holidays = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                holiday = CountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                holiday.subdivision = getattr(row, self.get_column_name("subdivision"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.is_public = getattr(row, self.get_column_name("is_public"))
                holiday.is_bank = getattr(row, self.get_column_name("is_bank"))
                holiday.is_armed_forces = getattr(row, self.get_column_name("is_armed_forces"))
                holiday.is_gov = getattr(row, self.get_column_name("is_gov"))
                holiday.is_opt = getattr(row, self.get_column_name("is_opt"))
                holiday.is_school = getattr(row, self.get_column_name("is_school"))
                holiday.is_workday = getattr(row, self.get_column_name("is_workday"))
                holiday.is_half = getattr(row, self.get_column_name("is_half"))
                holidays[holiday.id] = holiday
            return holidays
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            holiday = None
            if row is not None:
                holiday = CountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                holiday.subdivision = getattr(row, self.get_column_name("subdivision"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.is_public = getattr(row, self.get_column_name("is_public"))
                holiday.is_bank = getattr(row, self.get_column_name("is_bank"))
                holiday.is_armed_forces = getattr(row, self.get_column_name("is_armed_forces"))
                holiday.is_gov = getattr(row, self.get_column_name("is_gov"))
                holiday.is_opt = getattr(row, self.get_column_name("is_opt"))
                holiday.is_school = getattr(row, self.get_column_name("is_school"))
                holiday.is_workday = getattr(row, self.get_column_name("is_workday"))
                holiday.is_half = getattr(row, self.get_column_name("is_half"))
            return holiday

    @timed
    def get_nexts(self) -> dict[int, CountryHoliday]:
        holidays = {}
        stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("holiday_date")) >= datetime.now())
        with self._engine.begin() as conn:
            res = conn.execute(stmt)
        for row in res:
            holiday = CountryHoliday(getattr(row, self.get_column_name("id")))
            holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
            holiday.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
            holiday.subdivision = getattr(row, self.get_column_name("subdivision"))
            holiday.name = getattr(row, self.get_column_name("name"))
            holiday.is_public = getattr(row, self.get_column_name("is_public"))
            holiday.is_bank = getattr(row, self.get_column_name("is_bank"))
            holiday.is_armed_forces = getattr(row, self.get_column_name("is_armed_forces"))
            holiday.is_gov = getattr(row, self.get_column_name("is_gov"))
            holiday.is_opt = getattr(row, self.get_column_name("is_opt"))
            holiday.is_school = getattr(row, self.get_column_name("is_school"))
            holiday.is_workday = getattr(row, self.get_column_name("is_workday"))
            holiday.is_half = getattr(row, self.get_column_name("is_half"))
            holidays[holiday.id] = holiday
        return holidays

    @timed
    def create(self, holidays: list[CountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): holiday.id,
                                                self.get_column_name("holiday_date"): holiday.holiday_date,
                                                self.get_column_name("country_iso2"): holiday.country_iso2,
                                                self.get_column_name("subdivision"): holiday.subdivision,
                                                self.get_column_name("name"): holiday.name,
                                                self.get_column_name("is_public"): holiday.is_public,
                                                self.get_column_name("is_bank"): holiday.is_bank,
                                                self.get_column_name("is_armed_forces"): holiday.is_armed_forces,
                                                self.get_column_name("is_gov"): holiday.is_gov,
                                                self.get_column_name("is_opt"): holiday.is_opt,
                                                self.get_column_name("is_school"): holiday.is_school,
                                                self.get_column_name("is_workday"): holiday.is_workday,
                                                self.get_column_name("is_half"): holiday.is_half
                                               } for holiday in holidays])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, holidays: list[CountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("holiday_date"): bindparam("holiday_date"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("subdivision"): bindparam("subdivision"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("is_public"): bindparam("is_public"),
                                                                                                                             self.get_column_name("is_bank"): bindparam("is_bank"),
                                                                                                                             self.get_column_name("is_armed_forces"): bindparam("is_armed_forces"),
                                                                                                                             self.get_column_name("is_gov"): bindparam("is_gov"),
                                                                                                                             self.get_column_name("is_opt"): bindparam("is_opt"),
                                                                                                                             self.get_column_name("is_school"): bindparam("is_school"),
                                                                                                                             self.get_column_name("is_workday"): bindparam("is_workday"),
                                                                                                                             self.get_column_name("is_half"): bindparam("is_half")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": holiday.id,
                                     "holiday_date": holiday.holiday_date,
                                     "country_iso2": holiday.country_iso2,
                                     "subdivision": holiday.subdivision,
                                     "name": holiday.name,
                                     "is_public": holiday.is_public,
                                     "is_bank": holiday.is_bank,
                                     "is_armed_forces": holiday.is_armed_forces,
                                     "is_gov": holiday.is_gov,
                                     "is_opt": holiday.is_opt,
                                     "is_school": holiday.is_school,
                                     "is_workday": holiday.is_workday,
                                     "is_half": holiday.is_half
                                    } for holiday in holidays])

    @timed
    def delete(self, holidays: list[CountryHoliday]) -> None:
        if len(holidays) > 0:
            ids = [holiday.id for holiday in holidays]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class CountryHolidayAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CountryHolidayAsyncDAO, self).__init__()

    @abstractmethod
    async def get_nexts(self) -> dict[int, CountryHoliday]:
        raise NotImplementedError("Should implement get_nexts()")


class SQlAlchemyCountryHolidayAsyncDAO(CountryHolidayAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        CountryHolidayAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("country_holiday"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("holiday_date"), Date, nullable=False),
                                   Column(self.get_column_name("country_iso2"), String(2), nullable=True),
                                   Column(self.get_column_name("subdivision"), String(20), nullable=True),
                                   Column(self.get_column_name("name"), String(50), nullable=True),
                                   Column(self.get_column_name("is_public"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_bank"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_armed_forces"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_gov"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_opt"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_school"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_workday"), Boolean, nullable=True),
                                   Column(self.get_column_name("is_half"), Boolean, nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("country_holiday_pk")),
                                   ForeignKeyConstraint([self.get_column_name("country_iso2")],
                                                        ["{}.{}".format(self.get_table_name("country", "iso"), self.get_column_name("iso2"))],
                                                        name=self.get_key_name("country_holiday_fk1")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> CountryHoliday | dict[int, CountryHoliday] | None:
        if id_ is None:
            holidays = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                holiday = CountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                holiday.subdivision = getattr(row, self.get_column_name("subdivision"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.is_public = getattr(row, self.get_column_name("is_public"))
                holiday.is_bank = getattr(row, self.get_column_name("is_bank"))
                holiday.is_armed_forces = getattr(row, self.get_column_name("is_armed_forces"))
                holiday.is_gov = getattr(row, self.get_column_name("is_gov"))
                holiday.is_opt = getattr(row, self.get_column_name("is_opt"))
                holiday.is_school = getattr(row, self.get_column_name("is_school"))
                holiday.is_workday = getattr(row, self.get_column_name("is_workday"))
                holiday.is_half = getattr(row, self.get_column_name("is_half"))
                holidays[holiday.id] = holiday
            return holidays
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            holiday = None
            if row is not None:
                holiday = CountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
                holiday.subdivision = getattr(row, self.get_column_name("subdivision"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.is_public = getattr(row, self.get_column_name("is_public"))
                holiday.is_bank = getattr(row, self.get_column_name("is_bank"))
                holiday.is_armed_forces = getattr(row, self.get_column_name("is_armed_forces"))
                holiday.is_gov = getattr(row, self.get_column_name("is_gov"))
                holiday.is_opt = getattr(row, self.get_column_name("is_opt"))
                holiday.is_school = getattr(row, self.get_column_name("is_school"))
                holiday.is_workday = getattr(row, self.get_column_name("is_workday"))
                holiday.is_half = getattr(row, self.get_column_name("is_half"))
            return holiday

    @async_timed
    async def get_nexts(self) -> dict[int, CountryHoliday]:
        holidays = {}
        stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("holiday_date")) >= datetime.now())
        async with self._engine.begin() as conn:
            res = await conn.execute(stmt)
        for row in res:
            holiday = CountryHoliday(getattr(row, self.get_column_name("id")))
            holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
            holiday.country_iso2 = getattr(row, self.get_column_name("country_iso2"))
            holiday.subdivision = getattr(row, self.get_column_name("subdivision"))
            holiday.name = getattr(row, self.get_column_name("name"))
            holiday.is_public = getattr(row, self.get_column_name("is_public"))
            holiday.is_bank = getattr(row, self.get_column_name("is_bank"))
            holiday.is_armed_forces = getattr(row, self.get_column_name("is_armed_forces"))
            holiday.is_gov = getattr(row, self.get_column_name("is_gov"))
            holiday.is_opt = getattr(row, self.get_column_name("is_opt"))
            holiday.is_school = getattr(row, self.get_column_name("is_school"))
            holiday.is_workday = getattr(row, self.get_column_name("is_workday"))
            holiday.is_half = getattr(row, self.get_column_name("is_half"))
            holidays[holiday.id] = holiday
        return holidays

    @async_timed
    async def create(self, holidays: list[CountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): holiday.id,
                                                self.get_column_name("holiday_date"): holiday.holiday_date,
                                                self.get_column_name("country_iso2"): holiday.country_iso2,
                                                self.get_column_name("subdivision"): holiday.subdivision,
                                                self.get_column_name("name"): holiday.name,
                                                self.get_column_name("is_public"): holiday.is_public,
                                                self.get_column_name("is_bank"): holiday.is_bank,
                                                self.get_column_name("is_armed_forces"): holiday.is_armed_forces,
                                                self.get_column_name("is_gov"): holiday.is_gov,
                                                self.get_column_name("is_opt"): holiday.is_opt,
                                                self.get_column_name("is_school"): holiday.is_school,
                                                self.get_column_name("is_workday"): holiday.is_workday,
                                                self.get_column_name("is_half"): holiday.is_half
                                               } for holiday in holidays])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, holidays: list[CountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("holiday_date"): bindparam("holiday_date"),
                                                                                                                             self.get_column_name("country_iso2"): bindparam("country_iso2"),
                                                                                                                             self.get_column_name("subdivision"): bindparam("subdivision"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("is_public"): bindparam("is_public"),
                                                                                                                             self.get_column_name("is_bank"): bindparam("is_bank"),
                                                                                                                             self.get_column_name("is_armed_forces"): bindparam("is_armed_forces"),
                                                                                                                             self.get_column_name("is_gov"): bindparam("is_gov"),
                                                                                                                             self.get_column_name("is_opt"): bindparam("is_opt"),
                                                                                                                             self.get_column_name("is_school"): bindparam("is_school"),
                                                                                                                             self.get_column_name("is_workday"): bindparam("is_workday"),
                                                                                                                             self.get_column_name("is_half"): bindparam("is_half")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": holiday.id,
                                           "holiday_date": holiday.holiday_date,
                                           "country_iso2": holiday.country_iso2,
                                           "subdivision": holiday.subdivision,
                                           "name": holiday.name,
                                           "is_public": holiday.is_public,
                                           "is_bank": holiday.is_bank,
                                           "is_armed_forces": holiday.is_armed_forces,
                                           "is_gov": holiday.is_gov,
                                           "is_opt": holiday.is_opt,
                                           "is_school": holiday.is_school,
                                           "is_workday": holiday.is_workday,
                                           "is_half": holiday.is_half
                                          } for holiday in holidays])

    @async_timed
    async def delete(self, holidays: list[CountryHoliday]) -> None:
        if len(holidays) > 0:
            ids = [holiday.id for holiday in holidays]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class FinancialCountryHolidayDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FinancialCountryHolidayDAO, self).__init__()


class SQlAlchemyFinancialCountryHolidayDAO(FinancialCountryHolidayDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        FinancialCountryHolidayDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("financial_country_holiday"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("exchange_mic"), String(4), nullable=True),
                                   Column(self.get_column_name("central_bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("holiday_id"), Integer, nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("financial_country_holiday_pk")),
                                   ForeignKeyConstraint([self.get_column_name("exchange_mic")],
                                                        ["{}.{}".format(self.get_table_name("market_exchange", "iso"), self.get_column_name("mic"))],
                                                        name=self.get_key_name("financial_country_holiday_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("central_bank_id")],
                                                        ["{}.{}".format(self.get_table_name("central_bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("financial_country_holiday_fk2")),
                                   ForeignKeyConstraint([self.get_column_name("holiday_id")],
                                                        ["{}.{}".format(self.get_table_name("country_holiday", "time"), self.get_column_name("id"))],
                                                        name=self.get_key_name("financial_country_holiday_fk3")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> FinancialCountryHoliday | dict[int, FinancialCountryHoliday] | None:
        if id_ is None:
            holidays = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                holiday = FinancialCountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.holiday_id = getattr(row, self.get_column_name("holiday_id"))
                holidays[holiday.id] = holiday
            return holidays
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            holiday = None
            if row is not None:
                holiday = FinancialCountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.holiday_id = getattr(row, self.get_column_name("holiday_id"))
            return holiday

    @timed
    def create(self, holidays: list[FinancialCountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): holiday.id,
                                                self.get_column_name("exchange_mic"): holiday.exchange_mic,
                                                self.get_column_name("central_bank_id"): holiday.central_bank_id,
                                                self.get_column_name("holiday_id"): holiday.holiday_id
                                               } for holiday in holidays])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, holidays: list[FinancialCountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("exchange_mic"): bindparam("exchange_mic"),
                                                                                                                             self.get_column_name("central_bank_id"): bindparam("central_bank_id"),
                                                                                                                             self.get_column_name("holiday_id"): bindparam("holiday_id")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": holiday.id,
                                     "exchange_mic": holiday.exchange_mic,
                                     "central_bank_id": holiday.central_bank_id,
                                     "holiday_id": holiday.holiday_id
                                    } for holiday in holidays])

    @timed
    def delete(self, holidays: list[FinancialCountryHoliday]) -> None:
        if len(holidays) > 0:
            ids = [holiday.id for holiday in holidays]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class FinancialCountryHolidayAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FinancialCountryHolidayAsyncDAO, self).__init__()


class SQlAlchemyFinancialCountryHolidayAsyncDAO(FinancialCountryHolidayAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        FinancialCountryHolidayAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("financial_country_holiday"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("exchange_mic"), String(4), nullable=True),
                                   Column(self.get_column_name("central_bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("holiday_id"), Integer, nullable=False),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("financial_country_holiday_pk")),
                                   ForeignKeyConstraint([self.get_column_name("exchange_mic")],
                                                        ["{}.{}".format(self.get_table_name("market_exchange", "iso"), self.get_column_name("mic"))],
                                                        name=self.get_key_name("financial_country_holiday_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("central_bank_id")],
                                                        ["{}.{}".format(self.get_table_name("central_bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("financial_country_holiday_fk2")),
                                   ForeignKeyConstraint([self.get_column_name("holiday_id")],
                                                        ["{}.{}".format(self.get_table_name("country_holiday", "time"), self.get_column_name("id"))],
                                                        name=self.get_key_name("financial_country_holiday_fk3")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> FinancialCountryHoliday | dict[int, FinancialCountryHoliday] | None:
        if id_ is None:
            holidays = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                holiday = FinancialCountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.holiday_id = getattr(row, self.get_column_name("holiday_id"))
                holidays[holiday.id] = holiday
            return holidays
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            holiday = None
            if row is not None:
                holiday = FinancialCountryHoliday(getattr(row, self.get_column_name("id")))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.holiday_id = getattr(row, self.get_column_name("holiday_id"))
            return holiday

    @async_timed
    async def create(self, holidays: list[FinancialCountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): holiday.id,
                                                self.get_column_name("exchange_mic"): holiday.exchange_mic,
                                                self.get_column_name("central_bank_id"): holiday.central_bank_id,
                                                self.get_column_name("holiday_id"): holiday.holiday_id
                                               } for holiday in holidays])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, holidays: list[FinancialCountryHoliday]) -> None:
        if len(holidays) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("exchange_mic"): bindparam("exchange_mic"),
                                                                                                                             self.get_column_name("central_bank_id"): bindparam("central_bank_id"),
                                                                                                                             self.get_column_name("holiday_id"): bindparam("holiday_id")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": holiday.id,
                                           "exchange_mic": holiday.exchange_mic,
                                           "central_bank_id": holiday.central_bank_id,
                                           "holiday_id": holiday.holiday_id
                                          } for holiday in holidays])

    @async_timed
    async def delete(self, holidays: list[FinancialCountryHoliday]) -> None:
        if len(holidays) > 0:
            ids = [holiday.id for holiday in holidays]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)


class FinancialHolidayDAO(DAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FinancialHolidayDAO, self).__init__()

    @abstractmethod
    def get_nexts(self) -> dict[int, FinancialHoliday]:
        raise NotImplementedError("Should implement get_nexts()")


class SQlAlchemyFinancialHolidayDAO(FinancialHolidayDAO, SQLAlchemyDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        FinancialHolidayDAO.__init__(self)
        SQLAlchemyDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("financial_holiday"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("holiday_date"), Date, nullable=False),
                                   Column(self.get_column_name("exchange_mic"), String(4), nullable=True),
                                   Column(self.get_column_name("central_bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("name"), String(50), nullable=True),
                                   Column(self.get_column_name("start_time"), Time, nullable=True),
                                   Column(self.get_column_name("end_time"), Time, nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("financial_holiday_pk")),
                                   ForeignKeyConstraint([self.get_column_name("exchange_mic")],
                                                        ["{}.{}".format(self.get_table_name("market_exchange", "iso"), self.get_column_name("mic"))],
                                                        name=self.get_key_name("financial_holiday_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("central_bank_id")],
                                                        ["{}.{}".format(self.get_table_name("central_bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("financial_holiday_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @timed
    def get(self, id_: int | None = None) -> FinancialHoliday | dict[int, FinancialHoliday] | None:
        if id_ is None:
            holidays = {}
            stmt = select(self._table)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            for row in res:
                holiday = FinancialHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.start_time = getattr(row, self.get_column_name("start_time"))
                holiday.end_time = getattr(row, self.get_column_name("end_time"))
                holidays[holiday.id] = holiday
            return holidays
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            with self._engine.begin() as conn:
                res = conn.execute(stmt)
            row = res.first()
            holiday = None
            if row is not None:
                holiday = FinancialHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.start_time = getattr(row, self.get_column_name("start_time"))
                holiday.end_time = getattr(row, self.get_column_name("end_time"))
            return holiday

    @timed
    def get_nexts(self) -> dict[int, FinancialHoliday]:
        holidays = {}
        stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("holiday_date")) >= datetime.now())
        with self._engine.begin() as conn:
            res = conn.execute(stmt)
        for row in res:
            holiday = FinancialHoliday(getattr(row, self.get_column_name("id")))
            holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
            holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
            holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
            holiday.name = getattr(row, self.get_column_name("name"))
            holiday.start_time = getattr(row, self.get_column_name("start_time"))
            holiday.end_time = getattr(row, self.get_column_name("end_time"))
            holidays[holiday.id] = holiday
        return holidays

    @timed
    def create(self, holidays: list[FinancialHoliday]) -> None:
        if len(holidays) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): holiday.id,
                                                self.get_column_name("holiday_date"): holiday.holiday_date,
                                                self.get_column_name("exchange_mic"): holiday.exchange_mic,
                                                self.get_column_name("central_bank_id"): holiday.central_bank_id,
                                                self.get_column_name("name"): holiday.name,
                                                self.get_column_name("start_time"): holiday.start_time,
                                                self.get_column_name("end_time"): holiday.end_time
                                               } for holiday in holidays])
            with self._engine.begin() as conn:
                conn.execute(stmt)

    @timed
    def update(self, holidays: list[FinancialHoliday]) -> None:
        if len(holidays) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("holiday_date"): bindparam("holiday_date"),
                                                                                                                             self.get_column_name("exchange_mic"): bindparam("exchange_mic"),
                                                                                                                             self.get_column_name("central_bank_id"): bindparam("central_bank_id"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("start_time"): bindparam("start_time"),
                                                                                                                             self.get_column_name("end_time"): bindparam("end_time")
                                                                                                                            })
            with self._engine.begin() as conn:
                conn.execute(stmt, [{
                                     "_id": holiday.id,
                                     "holiday_date": holiday.holiday_date,
                                     "exchange_mic": holiday.exchange_mic,
                                     "central_bank_id": holiday.central_bank_id,
                                     "name": holiday.name,
                                     "start_time": holiday.start_time,
                                     "end_time": holiday.end_time
                                    } for holiday in holidays])

    @timed
    def delete(self, holidays: list[FinancialHoliday]) -> None:
        if len(holidays) > 0:
            ids = [holiday.id for holiday in holidays]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            with self._engine.begin() as conn:
                conn.execute(stmt)


class FinancialHolidayAsyncDAO(AsyncDAO, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FinancialHolidayAsyncDAO, self).__init__()

    @abstractmethod
    async def get_nexts(self) -> dict[int, FinancialHoliday]:
        raise NotImplementedError("Should implement get_nexts()")


class SQlAlchemyFinancialHolidayAsyncDAO(FinancialHolidayAsyncDAO, SQLAlchemyAsyncDAO):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        FinancialHolidayAsyncDAO.__init__(self)
        SQLAlchemyAsyncDAO.__init__(self)

    def _init_table(self) -> None:
        self._table: Table = Table(self.get_table_name("financial_holiday"),
                                   self._metadata,
                                   Column(self.get_column_name("id"), Integer, nullable=False),
                                   Column(self.get_column_name("holiday_date"), Date, nullable=False),
                                   Column(self.get_column_name("exchange_mic"), String(4), nullable=True),
                                   Column(self.get_column_name("central_bank_id"), Integer, nullable=True),
                                   Column(self.get_column_name("name"), String(50), nullable=True),
                                   Column(self.get_column_name("start_time"), Time, nullable=True),
                                   Column(self.get_column_name("end_time"), Time, nullable=True),
                                   PrimaryKeyConstraint(self.get_column_name("id"), name=self.get_key_name("financial_holiday_pk")),
                                   ForeignKeyConstraint([self.get_column_name("exchange_mic")],
                                                        ["{}.{}".format(self.get_table_name("market_exchange", "iso"), self.get_column_name("mic"))],
                                                        name=self.get_key_name("financial_holiday_fk1")),
                                   ForeignKeyConstraint([self.get_column_name("central_bank_id")],
                                                        ["{}.{}".format(self.get_table_name("central_bank", "institution"), self.get_column_name("id"))],
                                                        name=self.get_key_name("financial_holiday_fk2")),
                                   *(self.get_meta_columns()),
                                   schema=self.get_schema_name(),
                                   keep_existing=True)

    @async_timed
    async def get(self, id_: int | None = None) -> FinancialHoliday | dict[int, FinancialHoliday] | None:
        if id_ is None:
            holidays = {}
            stmt = select(self._table)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            for row in res:
                holiday = FinancialHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.start_time = getattr(row, self.get_column_name("start_time"))
                holiday.end_time = getattr(row, self.get_column_name("end_time"))
                holidays[holiday.id] = holiday
            return holidays
        else:
            stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("id")) == id_)
            async with self._engine.begin() as conn:
                res = await conn.execute(stmt)
            row = res.first()
            holiday = None
            if row is not None:
                holiday = FinancialHoliday(getattr(row, self.get_column_name("id")))
                holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
                holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
                holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
                holiday.name = getattr(row, self.get_column_name("name"))
                holiday.start_time = getattr(row, self.get_column_name("start_time"))
                holiday.end_time = getattr(row, self.get_column_name("end_time"))
            return holiday

    @async_timed
    async def get_nexts(self) -> dict[int, FinancialHoliday]:
        holidays = {}
        stmt = select(self._table).where(getattr(self._table.c, self.get_column_name("holiday_date")) >= datetime.now())
        async with self._engine.begin() as conn:
            res = await conn.execute(stmt)
        for row in res:
            holiday = FinancialHoliday(getattr(row, self.get_column_name("id")))
            holiday.holiday_date = getattr(row, self.get_column_name("holiday_date"))
            holiday.exchange_mic = getattr(row, self.get_column_name("exchange_mic"))
            holiday.central_bank_id = getattr(row, self.get_column_name("central_bank_id"))
            holiday.name = getattr(row, self.get_column_name("name"))
            holiday.start_time = getattr(row, self.get_column_name("start_time"))
            holiday.end_time = getattr(row, self.get_column_name("end_time"))
            holidays[holiday.id] = holiday
        return holidays

    @async_timed
    async def create(self, holidays: list[FinancialHoliday]) -> None:
        if len(holidays) > 0:
            stmt = insert(self._table).values([{
                                                self.get_column_name("id"): holiday.id,
                                                self.get_column_name("holiday_date"): holiday.holiday_date,
                                                self.get_column_name("exchange_mic"): holiday.exchange_mic,
                                                self.get_column_name("central_bank_id"): holiday.central_bank_id,
                                                self.get_column_name("name"): holiday.name,
                                                self.get_column_name("start_time"): holiday.start_time,
                                                self.get_column_name("end_time"): holiday.end_time
                                               } for holiday in holidays])
            async with self._engine.begin() as conn:
                await conn.execute(stmt)

    @async_timed
    async def update(self, holidays: list[FinancialHoliday]) -> None:
        if len(holidays) > 0:
            stmt = update(self._table).where(getattr(self._table.c, self.get_column_name("id")) == bindparam("_id")).values({
                                                                                                                             self.get_column_name("holiday_date"): bindparam("holiday_date"),
                                                                                                                             self.get_column_name("exchange_mic"): bindparam("exchange_mic"),
                                                                                                                             self.get_column_name("central_bank_id"): bindparam("central_bank_id"),
                                                                                                                             self.get_column_name("name"): bindparam("name"),
                                                                                                                             self.get_column_name("start_time"): bindparam("start_time"),
                                                                                                                             self.get_column_name("end_time"): bindparam("end_time")
                                                                                                                            })
            async with self._engine.begin() as conn:
                await conn.execute(stmt, [{
                                           "_id": holiday.id,
                                           "holiday_date": holiday.holiday_date,
                                           "exchange_mic": holiday.exchange_mic,
                                           "central_bank_id": holiday.central_bank_id,
                                           "name": holiday.name,
                                           "start_time": holiday.start_time,
                                           "end_time": holiday.end_time
                                          } for holiday in holidays])

    @async_timed
    async def delete(self, holidays: list[FinancialHoliday]) -> None:
        if len(holidays) > 0:
            ids = [holiday.id for holiday in holidays]
            stmt = delete(self._table).where(getattr(self._table.c, self.get_column_name("id")).in_(ids))
            async with self._engine.begin() as conn:
                await conn.execute(stmt)
