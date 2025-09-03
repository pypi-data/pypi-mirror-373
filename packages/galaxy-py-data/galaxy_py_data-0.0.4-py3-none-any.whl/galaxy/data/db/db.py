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

from os import path,                                                            \
               listdir
import asyncio
from datetime import datetime
from abc import ABC,                                                            \
                abstractmethod
from urllib.parse import quote_plus
from sqlalchemy.engine.base import Connection,                                  \
                                   Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.engine.create import create_engine
from sqlalchemy.ext.asyncio.engine import create_async_engine,                  \
                                   AsyncEngine,                                 \
                                   AsyncConnection
from sqlalchemy.sql.schema import MetaData,                                     \
                                  Table,                                        \
                                  Column
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.expression import text
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import func
from snowflake.sqlalchemy import URL as SnowflakeURL
from transitions.core import Machine,                                           \
                             EventData
from transitions.extensions.asyncio import AsyncMachine
from typing import Any,                                                         \
                   Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from galaxy.data import constant
from galaxy.data.model.model import DataModel,                                  \
                                    AsyncDataModel
from galaxy.utils.base import TimestampedState,                                 \
                              Component,                                        \
                              Configurable,                                     \
                              TimestampedAsyncState
from galaxy.utils.type import CompId
from galaxy.service.service import Manager,                                     \
                                   AsyncManager,                                \
                                   Service,                                     \
                                   AsyncService,                                \
                                   LogService,                                  \
                                   LogAsyncService
from galaxy.service import constant as service_constant


class DAO(Component, ABC):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(DAO, self).__init__()
        self.schema = None

    @abstractmethod
    def get(self, _id: Any | None = None) -> Any | None:
        raise NotImplementedError("Should implement get()")

    @abstractmethod
    def create(self, elts: list) -> None:
        raise NotImplementedError("Should implement create()")

    @abstractmethod
    def update(self, elts: list) -> None:
        raise NotImplementedError("Should implement update()")

    @abstractmethod
    def delete(self, elt: list) -> None:
        raise NotImplementedError("Should implement delete()")


class AsyncDAO(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncDAO, self).__init__()
        self.schema = None

    @abstractmethod
    async def get(self, _id: Any | None) -> Any | None:
        raise NotImplementedError("Should implement get()")

    @abstractmethod
    async def create(self, elts: list) -> None:
        raise NotImplementedError("Should implement create()")

    @abstractmethod
    async def update(self, elts: list) -> None:
        raise NotImplementedError("Should implement update()")

    @abstractmethod
    async def delete(self, elts: list) -> None:
        raise NotImplementedError("Should implement delete()")


class DatabaseModel(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: DBModelStateMachine = DBModelStateMachine(self)
        self.log: LogService | None = None

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement connect()")

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError("Should implement close()")

    @abstractmethod
    def create_ddl(self) -> None:
        raise NotImplementedError("Should implement create_ddl()")

    @abstractmethod
    def create_dml(self) -> None:
        raise NotImplementedError("Should implement create_dml()")

    def __repr__(self) -> str:
        return "<DatabaseModel(id='{}')>".format(self.id)


class DBModelState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelState, self).__init__(name=name)
        self.model: DatabaseModel = model


class DBModelNewState(DBModelState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelNewState, self).__init__(service_constant.STATE_NEW, model)


class DBModelInitiatedState(DBModelState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelInitiatedState, self).__init__(service_constant.STATE_INIT, model)

    def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The database model {} is loading".format(self.model))
        self.model._load()
        self.model.log.logger.debug("The database model {} is loaded".format(self.model))
        super(DBModelInitiatedState, self).enter(event_data)


class DBModelConnectedState(DBModelState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelConnectedState, self).__init__(service_constant.STATE_CONNECTED, model)

    def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The database model {} is connecting".format(self.model))
        self.model._connect()
        self.model.log.logger.debug("The database model {} is connected".format(self.model))
        super(DBModelConnectedState, self).enter(event_data)


class DBModelClosedState(DBModelState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelClosedState, self).__init__(service_constant.STATE_CLOSED, model)

    def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The database model {} is disconnecting".format(self.model))
        self.model._close()
        self.model.log.logger.debug("The database model {} is disconnected".format(self.model))
        super(DBModelClosedState, self).enter(event_data)


class DBModelTimeoutState(DBModelState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelTimeoutState, self).__init__(service_constant.STATE_TIMEOUT, model)


