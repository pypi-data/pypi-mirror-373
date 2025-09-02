#  Copyright (c) 2023 bastien.saltel
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

from django.db.models.fields import AutoField,                                  \
                                    SmallAutoField,                             \
                                    CharField,                                  \
                                    BooleanField,                               \
                                    SmallIntegerField,                          \
                                    IntegerField,                               \
                                    FloatField,                                 \
                                    DateField,                                  \
                                    DateTimeField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE

from galaxy.data.db.djangodb import AuditableModel,                             \
                                    UUIDAuditableModel
from galaxy.data.db.orm.django.iso import Country,                              \
                                          Currency,                             \
                                          MarketExchange
from galaxy.data.db.orm.django.institution import Bank,                         \
                                                  RegulatoryAuthority
from galaxy.data.db.orm.django.company import Company,                          \
                                              SoftwareVendor,                   \
                                              DataVendor


class FinanceModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "finance"
        abstract = True


class FinanceUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "finance"
        abstract = True


class ExerciseStyle(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=4,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<ExerciseStyle(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."exercise_style"'


class OptionType(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=1,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<OptionType(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."option_type"'


class ExpirationType(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=1,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<ExpirationType(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."expiration_type"'


class PayoffType(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<PayoffType(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."payoff_type"'


class DeliveryType(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=4,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<DeliveryType(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."delivery_type"'


class DeliveryMonth(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=1,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=3)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=10)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<DeliveryMonth(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."delivery_month"'


class InstrumentClass(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                primary_key=True)
    cfi: CharField = CharField(db_column="cfi",
                               max_length=1)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    derivative: BooleanField = BooleanField(db_column="derivative")

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<InstrumentClass(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."instrument_class"'


class IssuerType(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<IssuerType(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."issuer_type"'


class STIRColor(FinanceModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    year_nb: SmallIntegerField = SmallIntegerField(db_column="year_nb")
    name: CharField = CharField(db_column="name",
                                max_length=20)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<STIRColor(id='{}')>".format(self.id)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."stir_color"'


class ProductFamily(FinanceModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=8)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=80)
    clearing_name: CharField = CharField(db_column="clearing_name",
                                         max_length=80,
                                         null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<ProductFamily(id='{}')>".format(self.id)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."product_family"'


class STIRProductGroup(FinanceModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50)
    trading_name: CharField = CharField(db_column="trading_name",
                                        max_length=20,
                                        null=True)
    color: ForeignKey = ForeignKey("STIRColor",
                                   db_column="color_id",
                                   on_delete=CASCADE,
                                   null=True)
    instrument_class: ForeignKey = ForeignKey("InstrumentClass",
                                              db_column="class_code",
                                              on_delete=CASCADE)
    family: ForeignKey = ForeignKey("ProductFamily",
                                    db_column="family_id",
                                    on_delete=CASCADE,
                                    null=True)
    expiration: ForeignKey = ForeignKey("ExpirationType",
                                        db_column="expiration_code",
                                        on_delete=CASCADE,
                                        null=True)
    nb_expiration: SmallIntegerField(db_column="nb_expiration")

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<STIRProductGroup(id='{}')>".format(self.id)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."stir_product_group"'


class Product(FinanceModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=120)
    nickname: CharField = CharField(db_column="nickname",
                                    max_length=80,
                                    null=True)
    cfi: CharField = CharField(db_column="cfi",
                               max_length=6,
                               null=True)
    isin: CharField = CharField(db_column="isin",
                                max_length=12,
                                null=True)
    cusip: CharField = CharField(db_column="cusip",
                                 max_length=8,
                                 null=True)
    sedol: CharField = CharField(db_column="sedol",
                                 max_length=7,
                                 null=True)
    ric: CharField = CharField(db_column="ric",
                               max_length=10,
                               null=True)
    symbol: CharField = CharField(db_column="symbol",
                                  max_length=10,
                                  null=True)
    instrument_class: ForeignKey = ForeignKey("InstrumentClass",
                                              db_column="class_code",
                                              on_delete=CASCADE)
    family: ForeignKey = ForeignKey("ProductFamily",
                                    db_column="family_id",
                                    on_delete=CASCADE,
                                    null=True)
    parent: ForeignKey = ForeignKey("Product",
                                    db_column="parent_id",
                                    on_delete=CASCADE,
                                    null=True)
    underlying: ForeignKey = ForeignKey("Product",
                                        db_column="underlying_id",
                                        on_delete=CASCADE,
                                        null=True)
    currency: ForeignKey = ForeignKey(Currency,
                                      db_column="currency_iso3",
                                      on_delete=CASCADE,
                                      null=True)
    exercise: ForeignKey = ForeignKey("ExerciseStyle",
                                      db_column="exercise_code",
                                      on_delete=CASCADE,
                                      null=True)
    payoff: ForeignKey = ForeignKey("PayoffType",
                                    db_column="payoff_code",
                                    on_delete=CASCADE,
                                    null=True)
    delivery: ForeignKey = ForeignKey("DeliveryType",
                                      db_column="delivery_code",
                                      on_delete=CASCADE,
                                      null=True)
    contract_size: FloatField = FloatField(db_column="contract_size",
                                           null=True)
    coupon_rate: FloatField = FloatField(db_column="coupon_rate",
                                         null=True)
    notional_value: IntegerField = IntegerField(db_column="notional_value",
                                                null=True)
    tick_size: FloatField = FloatField(db_column="tick_size",
                                       null=True)
    tick_value: FloatField = FloatField(db_column="tick_value",
                                        null=True)
    max_price: FloatField = FloatField(db_column="max_price",
                                       null=True)
    quote_min_quantity: FloatField = FloatField(db_column="quote_min_quantity",
                                                null=True)
    max_order_quantity: FloatField = FloatField(db_column="max_order_quantity",
                                                null=True)
    max_tes_quantity: FloatField = FloatField(db_column="max_tes_quantity",
                                              null=True)
    max_future_spread_quantity: IntegerField = IntegerField(db_column="max_future_spread_quantity",
                                                            null=True)
    max_market_order_quantity: IntegerField = IntegerField(db_column="max_market_order_quantity",
                                                           null=True)
    position_limit: IntegerField = IntegerField(db_column="position_limit",
                                                null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Product(id='{}')>".format(self.id)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."product"'


class ProductSerie(FinanceUUIDModel):
    """
    classdocs
    """

    name: CharField = CharField(db_column="name",
                                max_length=80)
    instrument_class: ForeignKey = ForeignKey("InstrumentClass",
                                              db_column="class_code",
                                              on_delete=CASCADE)
    underlying: ForeignKey = ForeignKey("ProductSerie",
                                        db_column="underlying_id",
                                        on_delete=CASCADE,
                                        null=True)
    expiration_date: DateTimeField = DateTimeField(db_colunn="expiration_date",
                                                   null=True)
    expiration_month: DateField = DateField(db_colunn="expiration_month",
                                            null=True)
    delivery_date: DateField = DateField(db_colunn="delivery_date",
                                         null=True)
    last_trading_date: DateTimeField = DateTimeField(db_colunn="last_trading_date",
                                                     null=True)
    stir_group: ForeignKey = ForeignKey("STIRProductGroup",
                                        db_column="stir_group_id",
                                        on_delete=CASCADE,
                                        null=True)
    exercise: ForeignKey = ForeignKey("ExerciseStyle",
                                      db_column="exercise_code",
                                      on_delete=CASCADE,
                                      null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<ProductSerie(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."product_serie"'


class Issuer(FinanceModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    issuer_type: ForeignKey = ForeignKey("IssuerType",
                                         db_column="type_code",
                                         on_delete=CASCADE)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=120)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Issuer(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."issuer"'


class Instrument(FinanceUUIDModel):
    """
    classdocs
    """

    instrument_class: ForeignKey = ForeignKey("InstrumentClass",
                                              db_column="class_code",
                                              on_delete=CASCADE)
    exchange: ForeignKey = ForeignKey(MarketExchange,
                                      db_column="exchange_mic",
                                      on_delete=CASCADE)
    cfi: CharField = CharField(db_column="cfi",
                               max_length=6,
                               null=True)
    isin: CharField = CharField(db_column="isin",
                                max_length=12,
                                null=True)
    cusip: CharField = CharField(db_column="cusip",
                                 max_length=8,
                                 null=True)
    nsin: CharField = CharField(db_column="nsin",
                                max_length=9,
                                null=True)
    sedol: CharField = CharField(db_column="sedol",
                                 max_length=7,
                                 null=True)
    ric: CharField = CharField(db_column="ric",
                               max_length=20,
                               null=True)
    symbol: CharField = CharField(db_column="symbol",
                                  max_length=10,
                                  null=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=120)
    product: ForeignKey = ForeignKey("Product",
                                     db_column="product_id",
                                     on_delete=CASCADE,
                                     null=True)
    serie: ForeignKey = ForeignKey("ProductSerie",
                                   db_column="serie_id",
                                   on_delete=CASCADE,
                                   null=True)
    currency: ForeignKey = ForeignKey(Currency,
                                      db_column="currency_iso3",
                                      on_delete=CASCADE)
    issuer: ForeignKey = ForeignKey("Issuer",
                                    db_column="issuer_id",
                                    on_delete=CASCADE)
    underlying: ForeignKey = ForeignKey("Instrument",
                                        db_column="underlying_id",
                                        on_delete=CASCADE,
                                        null=True)
    expiration_date: DateTimeField = DateTimeField(db_colunn="expiration_date",
                                                   null=True)
    delivery_date: DateField = DateField(db_colunn="delivery_date",
                                         null=True)
    maturity_date: DateField = DateField(db_colunn="maturity_date",
                                         null=True)
    strike_price: FloatField = FloatField(db_column="strike_price",
                                          null=True)
    option_tyoe: ForeignKey = ForeignKey("OptionType",
                                         db_column="option_type_code",
                                         on_delete=CASCADE,
                                         null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Instrument(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."instrument"'


class Straddle(FinanceUUIDModel):
    """
    classdocs
    """

    call: ForeignKey = ForeignKey("Instrument",
                                  db_column="call_id",
                                  on_delete=CASCADE)
    put: ForeignKey = ForeignKey("Instrument",
                                 db_column="put_id",
                                 on_delete=CASCADE)
    exchange: ForeignKey = ForeignKey(MarketExchange,
                                      db_column="exchange_mic",
                                      on_delete=CASCADE)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=120)
    serie: ForeignKey = ForeignKey("ProductSerie",
                                   db_column="serie_id",
                                   on_delete=CASCADE,
                                   null=True)
    currency: ForeignKey = ForeignKey(Currency,
                                      db_column="currency_iso3",
                                      on_delete=CASCADE)
    underlying: ForeignKey = ForeignKey("Instrument",
                                        db_column="underlying_id",
                                        on_delete=CASCADE,
                                        null=True)
    expiration_date: DateTimeField = DateTimeField(db_colunn="expiration_date",
                                                   null=True)
    delivery_date: DateField = DateField(db_colunn="delivery_date",
                                         null=True)
    maturity_date: DateField = DateField(db_colunn="maturity_date",
                                         null=True)
    strike_price: FloatField = FloatField(db_column="strike_price",
                                          null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Straddle(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."straddle"'


class StrategyType(FinanceModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<StrategyType(code='{}')>".format(self.code)

    class Meta(FinanceModel.Meta):
        db_table = '"finance"."stratgey_type"'


class Strategy(FinanceUUIDModel):
    """
    classdocs
    """

    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=120)
    strategy_tyoe: ForeignKey = ForeignKey("StrategyType",
                                           db_column="strategy_type_code",
                                           on_delete=CASCADE,
                                           null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Strategy(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."strategy"'


class StrategyInstrument(FinanceUUIDModel):
    """
    classdocs
    """

    strategy: ForeignKey = ForeignKey("Strategy",
                                      db_column="strategy_id",
                                      on_delete=CASCADE)
    instrument: ForeignKey = ForeignKey("Instrument",
                                        db_column="instrument_id",
                                        on_delete=CASCADE)
    quantity: SmallIntegerField = SmallIntegerField(db_column="quantity")

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<StrategyInstrument(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."strategy_instrument"'


class DataProvider(FinanceModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=3)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    exchange: ForeignKey = ForeignKey(MarketExchange,
                                      db_column="exchange_mic",
                                      on_delete=CASCADE,
                                      null=True)
    bank: ForeignKey = ForeignKey(Bank,
                                  db_column="bank_id",
                                  on_delete=CASCADE,
                                  null=True)
    software_vendor: ForeignKey = ForeignKey(SoftwareVendor,
                                             db_column="software_vendor_id",
                                             on_delete=CASCADE,
                                             null=True)
    data_vendor: ForeignKey = ForeignKey(DataVendor,
                                         db_column="data_vendor_id",
                                         on_delete=CASCADE,
                                         null=True)
    reg_authority: ForeignKey = ForeignKey(RegulatoryAuthority,
                                           db_column="authority_code",
                                           on_delete=CASCADE,
                                           null=True)
    start_date: DateField = DateField(db_colunn="start_date")
    end_date: DateField = DateField(db_colunn="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<DataProvider(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."data_provider"'


class DataProviderSystem(FinanceModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=3)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    account_id: CharField = CharField(db_column="account_id",
                                      max_length=10)
    company: ForeignKey = ForeignKey(Company,
                                     db_column="company_id",
                                     on_delete=CASCADE)
    provider: ForeignKey = ForeignKey("DataProvider",
                                      db_column="provider_id",
                                      on_delete=CASCADE)
    start_date: DateField = DateField(db_colunn="start_date")
    end_date: DateField = DateField(db_colunn="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<DataProviderSystem(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."data_provider_system"'


class InstrumentClassMap(FinanceModel):
    """
    classdocs
    """

    instrument_class: ForeignKey = ForeignKey("InstrumentClass",
                                              db_column="class_code",
                                              on_delete=CASCADE)
    provider: ForeignKey = ForeignKey("DataProvider",
                                      db_column="provider_id",
                                      on_delete=CASCADE)
    id: CharField = CharField(db_column="id",
                              max_length=10)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<InstrumentClassMap(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."instrument_class_map"'


class ProductMap(FinanceModel):
    """
    classdocs
    """

    product: ForeignKey = ForeignKey("Product",
                                     db_column="product_id",
                                     on_delete=CASCADE)
    provider: ForeignKey = ForeignKey("DataProvider",
                                      db_column="provider_id",
                                      on_delete=CASCADE)
    id: CharField = CharField(db_column="id",
                              max_length=10)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<ProductMap(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."product_map"'


class ProductSerieMap(FinanceModel):
    """
    classdocs
    """

    serie: ForeignKey = ForeignKey("ProductSerie",
                                   db_column="serie_id",
                                   on_delete=CASCADE)
    provider: ForeignKey = ForeignKey("DataProvider",
                                      db_column="provider_id",
                                      on_delete=CASCADE)
    id: CharField = CharField(db_column="id",
                              max_length=10)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<ProductSerieMap(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."product_serie_map"'


class InstrumentMap(FinanceModel):
    """
    classdocs
    """

    instrument: ForeignKey = ForeignKey("Instrument",
                                        db_column="instrument_id",
                                        on_delete=CASCADE)
    provider: ForeignKey = ForeignKey("DataProvider",
                                      db_column="provider_id",
                                      on_delete=CASCADE)
    id: CharField = CharField(db_column="id",
                              max_length=10)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<InstrumentMap(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."instrument_map"'


class StrategyMap(FinanceModel):
    """
    classdocs
    """

    strategy: ForeignKey = ForeignKey("Strategy",
                                      db_column="strategy_id",
                                      on_delete=CASCADE)
    provider: ForeignKey = ForeignKey("DataProvider",
                                      db_column="provider_id",
                                      on_delete=CASCADE)
    id: CharField = CharField(db_column="id",
                              max_length=10)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<StrategyMap(id='{}')>".format(self.id)

    class Meta(FinanceUUIDModel.Meta):
        db_table = '"finance"."strategy_map"'
