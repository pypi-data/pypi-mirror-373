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

from django.db.models.fields import SmallAutoField,             \
                                    CharField,                  \
                                    IntegerField,               \
                                    BooleanField,               \
                                    DateField
from django.db.models.fields.related import ManyToManyField,    \
                                            ForeignKey
from django.db.models.deletion import CASCADE

from galaxy.data.db.djangodb import AuditableModel,             \
                                    UUIDAuditableModel


class IsoModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "iso"
        abstract = True


class IsoUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "iso"
        abstract = True


class Continent(IsoModel):
    """
    classdocs
    """

    iso2: CharField = CharField(db_column="iso2",
                                max_length=2,
                                null=False,
                                blank=False,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    countries: ManyToManyField = ManyToManyField("Country",
                                                 through="CountryContinent",
                                                 through_fields=("continent", "country"))

    def __str__(self) -> str:
        return str(self.iso2)

    def __repr__(self) -> str:
        return "<Continent(iso2='{}')>".format(self.iso2)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."continent"'


class Country(IsoModel):
    """
    classdocs
    """

    iso2: CharField = CharField(db_column="iso2",
                                max_length=2,
                                null=False,
                                blank=False,
                                primary_key=True)
    iso3: CharField = CharField(db_column="iso3",
                                max_length=3,
                                null=False,
                                blank=False)
    iso_code: IntegerField = IntegerField(db_column="iso_code",
                                          null=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=80,
                                    null=False,
                                    blank=False)
    iso_name: CharField = CharField(db_column="iso_name",
                                    max_length=80,
                                    null=False,
                                    blank=False)
    in_oecd: BooleanField = BooleanField(db_column="in_oecd",
                                         null=False)
    continents: ManyToManyField = ManyToManyField("Continent",
                                                  through="CountryContinent",
                                                  through_fields=("country", "continent"))
    currencies: ManyToManyField = ManyToManyField("Currency",
                                                  through="CountryCurrency",
                                                  through_fields=("country", "currency"))

    def __str__(self) -> str:
        return str(self.iso2)

    def __repr__(self) -> str:
        return "<Country(iso2='{}')>".format(self.iso2)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."country"'
        verbose_name = "Country"
        verbose_name_plural = "Countries"


class CountryContinent(IsoModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=False)
    continent: ForeignKey = ForeignKey(Continent,
                                       db_column="continent_iso2",
                                       on_delete=CASCADE,
                                       null=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CountryContinent(id='{}')>".format(self.id)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."country_continent"'


class CurrencyType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<CurrencyType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."currency_type"'


class Currency(IsoModel):
    """
    classdocs
    """

    iso3: CharField = CharField(db_column="iso3",
                                max_length=3,
                                null=False,
                                blank=False,
                                primary_key=True)
    iso_code: IntegerField = IntegerField(db_column="iso_code",
                                          null=True)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=80,
                                    null=False,
                                    blank=False)
    symbol: CharField = CharField(db_column="symbol",
                                  max_length=5,
                                  null=True)
    cur_type: ForeignKey = ForeignKey(CurrencyType,
                                      db_column="cfi",
                                      on_delete=CASCADE,
                                      null=False)
    countries: ManyToManyField = ManyToManyField("Country",
                                                 through="CountryCurrency",
                                                 through_fields=("currency", "country"))

    def __str__(self) -> str:
        return str(self.iso3)

    def __repr__(self) -> str:
        return "<Currency(iso3='{}')>".format(self.iso3)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."currency"'


class CountryCurrency(IsoModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=False)
    currency: ForeignKey = ForeignKey(Currency,
                                      db_column="currency_iso3",
                                      on_delete=CASCADE,
                                      null=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CountryCurrency(id='{}')>".format(self.id)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."country_currency"'


class PhonePrefix(IsoModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    prefix: IntegerField = IntegerField(db_column="prefix",
                                        null=False)
    country = ForeignKey(Country,
                         db_column="country_iso2",
                         on_delete=CASCADE,
                         null=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<PhonePrefix(id='{}')>".format(self.id)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."phone_prefix"'


class Language(IsoModel):
    """
    classdocs
    """

    iso3: CharField = CharField(db_column="iso3",
                                max_length=3,
                                null=False,
                                blank=False,
                                primary_key=True)
    iso2: CharField = CharField(db_column="iso2",
                                max_length=2,
                                null=True)
    iso639_3: CharField = CharField(db_column="iso639_3",
                                    max_length=3,
                                    null=True)
    iso639_3_other: CharField = CharField(db_column="iso639_3_other",
                                          max_length=3,
                                          null=True)
    iso639_1: CharField = CharField(db_column="iso639_1",
                                    max_length=3,
                                    null=True)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    scope_code: CharField = CharField(db_column="scope_code",
                                      max_length=1,
                                      null=True)
    type_code: CharField = CharField(db_column="type_code",
                                     max_length=1,
                                     null=True)

    def __str__(self) -> str:
        return str(self.iso3)

    def __repr__(self) -> str:
        return "<Language(iso3='{}')>".format(self.iso3)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."language"'


class MarketExchange(IsoModel):
    """
    classdocs
    """

    mic: CharField = CharField(db_column="mic",
                               max_length=4,
                               null=False,
                               blank=False,
                               primary_key=True)
    operating_mic: CharField = CharField(db_column="operating_mic",
                                         max_length=4,
                                         null=False,
                                         blank=False)
    lei: CharField = CharField(db_column="lei",
                               max_length=20,
                               null=True)
    name: CharField = CharField(db_column="name",
                                max_length=150,
                                null=False,
                                blank=False)
    acronym: CharField = CharField(db_column="acronym",
                                   max_length=20,
                                   null=True)
    city: CharField = CharField(db_column="city",
                                max_length=50,
                                null=True)
    website: CharField = CharField(db_column="website",
                                   max_length=250,
                                   null=True)
    open_date: DateField = DateField(db_column="open_date",
                                     null=True)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=True)

    def __str__(self) -> str:
        return str(self.mic)

    def __repr__(self) -> str:
        return "<MarketExchange(mic='{}')>".format(self.mic)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."market_exchange"'


class InstrumentCategory(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=80,
                                    null=True)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<InstrumentCategory(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."instrument_category"'


class InstrumentGroup(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=2,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=80,
                                    null=True)
    category: ForeignKey = ForeignKey(InstrumentCategory,
                                      db_column="category_cfi",
                                      on_delete=CASCADE,
                                      null=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<InstrumentGroup(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."instrument_group"'


class VotingRight(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<VotingRight(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."voting_right"'


class InstrumentOwnership(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<InstrumentOwnership(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."instrument_ownership"'


class PaymentStatus(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<PaymentStatus(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."payment_status"'


class IncomeType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<IncomeType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."income_type"'


class RedemptionConversionType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<RedemptionConversionType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."redemption_conversion_type"'


class DistributionType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<DistributionType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."distribution_type"'


class DistributionPolicy(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<DistributionPolicy(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."distribution_policy"'


class ClosedOpenEnd(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<ClosedOpenEnd(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."closed_open_end"'


class GuaranteeType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<GuaranteeType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."guarantee_type"'


class InterestType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<InterestType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."interest_type"'


class RedemptionReimbursementType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<RedemptionReimbursementType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."redemption_reimbursement"'


class SecurityType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<SecurityType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."security_type"'


class OptionType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<OptionType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."option_type"'


class WarrantType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<WarrantType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."warrant_type"'


class Termination(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<Termination(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."termination"'


class DeliveryType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<DeliveryType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."delivery_type"'


class WeightingType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<WeightingType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."weighting_type"'


class IndexReturnType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<IndexReturnType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."index_return_type"'


class BasketComposition(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<BasketComposition(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."basket_composition"'


class TimeFrequency(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<TimeFrequency(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."time_frequency"'


class EquityType(IsoModel):
    """
    classdocs
    """

    cfi: CharField = CharField(db_column="cfi",
                               max_length=1,
                               null=False,
                               blank=False,
                               primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.cfi)

    def __repr__(self) -> str:
        return "<EquityType(cfi='{}')>".format(self.cfi)

    class Meta(IsoModel.Meta):
        db_table = '"iso"."equity_type"'
