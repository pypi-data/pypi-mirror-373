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

from datetime import date
from dataclasses import dataclass,                                  \
                        field
from typing import Optional

from galaxy.data.model.model import DataModel
from galaxy.data.model.iso import Country,                          \
                                  PhonePrefix,                      \
                                  MarketExchange
from galaxy.data.model.institution import Bank,                     \
                                          RegulatoryAuthority


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
class Sex(object):
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
class Title(object):
    """
    classdocs
    """
    code: str
    name: str | None = field(init=False, default=None)

    def __str__(self) -> str:
        return self.code


class ClearingType(object):
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
class Company(object):
    """
    classdocs
    """
    id: int
    name: str | None = field(init=False, default=None)
    legal_name: str | None = field(init=False, default=None)
    lei: str | None = field(init=False, default=None)
    managing_lou: str | None = field(init=False, default=None)
    office_reg_num: str | None = field(init=False, default=None)
    business_reg_num: str | None = field(init=False, default=None)
    business_reg_entity_id: str | None = field(init=False, default=None)
    vat: str | None = field(init=False, default=None)
    business_unit: str | None = field(init=False, default=None)
    building: str | None = field(init=False, default=None)
    street_num: str | None = field(init=False, default=None)
    street: str | None = field(init=False, default=None)
    address1: str | None = field(init=False, default=None)
    address2: str | None = field(init=False, default=None)
    address3: str | None = field(init=False, default=None)
    zip_code: str | None = field(init=False, default=None)
    city: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)
    legal_building: str | None = field(init=False, default=None)
    legal_street_num: str | None = field(init=False, default=None)
    legal_street: str | None = field(init=False, default=None)
    legal_address1: str | None = field(init=False, default=None)
    legal_address2: str | None = field(init=False, default=None)
    legal_address3: str | None = field(init=False, default=None)
    legal_zip_code: str | None = field(init=False, default=None)
    legal_city: str | None = field(init=False, default=None)
    legal_country_iso2: str | None = field(init=False, default=None)
    phone: str | None = field(init=False, default=None)
    phone_prefix_id: int | None = field(init=False, default=None)
    fax: str | None = field(init=False, default=None)
    fax_prefix_id: int | None = field(init=False, default=None)
    website: str | None = field(init=False, default=None)
    holding_id: int | None = field(init=False, default=None)

    country: Country | None = field(init=False, default=None)
    legal_country: Country | None = field(init=False, default=None)
    phone_prefix: PhonePrefix | None = field(init=False, default=None)
    fax_prefix: PhonePrefix | None = field(init=False, default=None)
    holding: Optional["Company"] = field(init=False, default=None)

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
class Employee(object):
    """
    classdocs
    """
    id: int
    sex_code: str | None = field(init=False, default=None)
    title_code: str | None = field(init=False, default=None)
    firstname: str | None = field(init=False, default=None)
    full_firstname: str | None = field(init=False, default=None)
    middlename: str | None = field(init=False, default=None)
    initial: str | None = field(init=False, default=None)
    surname: str | None = field(init=False, default=None)
    full_surname: str | None = field(init=False, default=None)
    nationality_iso2: str | None = field(init=False, default=None)
    birth_date: date | None = field(init=False, default=None)
    birth_city: str | None = field(init=False, default=None)
    birth_country_iso2: str | None = field(init=False, default=None)
    passport_num: str | None = field(init=False, default=None)
    passport_country_iso2: str | None = field(init=False, default=None)
    passport_issue_date: date | None = field(init=False, default=None)
    passport_expiry_date: date | None = field(init=False, default=None)
    nin_num: str | None = field(init=False, default=None)
    email: str | None = field(init=False, default=None)
    phone: str | None = field(init=False, default=None)
    phone_prefix_id: int | None = field(init=False, default=None)
    mobile: str | None = field(init=False, default=None)
    mobile_prefix_id: int | None = field(init=False, default=None)
    building: str | None = field(init=False, default=None)
    street_num: str | None = field(init=False, default=None)
    street: str | None = field(init=False, default=None)
    address1: str | None = field(init=False, default=None)
    address2: str | None = field(init=False, default=None)
    address3: str | None = field(init=False, default=None)
    zip_code: str | None = field(init=False, default=None)
    city: str | None = field(init=False, default=None)
    country_iso2: str | None = field(init=False, default=None)

    sex: Sex | None = field(init=False, default=None)
    title: Title | None = field(init=False, default=None)
    nationality: Country| None = field(init=False, default=None)
    birth_country: Country| None = field(init=False, default=None)
    passport_country: Country| None = field(init=False, default=None)
    phone_prefix: PhonePrefix| None = field(init=False, default=None)
    mobile_prefix: PhonePrefix| None = field(init=False, default=None)

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
class Employment(object):
    """
    classdocs
    """
    id: int
    company_id: int | None = field(init=False, default=None)
    employee_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company| None = field(init=False, default=None)
    employee: Employee| None = field(init=False, default=None)

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
class SoftwareVendor(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)

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
class DataVendor(object):
    """
    classdocs
    """
    id: int
    code: str | None = field(init=False, default=None)
    name: str | None = field(init=False, default=None)
    fullname: str | None = field(init=False, default=None)

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
class ExchangeMembership(object):
    """
    classdocs
    """
    id: int
    company_id: int | None = field(init=False, default=None)
    code: str | None = field(init=False, default=None)
    rim_code: str | None = field(init=False, default=None)
    exchange_mic: str | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company| None = field(init=False, default=None)
    exchange: MarketExchange| None = field(init=False, default=None)

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
class CompanyClearingBank(object):
    """
    classdocs
    """
    id: int
    company_id: int | None = field(init=False, default=None)
    code: str | None = field(init=False, default=None)
    bank_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company| None = field(init=False, default=None)
    bank: Bank| None = field(init=False, default=None)

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
class CompanyBank(object):
    """
    classdocs
    """
    id: int
    company_id: int | None = field(init=False, default=None)
    code: str | None = field(init=False, default=None)
    bank_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company| None = field(init=False, default=None)
    bank: Bank| None = field(init=False, default=None)

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
class RegulatoryMembership(object):
    """
    classdocs
    """
    id: int
    company_id: int | None = field(init=False, default=None)
    code: str | None = field(init=False, default=None)
    authority_code: str | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company| None = field(init=False, default=None)
    authority: RegulatoryAuthority| None = field(init=False, default=None)

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
class CompanySoftwareVendor(object):
    """
    classdocs
    """
    id: int
    company_id: int | None = field(init=False, default=None)
    code: str | None = field(init=False, default=None)
    vendor_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company| None = field(init=False, default=None)
    vendor: SoftwareVendor| None = field(init=False, default=None)

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
class CompanyDataVendor(object):
    """
    classdocs
    """
    id: int
    company_id: int | None = field(init=False, default=None)
    code: str | None = field(init=False, default=None)
    vendor_id: int | None = field(init=False, default=None)
    start_date: date | None = field(init=False, default=None)
    end_date: date | None = field(init=False, default=None)

    company: Company| None = field(init=False, default=None)
    vendor: DataVendor| None = field(init=False, default=None)

    def __str__(self) -> str:
        return str(self.id)


class CompanyDataModel(DataModel):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(CompanyDataModel, self).__init__()
        self.sexes: dict[str, Sex] | None = None


    def _load_data(self):
        if self.loader is not None:
            pass

    def __repr__(self):
        return "<CompanyDataModel(id='{}')>".format(self.id)