class DBModelStateMachine(object):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        self._model: DatabaseModel = model
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, DBModelState] = {
                                                service_constant.STATE_NEW: DBModelNewState(self._model),
                                                service_constant.STATE_INIT: DBModelInitiatedState(self._model),
                                                service_constant.STATE_CONNECTED: DBModelConnectedState(self._model),
                                                service_constant.STATE_CLOSED: DBModelClosedState(self._model),
                                                service_constant.STATE_TIMEOUT: DBModelTimeoutState(self._model)
                                               }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": service_constant.STATE_NEW,
                                                    "dest": service_constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "connect",
                                                    "source": service_constant.STATE_INIT,
                                                    "dest": service_constant.STATE_CONNECTED
                                                   },
                                                   {
                                                    "trigger": "close",
                                                    "source": service_constant.STATE_CONNECTED,
                                                    "dest": service_constant.STATE_CLOSED
                                                   }]

    def _init_machine(self):
        self.machine: Machine = Machine(model=self._model,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[service_constant.STATE_NEW])


class AsyncDatabaseModel(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: DBModelAsyncStateMachine = DBModelAsyncStateMachine(self)
        self.log: LogAsyncService | None = None

    async def _load(self):
        super(AsyncDatabaseModel, self)._load()

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError("Should implement connect()")

    @abstractmethod
    async def _close(self) -> None:
        raise NotImplementedError("Should implement close()")

    @abstractmethod
    async def create_ddl(self) -> None:
        raise NotImplementedError("Should implement create_ddl()")

    @abstractmethod
    async def create_dml(self) -> None:
        raise NotImplementedError("Should implement create_dml()")

    def __repr__(self) -> str:
        return "<DatabaseModel(id='{}')>".format(self.id)


class DBModelAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelAsyncState, self).__init__(name=name)
        self.model: DatabaseModel = model


class DBModelNewAsyncState(DBModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelNewAsyncState, self).__init__(service_constant.STATE_NEW, model)


class DBModelInitiatedAsyncState(DBModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelInitiatedAsyncState, self).__init__(service_constant.STATE_INIT, model)

    async def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The database model {} is loading".format(self.model))
        await self.model._load()
        self.model.log.logger.debug("The database model {} is loaded".format(self.model))
        await super(DBModelInitiatedAsyncState, self).enter(event_data)


class DBModelConnectedAsyncState(DBModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelConnectedAsyncState, self).__init__(service_constant.STATE_CONNECTED, model)

    async def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The database model {} is connecting".format(self.model))
        await self.model._connect()
        self.model.log.logger.debug("The database model {} is connected".format(self.model))
        await super(DBModelConnectedAsyncState, self).enter(event_data)


class DBModelClosedAsyncState(DBModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelClosedAsyncState, self).__init__(service_constant.STATE_CLOSED, model)

    async def enter(self, event_data: EventData) -> None:
        self.model.log.logger.debug("The database model {} is disconnecting".format(self.model))
        await self.model._close()
        self.model.log.logger.debug("The database model {} is disconnected".format(self.model))
        await super(DBModelClosedAsyncState, self).enter(event_data)


class DBModelTimeoutAsyncState(DBModelAsyncState):
    """
    classdocs
    """

    def __init__(self, model: DatabaseModel) -> None:
        """
        Constructor
        """
        super(DBModelTimeoutAsyncState, self).__init__(service_constant.STATE_TIMEOUT, model)


class DBModelAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, model: AsyncDatabaseModel) -> None:
        """
        Constructor
        """
        self._model: AsyncDatabaseModel = model
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, DBModelAsyncState] = {
                                                     service_constant.STATE_NEW: DBModelNewAsyncState(self._model),
                                                     service_constant.STATE_INIT: DBModelInitiatedAsyncState(self._model),
                                                     service_constant.STATE_CONNECTED: DBModelConnectedAsyncState(self._model),
                                                     service_constant.STATE_CLOSED: DBModelClosedAsyncState(self._model),
                                                     service_constant.STATE_TIMEOUT: DBModelTimeoutAsyncState(self._model)
                                                    }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": service_constant.STATE_NEW,
                                                    "dest": service_constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "connect",
                                                    "source": service_constant.STATE_INIT,
                                                    "dest": service_constant.STATE_CONNECTED
                                                   },
                                                   {
                                                    "trigger": "close",
                                                    "source": service_constant.STATE_CONNECTED,
                                                    "dest": service_constant.STATE_CLOSED
                                                   }]

    def _init_machine(self):
        self.machine: AsyncMachine = AsyncMachine(model=self._model,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[service_constant.STATE_NEW])


