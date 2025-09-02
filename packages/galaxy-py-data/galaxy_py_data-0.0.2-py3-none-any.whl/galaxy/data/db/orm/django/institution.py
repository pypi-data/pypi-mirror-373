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

from django.db.models.fields import AutoField,                      \
                                    SmallAutoField,                 \
                                    CharField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE

from galaxy.data.db.djangodb import AuditableModel,                 \
                                    UUIDAuditableModel
from galaxy.data.db.orm.django.iso import Country,                  \
                                          PhonePrefix,              \
                                          Currency


class InstitutionModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "institution"
        abstract = True


class InstitutionUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "institution"
        abstract = True


class Bank(InstitutionModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              null=False,
                              primary_key=True)
    bic: CharField = CharField(db_column="bic",
                               max_length=11,
                               null=True)
    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False)
    sort_code: CharField = CharField(db_column="sort_code",
                                     max_length=6,
                                     null=True)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    building: CharField = CharField(db_column="building",
                                    max_length=80,
                                    null=True)
    street_num: CharField = CharField(db_column="street_num",
                                      max_length=10,
                                      null=True)
    street: CharField = CharField(db_column="street",
                                  max_length=120,
                                  null=True)
    address1: CharField = CharField(db_column="address1",
                                    max_length=250,
                                    null=True)
    address2: CharField = CharField(db_column="address2",
                                    max_length=250,
                                    null=True)
    address3: CharField = CharField(db_column="address3",
                                    max_length=250,
                                    null=True)
    zip_code: CharField = CharField(db_column="zip_code",
                                    max_length=10,
                                    null=True)
    city: CharField = CharField(db_column="city",
                                max_length=80,
                                null=True)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=True)
    phone: CharField = CharField(db_column="phone",
                                 max_length=20,
                                 null=True)
    phone_prefix: ForeignKey = ForeignKey(PhonePrefix,
                                          db_column="phone_prefix_id",
                                          on_delete=CASCADE,
                                          related_name="bank_phone_prefixes",
                                          null=True)
    fax: CharField = CharField(db_column="fax",
                               max_length=20,
                               null=True)
    fax_prefix: ForeignKey = ForeignKey(PhonePrefix,
                                        db_column="fax_prefix_id",
                                        on_delete=CASCADE,
                                        related_name="bank_fax_prefixes",
                                        null=True)
    website: CharField = CharField(db_column="website",
                                   max_length=250,
                                   null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Bank(id='{}')>".format(self.id)

    class Meta(InstitutionModel.Meta):
        db_table = '"institution"."bank"'


class BrokerGroup(InstitutionModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    bank: ForeignKey = ForeignKey(Bank,
                                  db_column="bank_id",
                                  on_delete=CASCADE,
                                  null=True)
    lei: CharField = CharField(db_column="lei",
                               max_length=20,
                               null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<BrokerGroup(id='{}')>".format(self.id)

    class Meta(InstitutionModel.Meta):
        db_table = '"institution"."broker_group"'


class Broker(InstitutionModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    group: ForeignKey = ForeignKey(BrokerGroup,
                                   db_column="group_id",
                                   on_delete=CASCADE,
                                   null=True)
    lei: CharField = CharField(db_column="lei",
                               max_length=20,
                               null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Broker(id='{}')>".format(self.id)

    class Meta(InstitutionModel.Meta):
        db_table = '"institution"."broker"'


class RegulatoryAuthority(InstitutionModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=True)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=False)
    website: CharField = CharField(db_column="website",
                                   max_length=250,
                                   null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<RegulatoryAuthority(id='{}')>".format(self.id)

    class Meta(InstitutionModel.Meta):
        db_table = '"institution"."regulatory_authority"'


class CentralBank(InstitutionModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=False)
    bank: ForeignKey = ForeignKey(Bank,
                                  db_column="bank_id",
                                  on_delete=CASCADE,
                                  null=True)
    currency: ForeignKey = ForeignKey(Currency,
                                      db_column="currency_iso3",
                                      on_delete=CASCADE,
                                      null=True)
    website: CharField = CharField(db_column="website",
                                   max_length=250,
                                   null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CentralBank(id='{}')>".format(self.id)

    class Meta(InstitutionModel.Meta):
        db_table = '"institution"."central_bank"'


class CentralSecuritiesDepository(InstitutionModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=False)
    bank: ForeignKey = ForeignKey(Bank,
                                  db_column="bank_id",
                                  on_delete=CASCADE,
                                  null=True)
    website: CharField = CharField(db_column="website",
                                   max_length=250,
                                   null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CentralSecuritiesDepository(id='{}')>".format(self.id)

    class Meta(InstitutionModel.Meta):
        db_table = '"institution"."csd"'


class Subcustodian(InstitutionModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    country: ForeignKey = ForeignKey(Country,
                                     db_column="country_iso2",
                                     on_delete=CASCADE,
                                     null=False)
    bank: ForeignKey = ForeignKey(Bank,
                                  db_column="bank_id",
                                  on_delete=CASCADE,
                                  null=True)
    website: CharField = CharField(db_column="website",
                                   max_length=250,
                                   null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Subcustodian(id='{}')>".format(self.id)

    class Meta(InstitutionModel.Meta):
        db_table = '"institution"."subcustodian"'
