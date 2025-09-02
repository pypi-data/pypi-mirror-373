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


class SQLAlchemyExerciseStyle(Base):
    """
    classdocs
    """

    __tablename__ = "finance_exercise_style"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyExerciseStyle(id='{}')>".format(self.id)


class SQLAlchemyOptionType(Base):
    """
    classdocs
    """

    __tablename__ = "finance_option_type"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyOptionType(id='{}')>".format(self.id)


class SQLAlchemyExpirationType(Base):
    """
    classdocs
    """

    __tablename__ = "finance_expiration_type"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyExpirationType(id='{}')>".format(self.id)


class SQLAlchemyPayoffType(Base):
    """
    classdocs
    """

    __tablename__ = "finance_payoff_type"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyPayoffType(id='{}')>".format(self.id)


class SQLAlchemyDeliveryType(Base):
    """
    classdocs
    """

    __tablename__ = "finance_delivery_type"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyDeliveryType(id='{}')>".format(self.id)


class SQLAlchemyDeliveryMonth(Base):
    """
    classdocs
    """

    __tablename__ = "finance_delivery_month"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyDeliveryMonth(id='{}')>".format(self.id)


class SQLAlchemyInstrumentClass(Base):
    """
    classdocs
    """

    __tablename__ = "finance_instrument_class"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyInstrumentClass(id='{}')>".format(self.id)


class SQLAlchemyIssuerType(Base):
    """
    classdocs
    """

    __tablename__ = "finance_issuer_type"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyIssuerType(id='{}')>".format(self.id)


class SQLAlchemySTIRColor(Base):
    """
    classdocs
    """

    __tablename__ = "finance_stir_color"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemySTIRColor(id='{}')>".format(self.id)


class SQLAlchemyProductFamily(Base):
    """
    classdocs
    """

    __tablename__ = "finance_product_family"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyProductFamily(id='{}')>".format(self.id)


class SQLAlchemySTIRProductGroup(Base):
    """
    classdocs
    """

    __tablename__ = "finance_stir_product_group"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemySTIRProductGroup(id='{}')>".format(self.id)


class SQLAlchemyProduct(Base):
    """
    classdocs
    """

    __tablename__ = "finance_product"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyProduct(id='{}')>".format(self.id)


class SQLAlchemyProductSerie(Base):
    """
    classdocs
    """

    __tablename__ = "finance_product_serie"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyProductSerie(id='{}')>".format(self.id)


class SQLAlchemyIssuer(Base):
    """
    classdocs
    """

    __tablename__ = "finance_issuer"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyIssuer(id='{}')>".format(self.id)


class SQLAlchemyInstrument(Base):
    """
    classdocs
    """

    __tablename__ = "finance_instrument"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyInstrument(id='{}')>".format(self.id)


class SQLAlchemyStraddle(Base):
    """
    classdocs
    """

    __tablename__ = "finance_straddle"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyStraddle(id='{}')>".format(self.id)


class SQLAlchemStrategyType(Base):
    """
    classdocs
    """

    __tablename__ = "finance_strategy_type"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemStrategyType(id='{}')>".format(self.id)


class SQLAlchemyStrategy(Base):
    """
    classdocs
    """

    __tablename__ = "finance_strategy"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyStrategy(id='{}')>".format(self.id)


class SQLAlchemyStrategyInstrument(Base):
    """
    classdocs
    """

    __tablename__ = "finance_strategy_instrument"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyStrategyInstrument(id='{}')>".format(self.id)


class SQLAlchemyDataProvider(Base):
    """
    classdocs
    """

    __tablename__ = "finance_data_provider"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyDataProvider(id='{}')>".format(self.id)


class SQLAlchemyDataProviderSystem(Base):
    """
    classdocs
    """

    __tablename__ = "finance_data_provider_system"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyDataProviderSystem(id='{}')>".format(self.id)


class SQLAlchemyInstrumentClassMap(Base):
    """
    classdocs
    """

    __tablename__ = "finance_instrument_class_map"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyInstrumentClassMap(id='{}')>".format(self.id)


class SQLAlchemyProductMap(Base):
    """
    classdocs
    """

    __tablename__ = "finance_product_map"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyFinanceProductMap(id='{}')>".format(self.id)


class SQLAlchemyProductSerieMap(Base):
    """
    classdocs
    """

    __tablename__ = "finance_product_serie_map"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyFinanceProductMap(id='{}')>".format(self.id)


class SQLAlchemyInstrumentMap(Base):
    """
    classdocs
    """

    __tablename__ = "finance_instrument_map"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyInstrumentMap(id='{}')>".format(self.id)


class SQLAlchemyStrategyMap(Base):
    """
    classdocs
    """

    __tablename__ = "finance_strategy_map"

    def __str__(self) -> Id:
        return self.Id

    def __repr__(self) -> str:
        return "<SQLAlchemyStrategyMap(id='{}')>".format(self.id)
