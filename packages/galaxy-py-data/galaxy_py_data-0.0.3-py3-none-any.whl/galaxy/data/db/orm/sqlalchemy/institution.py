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


class SQLAlchemyBank(Base):
    """
    classdocs
    """

    __tablename__ = "institution_bank"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyBank(id='{}')>".format(self.id)


class SQLAlchemyBrokerGroup(Base):
    """
    classdocs
    """

    __tablename__ = "institution_broker_group"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyBrokerGroup(id='{}')>".format(self.id)


class SQLAlchemyBroker(Base):
    """
    classdocs
    """

    __tablename__ = "institution_broker"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyBroker(id='{}')>".format(self.id)


class SQLAlchemyRegulatoryAuthority(Base):
    """
    classdocs
    """

    __tablename__ = "institution_regulatory_authority"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyRegulatoryAuthority(id='{}')>".format(self.id)


class SQLAlchemyCentralBank(Base):
    """
    classdocs
    """

    __tablename__ = "institution_central_bank"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyCentralBank(id='{}')>".format(self.id)


class SQLAlchemyCentralSecuritiesDepository(Base):
    """
    classdocs
    """

    __tablename__ = "institution_csd"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyCentralSecuritiesDepository(id='{}')>".format(self.id)


class SQLAlchemySubcustodian(Base):
    """
    classdocs
    """

    __tablename__ = "institution_subcustodian"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemySubcustodian(id='{}')>".format(self.id)
