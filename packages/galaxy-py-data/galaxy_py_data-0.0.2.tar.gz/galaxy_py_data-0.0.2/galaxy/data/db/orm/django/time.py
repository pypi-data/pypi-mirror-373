#  Copyright (c) 2023 Sucden Financial Limited.
#
#  Written by bastien.saltel.
#

from django.db.models.fields import AutoField,                      \
                                    CharField,                      \
                                    BooleanField,                   \
                                    DateField,                      \
                                    TimeField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE

from galaxy.data.db.djangodb import AuditableModel,                 \
                                    UUIDAuditableModel
from galaxy.data.db.orm.django.iso import Country,                  \
                                          MarketExchange
from galaxy.data.db.orm.django.institution import CentralBank


class TimeModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "time"
        abstract = True


class TimeUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "time"
        abstract = True


class Period(TimeModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                null=False,
                                blank=False,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return "<Period(cfi='{}')>".format(self.code)

    class Meta(TimeModel.Meta):
        db_table = '"time"."period"'


class Interval(TimeModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                null=False,
                                blank=False,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return "<Interval(cfi='{}')>".format(self.code)

    class Meta(TimeModel.Meta):
        db_table = '"time"."interval"'


class DayTime(TimeModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                null=False,
                                blank=False,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return "<DayTime(cfi='{}')>".format(self.code)

    class Meta(TimeModel.Meta):
        db_table = '"time"."day_time"'


class CountryHoliday(TimeModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              null=False,
                              primary_key=True)
    holiday_date: DateField = DateField(db_column="holiday_date",
                                        null=False)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=True)
    subdivision: CharField = CharField(db_column="subdivision",
                                       max_length=20,
                                       null=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=True)
    is_public: BooleanField = BooleanField(db_column="is_public",
                                           null=False)
    is_bank: BooleanField = BooleanField(db_column="is_bank",
                                         null=False)
    is_armed_forces: BooleanField = BooleanField(db_column="is_armed_forces",
                                                 null=False)
    is_gov: BooleanField = BooleanField(db_column="is_gov",
                                        null=False)
    is_opt: BooleanField = BooleanField(db_column="is_opt",
                                        null=False)
    is_school: BooleanField = BooleanField(db_column="is_school",
                                           null=False)
    is_workday: BooleanField = BooleanField(db_column="is_workday",
                                            null=False)
    is_half: BooleanField = BooleanField(db_column="is_half",
                                         null=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CountryHoliday(id='{}')>".format(self.id)

    class Meta(TimeModel.Meta):
        db_table = '"time"."country_holiday"'


class FinancialCountryHoliday(TimeModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              null=False,
                              primary_key=True)
    exchange: ForeignKey = ForeignKey(MarketExchange,
                                      db_column="exchange_mic",
                                      on_delete=CASCADE,
                                      null=True)
    central_bank: ForeignKey = ForeignKey(CentralBank,
                                          db_column="central_bank_id",
                                          on_delete=CASCADE,
                                          null=True)
    holiday: ForeignKey = ForeignKey(CountryHoliday,
                                     db_column="holiday_id",
                                     on_delete=CASCADE,
                                     null=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<FinancialCountryHoliday(id='{}')>".format(self.id)

    class Meta(TimeModel.Meta):
        db_table = '"time"."financial_country_holiday"'


class FinancialHoliday(TimeModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              null=False,
                              primary_key=True)
    holiday_date: DateField = DateField(db_column="holiday_date",
                                        null=False)
    exchange: ForeignKey = ForeignKey(MarketExchange,
                                      db_column="exchange_mic",
                                      on_delete=CASCADE,
                                      null=True)
    central_bank: ForeignKey = ForeignKey(CentralBank,
                                          db_column="central_bank_id",
                                          on_delete=CASCADE,
                                          null=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=True)
    start_time: TimeField = TimeField(db_column="start_time",
                                      null=True)
    end_time: TimeField = TimeField(db_column="end_time",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<FinancialHoliday(id='{}')>".format(self.id)

    class Meta(TimeModel.Meta):
        db_table = '"time"."financial_holiday"'