class SQLAlchemyDBModel(DatabaseModel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SQLAlchemyDBModel, self).__init__()
        self.engine_fact: SQLAlchemyEngineFactory | None = None
        self.engine: Engine | None = None
        self.metadata: MetaData | None = None
        self.dml_dirs: list[str] | None = None
        self.daos: dict[CompId, SQLAlchemyDAO] | None = None
        self.conn: Connection | None = None

    def _load(self) -> None:
        super(SQLAlchemyDBModel, self)._load()
        if self.engine_fact is not None:
            self.engine_fact._load()
        if "schema" in self.conf and len(self.conf["schema"]) > 0:
            for dao in self.daos.values():
                dao.schema = self.conf["schema"]

    def _connect(self) -> None:
        self.engine = self.engine_fact.create()
        self.metadata = MetaData()
        #self.conn = self.engine.connect()
        [dao.init_engine(self.engine, self.metadata) for dao in self.daos.values()]

    def _close(self) -> None:
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    def create_ddl(self) -> None:
        [dao.init_conn(self.conn, self.metadata) for dao in self.daos.values()]
        self.metadata.create_all(bind=self.engine)

    def create_dml(self) -> None:
        if path.exists(path.join("sql", "dml")):
            for dml_dir in self.dml_dirs:
                dmldir = path.join("sql", "dml", dml_dir)
                if path.exists(dmldir) and path.isdir(dmldir):
                    sqlfiles = sorted([f for f in listdir(dmldir) if path.isfile(path.join(dmldir, f))])
                    for sqlfile in sqlfiles:
                        with open(path.join(dmldir, sqlfile), mode="r", encoding="utf-8") as f:
                            sql = f.read()
                            self.engine.execute(text(sql))


class SQLAlchemyEngineFactory(Component, Configurable):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogService | None = None

    def create(self) -> Engine:
        url = self._create_url()
        #[self.log.add_logger(logger) for logger in ["sqlalchemy.engine",
        #                                            "sqlalchemy.pool",
        #                                            "sqlalchemy.dialects",
        #                                            "sqlalchemy.orm"]]
        connect_args = {}
        if "private_key" in self.conf and len(self.conf["private_key"]) > 0:
            connect_args["private_key"] = self._create_snowflake_private_key(self.conf["private_key"])
        return create_engine(url,
                             connect_args=connect_args,
                             pool_size = self.conf["pool_size"],
                             max_overflow=self.conf["max_overflow"],
                             pool_timeout=self.conf["pool_timeout"])

    # Union is mandatory as type hint for return value, otherwise the error "TypeError: unsupported operand type(s) for |: 'type' and 'function'" will appear
    def _create_url(self) -> Union[URL, SnowflakeURL]:
        drivername = self.conf["dialect"]
        if "driver" in self.conf and len(self.conf["driver"]) > 0:
            drivername += "+{}".format(self.conf["driver"])
        host = None
        if "host" in self.conf and len(self.conf["host"]) > 0:
            host = self.conf["host"]
        account = None
        if "account" in self.conf and len(self.conf["account"]) > 0:
            account = self.conf["account"]
        port = self.conf["port"]
        database = self.conf["database"]
        warehouse = None
        if "warehouse" in self.conf and len(self.conf["warehouse"]) > 0:
            warehouse = self.conf["warehouse"]
        username = self.conf["username"]
        password = None
        if "password" in self.conf and len(self.conf["password"]) > 0:
            password = quote_plus(self.conf["password"], safe="!")
        role = None
        if "role" in self.conf and len(self.conf["role"]) > 0:
            role = self.conf["role"]
        query = {}
        if "query" in self.conf:
            query = self.conf["query"]
        if self.conf["dialect"] == constant.DIALECT_SNOWFLAKE:
            args = {}
            args["account"] = account
            args["port"] = port
            args["database"] = database
            if warehouse is not None:
                args["warehouse"] = warehouse
            args["user"] = username
            if password is not None:
                args["password"] = password
            if role is not None:
                args["role"] = role
            return SnowflakeURL(**args)
        return URL.create(drivername=drivername,
                          host=host,
                          port=port,
                          database=database,
                          username=username,
                          password=password,
                          query=query)

    def _create_snowflake_private_key(self, private_key: str) -> str:
        with open(private_key, "rb") as key:
            p_key = serialization.load_pem_private_key(key.read(),
                                                       password=None,
                                                       backend=default_backend())
        return p_key.private_bytes(encoding=serialization.Encoding.DER,
                                   format=serialization.PrivateFormat.PKCS8,
                                   encryption_algorithm=serialization.NoEncryption())


