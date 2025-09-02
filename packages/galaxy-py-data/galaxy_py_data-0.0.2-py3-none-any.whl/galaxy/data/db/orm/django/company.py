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

from django.db.models.fields import AutoField,                              \
                                    SmallAutoField,                         \
                                    CharField,                              \
                                    DateField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE

from galaxy.data.db.djangodb import AuditableModel,                         \
                                    UUIDAuditableModel
from galaxy.data.db.orm.django.iso import Country,                          \
                                          PhonePrefix,                      \
                                          MarketExchange
from galaxy.data.db.orm.django.institution import Bank,                     \
                                                  RegulatoryAuthority


class CompanyModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "company"
        abstract = True


class CompanyUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "company"
        abstract = True


class Sex(CompanyModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=4,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<Sex(code='{}')>".format(self.code)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."sex"'


class Title(CompanyModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=4,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<Title(code='{}')>".format(self.code)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."title"'


class ClearingType(CompanyModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=4,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=20)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return "<ClearingType(code='{}')>".format(self.code)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."clearing_type"'


class Company(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    legal_name: CharField = CharField(db_column="legal_name",
                                      max_length=80,
                                      null=True)
    lei: CharField = CharField(db_column="lei",
                               max_length=20,
                               null=True)
    managing_lou: CharField = CharField(db_column="managing_lou",
                                        max_length=20,
                                        null=True)
    office_reg_num: CharField = CharField(db_column="office_reg_num",
                                          max_length=8,
                                          null=True)
    business_reg_num: CharField = CharField(db_column="business_reg_num",
                                            max_length=8,
                                            null=True)
    business_reg_entity_id: CharField = CharField(db_column="business_reg_entity_id",
                                                  max_length=8,
                                                  null=True)
    vat: CharField = CharField(db_column="vat",
                               max_length=20,
                               null=True)
    business_unit: CharField = CharField(db_column="business_unit",
                                         max_length=20,
                                         null=True)
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
    legal_building: CharField = CharField(db_column="legal_building",
                                          max_length=80,
                                          null=True)
    legal_street_num: CharField = CharField(db_column="legal_street_num",
                                            max_length=10,
                                            null=True)
    legal_street: CharField = CharField(db_column="legal_street",
                                        max_length=120,
                                        null=True)
    legal_address1: CharField = CharField(db_column="legal_address1",
                                          max_length=250,
                                          null=True)
    legal_address2: CharField = CharField(db_column="legal_address2",
                                          max_length=250,
                                          null=True)
    legal_address3: CharField = CharField(db_column="legal_address3",
                                          max_length=250,
                                          null=True)
    legal_zip_code: CharField = CharField(db_column="legal_zip_code",
                                          max_length=10,
                                          null=True)
    legal_city: CharField = CharField(db_column="legal_city",
                                      max_length=80,
                                      null=True)
    legal_country: ForeignKey = ForeignKey(Country,
                                           db_column="legal_country_iso2",
                                           on_delete=CASCADE,
                                           null=True)
    phone: CharField = CharField(db_column="phone",
                                 max_length=20,
                                 null=True)
    phone_prefix: ForeignKey = ForeignKey(PhonePrefix,
                                          db_column="phone_prefix_id",
                                          on_delete=CASCADE,
                                          null=True)
    fax: CharField = CharField(db_column="fax",
                               max_length=20,
                               null=True)
    fax_prefix: ForeignKey = ForeignKey(PhonePrefix,
                                        db_column="fax_prefix_id",
                                        on_delete=CASCADE,
                                        null=True)
    website: CharField = CharField(db_column="website",
                                   max_length=250,
                                   null=True)
    holding: ForeignKey = ForeignKey("Company",
                                     db_column="holding_id",
                                     on_delete=CASCADE,
                                     null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Company(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."company"'


class Employee(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    sex: ForeignKey = ForeignKey("Sex",
                                 db_column="sex_code",
                                 on_delete=CASCADE)
    title: ForeignKey = ForeignKey("Title",
                                   db_column="title_code",
                                   on_delete=CASCADE)
    firstname: CharField = CharField(db_column="firstname",
                                     max_length=80)
    full_firstname: CharField = CharField(db_column="full_firstname",
                                          max_length=120,
                                          null=True)
    middlename: CharField = CharField(db_column="middlename",
                                      max_length=80,
                                      null=True)
    initial: CharField = CharField(db_column="initial",
                                   max_length=10,
                                   null=True)
    surname: CharField = CharField(db_column="surname",
                                   max_length=80,
                                   null=True)
    full_surname: CharField = CharField(db_column="full_surname",
                                        max_length=120,
                                        null=True)
    nationality: ForeignKey = ForeignKey(Country,
                                         db_column="nationality_iso2",
                                         on_delete=CASCADE,
                                         null=True)
    birth_date: DateField = DateField(db_column="birth_date",
                                      null=True)
    birth_city: CharField = CharField(db_column="birth_city",
                                      max_length=80,
                                      null=True)
    birth_country: ForeignKey = ForeignKey(Country,
                                           db_column="birth_country_iso2",
                                           on_delete=CASCADE,
                                           null=True)
    passport_num: CharField = CharField(db_column="passport_num",
                                        max_length=9,
                                        null=True)
    passport_country: ForeignKey = ForeignKey(Country,
                                              db_column="passport_country_iso2",
                                              on_delete=CASCADE,
                                              null=True)
    passport_issue_date: DateField = DateField(db_column="passport_issue_date",
                                               null=True)
    passport_expiry_date: DateField = DateField(db_column="passport_expiry_date",
                                                null=True)
    nin_num: CharField = CharField(db_column="nin_num",
                                   max_length=9,
                                   null=True)
    email: CharField = CharField(db_column="email",
                                 max_length=120,
                                 null=True)
    phone: CharField = CharField(db_column="phone",
                                 max_length=20,
                                 null=True)
    phone_prefix: ForeignKey = ForeignKey(PhonePrefix,
                                          db_column="phone_prefix_id",
                                          on_delete=CASCADE,
                                          null=True)
    mobile: CharField = CharField(db_column="mobile",
                                  max_length=20,
                                  null=True)
    mobile_prefix: ForeignKey = ForeignKey(PhonePrefix,
                                           db_column="mobile_prefix_id",
                                           on_delete=CASCADE,
                                           null=True)
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

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Employee(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."employee"'


class Employment(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    company: ForeignKey = ForeignKey("Company",
                                     db_column="company_id",
                                     on_delete=CASCADE)
    employee: ForeignKey = ForeignKey("Employee",
                                      db_column="employee_id",
                                      on_delete=CASCADE)
    start_date: DateField = DateField(db_column="start_date")
    end_date: DateField = DateField(db_column="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Employment(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."employment"'


class SoftwareVendor(CompanyModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=3)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=120)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SoftwareVendor(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."software_vendor"'


class DataVendor(CompanyModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=3)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    fullname: CharField = CharField(db_column="fullname",
                                    max_length=120)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<DataVendor(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."data_vendor"'


class ExchangeMembership(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    company: ForeignKey = ForeignKey("Company",
                                     db_column="company_id",
                                     on_delete=CASCADE)
    code: CharField = CharField(db_column="code",
                                max_length=10)
    rim_code: CharField = CharField(db_column="rim_code",
                                    max_length=10,
                                    null=True)
    exchange: ForeignKey = ForeignKey(MarketExchange,
                                      db_column="exchange_mic",
                                      on_delete=CASCADE)
    start_date: DateField = DateField(db_column="start_date")
    end_date: DateField = DateField(db_column="end_date",
                                    null=True)
    clearing_code: CharField = CharField(db_column="clearing_code",
                                         max_length=5,
                                         null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<ExchangeMembership(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."exchange_membership"'


class CompanyClearingBank(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    company: ForeignKey = ForeignKey("Company",
                                     db_column="company_id",
                                     on_delete=CASCADE)
    bank: ForeignKey = ForeignKey(Bank,
                                  db_column="bank_id",
                                  on_delete=CASCADE)
    start_date: DateField = DateField(db_column="start_date")
    end_date: DateField = DateField(db_column="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CompanyClearingBank(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."clearing_bank"'


class CompanyBank(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    company: ForeignKey = ForeignKey("Company",
                                     db_column="company_id",
                                     on_delete=CASCADE)
    bank: ForeignKey = ForeignKey(Bank,
                                  db_column="bank_id",
                                  on_delete=CASCADE)
    start_date: DateField = DateField(db_column="start_date")
    end_date: DateField = DateField(db_column="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CompanyBank(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."bank"'


class RegulatoryMembership(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    company: ForeignKey = ForeignKey("Company",
                                     db_column="company_id",
                                     on_delete=CASCADE)
    code: CharField = CharField(db_column="code",
                                max_length=10)
    bank: ForeignKey = ForeignKey(RegulatoryAuthority,
                                  db_column="authority_code",
                                  on_delete=CASCADE)
    start_date: DateField = DateField(db_column="start_date")
    end_date: DateField = DateField(db_column="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<RegulatoryMembership(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."regulatory_membership"'


class CompanySoftwareVendor(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    company: ForeignKey = ForeignKey("Company",
                                     db_column="company_id",
                                     on_delete=CASCADE)
    code: CharField = CharField(db_column="code",
                                max_length=10)
    vendor: ForeignKey = ForeignKey("SoftwareVendor",
                                    db_column="vendor_id",
                                    on_delete=CASCADE)
    start_date: DateField = DateField(db_column="start_date")
    end_date: DateField = DateField(db_column="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CompanySoftwareVendor(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."company_software_vendor"'


class CompanyDataVendor(CompanyModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    company: ForeignKey = ForeignKey("Company",
                                     db_column="company_id",
                                     on_delete=CASCADE)
    code: CharField = CharField(db_column="code",
                                max_length=10)
    vendor: ForeignKey = ForeignKey("DataVendor",
                                    db_column="vendor_id",
                                    on_delete=CASCADE)
    start_date: DateField = DateField(db_column="start_date")
    end_date: DateField = DateField(db_column="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<CompanyDataVendor(id='{}')>".format(self.id)

    class Meta(CompanyModel.Meta):
        db_table = '"company"."company_data_vendor"'
