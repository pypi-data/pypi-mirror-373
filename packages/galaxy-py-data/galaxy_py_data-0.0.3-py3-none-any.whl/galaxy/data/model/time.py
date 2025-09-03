#  Copyright (c) 2023 Sucden Financial Limited.
#
#  Written by bastien.saltel.
#

from datetime import datetime,                              \
                     date,                                  \
                     timedelta
from dataclasses import dataclass,                          \
                        field

from galaxy.data.model.model import DataModel,              \
                                    AsyncDataModel
from galaxy.data.model.iso import Country,                  \
                                  MarketExchange
from galaxy.data.model.institution import CentralBank
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
class Period(object):
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
class Interval(object):
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
class DayTime(object):
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
class CountryHoliday(object):
    """
    classdocs
    """
    id: int
    holiday_date: date | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    subdivision: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    is_public: bool | None = field(init=False, default=None)
    is_bank: bool | None = field(init=False, default=None)
    is_armed_forces: bool | None = field(init=False, default=None)
    is_gov: bool | None = field(init=False, default=None)
    is_opt: bool | None = field(init=False, default=None)
    is_school: bool | None = field(init=False, default=None)
    is_workday: bool | None = field(init=False, default=None)
    is_half: bool | None = field(init=False, default=None)

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
class FinancialCountryHoliday(object):
    """
    classdocs
    """
    id: int
    exchange_mic: str | None = field(init=False, default=None)
    central_bank_id: int | None = field(init=False, default=None)
    holiday_id: int | None = field(init=False, default=None)

    exchange: MarketExchange | None = field(init=False, default=None)
    central_bank: CentralBank | None = field(init=False, default=None)
    holiday: CountryHoliday | None = field(init=False, default=None)

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
class FinancialHoliday(object):
    """
    classdocs
    """
    id: int
    holiday_date: date | None = field(init=False, default=None)
    exchange_mic: str | None = field(init=False, default=None)
    central_bank_id: int | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    start_time: datetime | None = field(init=False, default=None)
    end_time: datetime | None = field(init=False, default=None)

    exchange: MarketExchange | None = field(init=False, default=None)
    central_bank: CentralBank | None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


class TimeDataModel(DataModel):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(TimeDataModel, self).__init__()
        self.periods: dict[str, Period] | None = None
        self.intervals: dict[str, Interval] | None = None
        self.day_times: dict[str, DayTime] | None = None
        self.country_holidays: dict[int, CountryHoliday] | None = None
        self.financial_country_holidays: dict[int, FinancialCountryHoliday] | None = None
        self.financial_holidays: dict[int, FinancialHoliday] | None = None

    @timed
    def _load(self) -> None:
        super(TimeDataModel, self)._load()
        if self.daos is not None:
            self.periods = self.daos["period"].get()
            self.intervals = self.daos["interval"].get()
            self.day_times = self.daos["day_time"].get()
            self.country_holidays = self.daos["country_holiday"].get_nexts()
            self.financial_country_holidays = self.daos["financial_country_holiday"].get()
            self.financial_holidays = self.daos["financial_holiday"].get_nexts()

    @timed
    def _clear(self) -> None:
        pass

    @staticmethod
    def get_previous_business_date(ref_date: date) -> date:
        # on Saturday, Sunday or Monday, refer to last Friday
        if ref_date.weekday() >= 5 or ref_date.weekday() == 0:
            ref_date = ref_date + timedelta(days=-1)
            while ref_date.weekday() > 4:
                ref_date = ref_date + timedelta(days=-1)
        else:
            ref_date = ref_date + timedelta(days=-1)
        return date(ref_date.year, ref_date.month, ref_date.day)

    @staticmethod
    def get_next_business_date(ref_date: date) -> date:
        # on Saturday, Sunday or Monday, refer to last Friday
        if ref_date.weekday() >= 5 or ref_date.weekday() == 0:
            ref_date = ref_date + timedelta(days=+1)
            while ref_date.weekday() > 4:
                ref_date = ref_date + timedelta(days=+1)
        else:
            ref_date = ref_date + timedelta(days=+1)
        return date(ref_date.year, ref_date.month, ref_date.day)

    def __repr__(self):
        return "<TimeDataModel(id='{}')>".format(self.id)


class TimeAsyncDataModel(AsyncDataModel):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(TimeAsyncDataModel, self).__init__()
        self.periods: dict[str, Period] | None = None
        self.intervals: dict[str, Interval] | None = None
        self.day_times: dict[str, DayTime] | None = None
        self.country_holidays: dict[int, CountryHoliday] | None = None
        self.financial_country_holidays: dict[int, FinancialCountryHoliday] | None = None
        self.financial_holidays: dict[int, FinancialHoliday] | None = None

    @async_timed
    async def _load(self) -> None:
        await super(TimeAsyncDataModel, self)._load()
        if self.daos is not None:
            self.periods = await self.daos["period"].get()
            self.intervals = await self.daos["interval"].get()
            self.day_times = await self.daos["day_time"].get()
            self.country_holidays = await self.daos["country_holiday"].get_nexts()
            self.financial_country_holidays = await self.daos["financial_country_holiday"].get()
            self.financial_holidays = await self.daos["financial_holiday"].get_nexts()

    @async_timed
    def _clear(self) -> None:
        pass

    @staticmethod
    def get_previous_business_date(ref_date: date) -> date:
        # on Saturday, Sunday or Monday, refer to last Friday
        if ref_date.weekday() >= 5 or ref_date.weekday() == 0:
            ref_date = ref_date + timedelta(days=-1)
            while ref_date.weekday() > 4:
                ref_date = ref_date + timedelta(days=-1)
        else:
            ref_date = ref_date + timedelta(days=-1)
        return date(ref_date.year, ref_date.month, ref_date.day)

    @staticmethod
    def get_next_business_date(ref_date: date) -> date:
        # on Saturday, Sunday or Monday, refer to last Friday
        if ref_date.weekday() >= 5 or ref_date.weekday() == 0:
            ref_date = ref_date + timedelta(days=+1)
            while ref_date.weekday() > 4:
                ref_date = ref_date + timedelta(days=+1)
        else:
            ref_date = ref_date + timedelta(days=+1)
        return date(ref_date.year, ref_date.month, ref_date.day)

    def __repr__(self):
        return "<TimeAsyncDataModel(id='{}')>".format(self.id)