class SQLAlchemyAsyncDBModel(AsyncDatabaseModel):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SQLAlchemyAsyncDBModel, self).__init__()
        self.engine_fact: SQLAlchemyAsyncEngineFactory | None = None
        self.engine: AsyncEngine | None = None
        self.metadata: MetaData | None = None
        self.dml_dirs: list[str] | None = None
        self.daos: dict[CompId, SQLAlchemyAsyncDAO] | None = None
        self.conn: AsyncConnection | None = None

    async def _load(self) -> None:
        await super(SQLAlchemyAsyncDBModel, self)._load()
        if self.engine_fact is not None:
            self.engine_fact._load()
        if "schema" in self.conf and len(self.conf["schema"]) > 0:
            for dao in self.daos.values():
                dao.schema = self.conf["schema"]

    async def _connect(self) -> None:
        self.engine = self.engine_fact.create()
        self.metadata = MetaData()
        #async with self.engine.begin() as conn:
        #    await conn.run_sync(self.metadata.create_all)
        #self.conn = await self.engine.connect()
        [dao.init_engine(self.engine, self.metadata) for dao in self.daos.values()]

        #if "continent" in self.daos:
        #    continent_dao = self.daos["continent"]
        #    continents = await continent_dao.get_continents()
        #    africa = continents["AF"]
        #    africa.name = "Africa"
        #    await continent_dao.update_continent(africa)
        #    continents = await continent_dao.get_continents()

    async def _close(self) -> None:
        if self.conn is not None and not self.conn.closed:
            await self.conn.close()

    async def create_ddl(self) -> None:
        [dao.init_engine(self.engine, self.metadata) for dao in self.daos.values()]
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)

    async def create_dml(self) -> None:
        if path.exists(path.join("sql", "dml")):
            for dml_dir in self.dml_dirs:
                dmldir = path.join("sql", "dml", dml_dir)
                if path.exists(dmldir) and path.isdir(dmldir):
                    sqlfiles = sorted([f for f in listdir(dmldir) if path.isfile(path.join(dmldir, f))])
                    for sqlfile in sqlfiles:
                        with open(path.join(dmldir, sqlfile), mode="r", encoding="utf-8") as f:
                            sql = f.read()
                            await self.conn.execute(text(sql))


class SQLAlchemyAsyncEngineFactory(Component, Configurable):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogAsyncService | None = None

    def create(self) -> AsyncEngine:
        url = self._create_url()
        #[self.log.add_logger(logger) for logger in ["sqlalchemy.engine",
        #                                            "sqlalchemy.pool",
        #                                            "sqlalchemy.dialects",
        #                                            "sqlalchemy.orm"]]
        return create_async_engine(url,
                                   pool_size=self.conf["pool_size"],
                                   max_overflow=self.conf["max_overflow"],
                                   pool_timeout=self.conf["pool_timeout"])

    def _create_url(self) -> URL:
        drivername = self.conf["dialect"]
        if "driver" in self.conf and len(self.conf["driver"]) > 0:
            drivername += "+{}".format(self.conf["driver"])
        host = self.conf["host"]
        port = self.conf["port"]
        database = self.conf["database"]
        username = self.conf["username"]
        password = quote_plus(self.conf["password"], safe="!")
        query = {}
        if "query" in self.conf:
            query = self.conf["query"]
        return URL.create(drivername=drivername,
                          host=host,
                          port=port,
                          database=database,
                          username=username,
                          password=password,
                          query=query)


