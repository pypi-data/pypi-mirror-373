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

# Supported Dialects
DIALECT_SQLITE = "sqlite"
DIALECT_MYSQL = "mysql"
DIALECT_MARIADB = "mariadb"
DIALECT_POSTGRESQL = "postgresql"
DIALECT_MSSQL = "mssql"
DIALECT_ORACLE = "oracle"
DIALECT_SNOWFLAKE = "snowflake"

# Auditable Fields
AUDIT_CREATE_DATE = "meta_create_date"
AUDIT_CREATE_BY = "meta_create_by"
AUDIT_CREATE_HOSTNAME = "meta_create_host"
AUDIT_UPDATE_DATE = "meta_update_date"
AUDIT_UPDATE_BY = "meta_update_by"
AUDIT_UPDATE_HOSTNAME = "meta_update_host"
AUDIT_COMMENT = "meta_comment"

AUDIT_UPDATE_FIELDS = [
                       AUDIT_UPDATE_DATE,
                       AUDIT_UPDATE_BY,
                       AUDIT_COMMENT
                      ]

AUDIT_FIELDS = [
                AUDIT_CREATE_DATE,
                AUDIT_CREATE_BY,
                AUDIT_UPDATE_DATE,
                AUDIT_UPDATE_BY,
                AUDIT_COMMENT
               ]

# Database Operation
DB_OPE_CREATE = "create"
DB_OPE_UPDATE = "update"
DB_OPE_DELETE = "delete"
