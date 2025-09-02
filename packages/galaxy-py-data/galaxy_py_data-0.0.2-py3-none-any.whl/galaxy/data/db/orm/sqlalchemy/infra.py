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


class SQLAlchemyOSIModelLayer(Base):
    """
    classdocs
    """

    __tablename__ = "infra_osi_model_layer"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyOSIModelLayer(id='{}')>".format(self.id)


class SQLAlchemyProtocol(Base):
    """
    classdocs
    """

    __tablename__ = "infra_protocol"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyProtocol(id='{}')>".format(self.id)


class SQLAlchemyEnvironment(Base):
    """
    classdocs
    """

    __tablename__ = "infra_environment"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyEnvironment(id='{}')>".format(self.id)


class SQLAlchemyHashingAlgorithm(Base):
    """
    classdocs
    """

    __tablename__ = "infra_hashing_algorithm"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyHashingAlgorithm(id='{}')>".format(self.id)


class SQLAlchemyDataProviderServer(Base):
    """
    classdocs
    """

    __tablename__ = "infra_data_provider_server"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyDataProviderServer(id='{}')>".format(self.id)


class SQLAlchemyDataProviderCredential(Base):
    """
    classdocs
    """

    __tablename__ = "infra_data_provider_credential"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyDataProviderCredential(id='{}')>".format(self.id)


class SQLAlchemyDomain(Base):
    """
    classdocs
    """

    __tablename__ = "infra_domains"

    def __str__(self) -> Id:
        return str(self.Id)

    def __repr__(self) -> str:
        return "<SQLAlchemyDomain(id='{}')>".format(self.id)


class SQLAlchemyDomainUser(Base):
    """
    classdocs
    """

    __tablename__ = "infra_domains_user"

    def __str__(self) -> Id:
        return str(self.Id)

    def __repr__(self) -> str:
        return "<SQLAlchemyDomainUser(id='{}')>".format(self.id)


class SQLAlchemyTradingPlatform(Base):
    """
    classdocs
    """

    __tablename__ = "infra_trading_platform"

    def __str__(self) -> Id:
        return str(self.Id)

    def __repr__(self) -> str:
        return "<SQLAlchemyTradingPlatform(id='{}')>".format(self.id)


class SQLAlchemyTradingServer(Base):
    """
    classdocs
    """

    __tablename__ = "infra_trading_server"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyTradingServer(id='{}')>".format(self.id)