class SQLAlchemyDAO(ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self._table: Table | None = None
        self._engine: Engine | None = None
        self._metadata: MetaData | None = None
        self.log: LogService | None = None

    def init_engine(self, engine: Engine, metadata: MetaData) -> None:
        self._engine = engine
        self._metadata = metadata
        self._init_table()

    @abstractmethod
    def _init_table(self) -> None:
        raise NotImplementedError("Should implement _init_table()")

    def execute(self, stmt: Any) -> Any:
        with self._engine.begin() as conn:
            try:
                return conn.execute(stmt)
            except Exception as e:
                self.log.logger.exception("An exception occurred : {}".format(str(e)))
                return None

    def get_schema_name(self) -> str | None:
        if self.schema is not None:
            if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                             constant.DIALECT_MYSQL,
                                             constant.DIALECT_MARIADB,
                                             constant.DIALECT_SQLITE]:
                return self.schema.lower()
            elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
                return self.schema.upper()
            elif self._engine.dialect.name == constant.DIALECT_MSSQL:
                return self.schema.capitalize()
        return None

    def get_table_name(self, table_name: str, schema_name: str | None = None) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            if schema_name is not None:
                return "{}.{}".format(schema_name.lower(), table_name.lower())
            return table_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            if schema_name is not None:
                return "{}.{}".format(schema_name.upper(), table_name.upper())
            return table_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            if schema_name is not None:
                return "{}.{}".format(schema_name.capitalize(), "".join(w.capitalize() for w in table_name.split("_")))
            return "".join(w.capitalize() for w in table_name.split("_"))

    def get_column_name(self, column_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return column_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return column_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in column_name.split("_"))

    def get_key_name(self, key_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return key_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return key_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in key_name.split("_"))

    def get_constraint_name(self, con_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return con_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return con_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in con_name.split("_"))

    def get_index_name(self, idx_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return idx_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return idx_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in idx_name.split("_"))

    def get_meta_columns(self) -> list[Column]:
        if self._engine.dialect.name == constant.DIALECT_POSTGRESQL:
            return [
                    Column(constant.AUDIT_CREATE_DATE, TIMESTAMP(timezone=True), nullable=False, default=func.current_timestamp()),
                    Column(constant.AUDIT_CREATE_BY, String(50), nullable=False, default=lambda: self._engine.url.username),
                    Column(constant.AUDIT_UPDATE_DATE, TIMESTAMP(timezone=True), onupdate=func.current_timestamp()),
                    Column(constant.AUDIT_UPDATE_BY, String(50), onupdate=lambda: self._engine.url.username),
                    Column(constant.AUDIT_COMMENT, String(255))
                   ]
        return list()


class SQLAlchemyAsyncDAO(ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self._table: Table | None = None
        self._engine: AsyncEngine | None = None
        self._metadata: MetaData | None= None
        self.log: LogAsyncService | None = None

    def init_engine(self, engine: AsyncEngine, metadata: MetaData) -> None:
        self._engine = engine
        self._metadata = metadata
        self._init_table()

    @abstractmethod
    def _init_table(self) -> None:
        raise NotImplementedError("Should implement _init_table()")

    async def execute(self, stmt: Any) -> Any:
        async with self._engine.begin() as conn:
            try:
                return await conn.execute(stmt)
            except Exception as e:
                self.log.logger.exception("An exception occurred : {}".format(str(e)))
                return None

    def get_schema_name(self) -> str | None:
        if self.schema is not None:
            if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                             constant.DIALECT_MYSQL,
                                             constant.DIALECT_MARIADB,
                                             constant.DIALECT_SQLITE]:
                return self.schema.lower()
            elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
                return self.schema.upper()
            elif self._engine.dialect.name == constant.DIALECT_MSSQL:
                return self.schema.capitalize()
        return None

    def get_table_name(self, table_name: str, schema_name: str | None = None) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            if schema_name is not None:
                return "{}.{}".format(schema_name.lower(), table_name.lower())
            return table_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            if schema_name is not None:
                return "{}.{}".format(schema_name.upper(), table_name.upper())
            return table_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            if schema_name is not None:
                return "{}.{}".format(schema_name.capitalize(), "".join(w.capitalize() for w in table_name.split("_")))
            return "".join(w.capitalize() for w in table_name.split("_"))

    def get_column_name(self, column_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return column_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return column_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in column_name.split("_"))

    def get_key_name(self, key_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return key_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return key_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in key_name.split("_"))

    def get_constraint_name(self, con_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return con_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return con_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in con_name.split("_"))

    def get_index_name(self, idx_name: str) -> str:
        if self._engine.dialect.name in [constant.DIALECT_POSTGRESQL,
                                         constant.DIALECT_MYSQL,
                                         constant.DIALECT_MARIADB,
                                         constant.DIALECT_SQLITE]:
            return idx_name.lower()
        elif self._engine.dialect.name in [constant.DIALECT_ORACLE, constant.DIALECT_SNOWFLAKE]:
            return idx_name.upper()
        elif self._engine.dialect.name == constant.DIALECT_MSSQL:
            return "".join(w.capitalize() for w in idx_name.split("_"))

    def get_meta_columns(self) -> list[Column]:
        if self._engine.dialect.name == constant.DIALECT_POSTGRESQL:
            return [
                    Column(constant.AUDIT_CREATE_DATE, TIMESTAMP(timezone=True), nullable=False, default=datetime.now),
                    Column(constant.AUDIT_CREATE_BY, String(50), nullable=False, default=lambda: self._engine.url.username),
                    Column(constant.AUDIT_UPDATE_DATE, TIMESTAMP(timezone=True), onupdate=datetime.now),
                    Column(constant.AUDIT_UPDATE_BY, String(50), onupdate=lambda: self._engine.url.username),
                    Column(constant.AUDIT_COMMENT, String(255))
                   ]
        return list()


