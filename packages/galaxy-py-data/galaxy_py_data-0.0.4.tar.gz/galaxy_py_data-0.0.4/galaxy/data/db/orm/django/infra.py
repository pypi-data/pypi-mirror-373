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

from django.db.models.fields import SmallAutoField,                         \
                                    CharField,                              \
                                    IntegerField,                           \
                                    AutoField,                              \
                                    SmallIntegerField,                      \
                                    DateField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE

from galaxy.data.db.djangodb import AuditableModel,                         \
                                    UUIDAuditableModel
from galaxy.data.db.orm.django.company import Employee,                     \
                                              SoftwareVendor
from galaxy.data.db.orm.django.finance import DataProviderSystem


class InfraModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "infra"
        abstract = True


class InfraUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "infra"
        abstract = True


class OSIModelLayer(InfraModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<OSIModelLayer(id='{}')>".format(self.id)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."osi_model_layer"'


class Protocol(InfraModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=20,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    rfc_num: IntegerField = IntegerField(db_column="rfc_num",
                                         null=True)
    layer: ForeignKey = ForeignKey("OSIModelLayer",
                                   db_column="layer_id",
                                   on_delete=CASCADE)
    default_port: IntegerField = IntegerField(db_column="default_port",
                                              null=True)

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return "<Protocol(code='{}')>".format(self.code)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."protocol"'


class Environment(InfraModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=3,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return "<Environment(code='{}')>".format(self.code)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."environment"'


class HashingAlgorithm(InfraModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=20,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=80)

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return "<Environment(code='{}')>".format(self.code)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."hashing_algorithm"'


class DataProviderServer(InfraUUIDModel):
    """
    classdocs
    """

    host: CharField = CharField(db_column="host",
                                max_length=50)
    port: IntegerField = IntegerField(db_column="port")
    env: ForeignKey = ForeignKey("Environment",
                                 db_column="env_id",
                                 on_delete=CASCADE)
    protocol: ForeignKey = ForeignKey("Protocol",
                                      db_column="protocol_code",
                                      on_delete=CASCADE)
    system: ForeignKey = ForeignKey(DataProviderSystem,
                                    db_column="sys_id",
                                    on_delete=CASCADE)
    start_date: DateField = DateField(db_colunn="start_date")
    end_date: DateField = DateField(db_colunn="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<DataProviderServer(id='{}')>".format(self.id)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."data_provider_server"'


class DataProviderCredential(InfraModel):
    """
    classdocs
    """

    id: AutoField = AutoField(db_column="id",
                              primary_key=True)
    username: CharField = CharField(db_column="username",
                                    max_length=50,
                                    null=True)
    password: CharField = CharField(db_column="password",
                                    max_length=50,
                                    null=True)
    public_key_file: CharField = CharField(db_column="public_key_file",
                                           max_length=250,
                                           null=True)
    private_key_file: CharField = CharField(db_column="private_key_file",
                                            max_length=250,
                                            null=True)
    passphrase: CharField = CharField(db_column="passphrase",
                                      max_length=50,
                                      null=True)
    fingerprint: CharField = CharField(db_column="fingerprint",
                                       max_length=50,
                                       null=True)
    rsa_key_len: SmallIntegerField = SmallIntegerField(db_column="rsa_key_len",
                                                       null=True)
    server: ForeignKey = ForeignKey("DataProviderServer",
                                    db_column="server_id",
                                    on_delete=CASCADE)
    start_date: DateField = DateField(db_colunn="start_date")
    end_date: DateField = DateField(db_colunn="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<DataProviderCredential(id='{}')>".format(self.id)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."data_provider_credential"'


class Domain(InfraModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=250)
    netbios: CharField = CharField(db_column="netbios",
                                   max_length=20)
    start_date: DateField = DateField(db_colunn="start_date")
    end_date: DateField = DateField(db_colunn="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Domain(id='{}')>".format(self.id)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."domain"'


class DomainUser(InfraModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    username: CharField = CharField(db_column="name",
                                    max_length=50)
    domain: ForeignKey = ForeignKey("Domain",
                                    db_column="domain_id",
                                    on_delete=CASCADE)
    email: CharField = CharField(db_column="email",
                                 max_length=250)
    employee: ForeignKey = ForeignKey(Employee,
                                      db_column="employee_id",
                                      on_delete=CASCADE)
    start_date: DateField = DateField(db_colunn="start_date")
    end_date: DateField = DateField(db_colunn="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<DomainUser(id='{}')>".format(self.id)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."domain_user"'


class TradingPlatform(InfraModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=10)
    name: CharField = CharField(db_column="name",
                                max_length=80)
    vendor: ForeignKey = ForeignKey(SoftwareVendor,
                                    db_column="vendor_id",
                                    on_delete=CASCADE,
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<TradingPlatform(id='{}')>".format(self.id)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."trading_platform"'


class TradingServer(InfraUUIDModel):
    """
    classdocs
    """

    host: CharField = CharField(db_column="host",
                                max_length=50)
    domain: ForeignKey = ForeignKey("Domain",
                                    db_column="domain_id",
                                    on_delete=CASCADE)
    env: ForeignKey = ForeignKey("Environment",
                                 db_column="env_id",
                                 on_delete=CASCADE)
    platform: ForeignKey = ForeignKey("TradingPlatform",
                                      db_column="platform_id",
                                      on_delete=CASCADE)
    start_date: DateField = DateField(db_colunn="start_date")
    end_date: DateField = DateField(db_colunn="end_date",
                                    null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<TradingServer(id='{}')>".format(self.id)

    class Meta(InfraModel.Meta):
        db_table = '"infra"."trading_server"'
