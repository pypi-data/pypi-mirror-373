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

from galaxy.utils.type import Id

Base = declarative_base()


class SQLAlchemySex(Base):
    """
    classdocs
    """

    __tablename__ = "company_sex"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemySex(id='{}')>".format(self.id)


class SQLAlchemyTitle(Base):
    """
    classdocs
    """

    __tablename__ = "company_title"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyTitle(id='{}')>".format(self.id)


class SQLAlchemyClearingType(Base):
    """
    classdocs
    """

    __tablename__ = "company_clearing_type"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyClearingType(id='{}')>".format(self.id)


class SQLAlchemyCompany(Base):
    """
    classdocs
    """

    __tablename__ = "company_company"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyCompany(id='{}')>".format(self.id)


class SQLAlchemyEmployee(Base):
    """
    classdocs
    """

    __tablename__ = "company_employee"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyEmployee(id='{}')>".format(self.id)


class SQLAlchemyEmployment(Base):
    """
    classdocs
    """

    __tablename__ = "company_employment"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyEmployment(id='{}')>".format(self.id)


class SQLAlchemySoftwareVendor(Base):
    """
    classdocs
    """

    __tablename__ = "company_software_vendor"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemySoftwareVendor(id='{}')>".format(self.id)


class SQLAlchemyDataVendor(Base):
    """
    classdocs
    """

    __tablename__ = "company_data_vendor"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyDataVendor(id='{}')>".format(self.id)


class SQLAlchemyExchangeMembership(Base):
    """
    classdocs
    """

    __tablename__ = "company_exchange_membership"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyExchangeMembership(id='{}')>".format(self.id)


class SQLAlchemyCompanyClearingBank(Base):
    """
    classdocs
    """

    __tablename__ = "company_clearing_bank"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyCompanyClearingBank(id='{}')>".format(self.id)


class SQLAlchemyCompanyBank(Base):
    """
    classdocs
    """

    __tablename__ = "company_bank"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyCompanyBank(id='{}')>".format(self.id)


class SQLAlchemyRegulatoryMembership(Base):
    """
    classdocs
    """

    __tablename__ = "company_regulatory_membership"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyRegulatoryMembership(id='{}')>".format(self.id)


class SQLAlchemyCompanySoftwareVendor(Base):
    """
    classdocs
    """

    __tablename__ = "company_company_software_vendor"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyCompanySoftwareVendor(id='{}')>".format(self.id)


class SQLAlchemyCompanyDataVendor(Base):
    """
    classdocs
    """

    __tablename__ = "company_company_data_vendor"

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<SQLAlchemyCompanyDataVendor(id='{}')>".format(self.id)