class DatabaseService(Service, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DatabaseService, self).__init__()
        self.models: dict[str, DatabaseModel] = {}
        self.data: dict[str, DataModel] = {}

    def _load(self) -> None:
        super(DatabaseService, self)._load()
        [model.load() for model in self.models.values()]
        [model.connect() for model in self.models.values()]

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        [model.close() for model in self.models.values()]

    def restart(self) -> None:
        self.stop()
        self.start()

    def is_enabled(self) -> bool:
        return self.enabled

    def create_ddl(self) -> None:
        [model.create_ddl() for model in self.models.values()]

    def create_dml(self) -> None:
        [model.create_dml() for model in self.models.values()]

    def __repr__(self) -> str:
        return "<DatabaseService(id='{}')>".format(self.id)


class DBMaintenanceService(DatabaseService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DBMaintenanceService, self).__init__()
        self.models: dict[CompId, DatabaseModel] = {}

    def __repr__(self) -> str:
        return "<DBMaintenanceService(id='{}')>".format(self.id)


class DatabaseAsyncService(AsyncService, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DatabaseAsyncService, self).__init__()
        self.models: dict[str, AsyncDatabaseModel] = {}
        self.data: dict[str, AsyncDataModel] = {}
        self.loop = None

    async def _load(self) -> None:
        await super(DatabaseAsyncService, self)._load()
        await asyncio.gather(*[model.load() for model in self.models.values()])
        await asyncio.gather(*[model.connect() for model in self.models.values()])

    async def _start(self) -> None:
        pass

    async def _stop(self) -> None:
        await asyncio.gather(*[model.close() for model in self.models.values()])

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    async def is_enabled(self) -> bool:
        return self.enabled

    async def create_ddl(self) -> None:
        results = await asyncio.gather(*[model.create_ddl() for model in self.models.values()])

    async def create_dml(self) -> None:
        results = await asyncio.gather(*[model.create_dml() for model in self.models.values()])

    def __repr__(self) -> str:
        return "<DatabaseAsyncService(id='{}')>".format(self.id)


class SnowflakeDBAsyncService(DatabaseAsyncService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SnowflakeDBAsyncService, self).__init__()
        self.models: dict[str, DatabaseModel] = {}
        self.data: dict[str, DataModel] = {}

    async def _load(self) -> None:
        await super(DatabaseAsyncService, self)._load()
        for model in self.models.values():
            model.load()
            model.connect()

    async def _stop(self) -> None:
        [model.close() for model in self.models.values()]

    async def create_ddl(self) -> None:
        [model.create_ddl() for model in self.models.values()]

    async def create_dml(self) -> None:
        [model.create_dml() for model in self.models.values()]

    def __repr__(self) -> str:
        return "<SnowflakeDBAsyncService(id='{}')>".format(self.id)


class DBMaintenanceAsyncService(DatabaseAsyncService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DBMaintenanceAsyncService, self).__init__()
        self.models: dict[CompId, AsyncDatabaseModel] = {}

    def __repr__(self) -> str:
        return "<DBMaintenanceAsyncService(id='{}')>".format(self.id)


class DatabaseManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DatabaseManager, self).__init__()

    def __repr__(self) -> str:
        return "<DatabaseManager(id='{}')>".format(self.id)


class DatabaseAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DatabaseAsyncManager, self).__init__()

    def __repr__(self) -> str:
        return "<DatabaseAsyncManager(id='{}')>".format(self.id)