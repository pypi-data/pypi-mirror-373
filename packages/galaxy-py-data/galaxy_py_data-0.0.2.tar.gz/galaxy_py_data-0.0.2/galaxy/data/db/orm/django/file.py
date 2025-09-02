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

from django.db.models.fields import SmallAutoField,             \
                                    CharField,                  \
                                    BooleanField,               \
                                    DateTimeField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE

from galaxy.data.db.djangodb import AuditableModel,             \
                                    UUIDAuditableModel


class FileModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "file"
        abstract = True


class FileUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "file"
        abstract = True


class Extension(FileModel):
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
    extension: CharField = CharField(db_column="extension",
                                     max_length=10,
                                     null=False,
                                     blank=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Extension(id='{}')>".format(self.id)

    class Meta(FileModel.Meta):
        db_table = '"file"."extension"'


class Format(FileModel):
    """
    classdocs
    """

    id: SmallAutoField = SmallAutoField(db_column="id",
                                        null=False,
                                        primary_key=True)
    code: CharField = CharField(db_column="code",
                                max_length=15,
                                null=False,
                                blank=False)
    name: CharField = CharField(db_column="name",
                                max_length=80,
                                null=False,
                                blank=False)
    fullname: CharField = CharField(db_column="name",
                                    max_length=120,
                                    null=False,
                                    blank=False)
    is_proprietary: BooleanField = BooleanField(db_column="is_proprietary",
                                                null=False)
    create_by: CharField = CharField(db_column="create_by",
                                     max_length=150,
                                     null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Format(id='{}')>".format(self.id)

    class Meta(FileModel.Meta):
        db_table = '"file"."format"'


class Location(FileUUIDModel):
    """
    classdocs
    """

    path: CharField = CharField(db_column="path",
                                max_length=250,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Location(id='{}')>".format(self.id)

    class Meta(FileUUIDModel.Meta):
        db_table = '"file"."location"'


class File(FileUUIDModel):
    """
    classdocs
    """

    name: CharField = CharField(db_column="name",
                                max_length=150,
                                null=False,
                                blank=False)
    path: ForeignKey = ForeignKey(Location,
                                  db_column="path_id",
                                  on_delete=CASCADE,
                                  null=False)
    extension: ForeignKey = ForeignKey(Extension,
                                       db_column="extension_id",
                                       on_delete=CASCADE,
                                       null=False)
    format: ForeignKey = ForeignKey(Format,
                                    db_column="format_id",
                                    on_delete=CASCADE,
                                    null=False)
    create_date: DateTimeField = DateTimeField(db_column="create_date",
                                               null=False)
    create_by: CharField = CharField(db_column="create_by",
                                     max_length=50,
                                     null=False,
                                     blank=False)
    last_modif_date: DateTimeField = DateTimeField(db_column="last_modif_date",
                                                   null=False)
    last_modif_by: CharField = CharField(db_column="last_modif_by",
                                         max_length=50,
                                         null=False,
                                         blank=False)
    delete_date: DateTimeField = DateTimeField(db_column="delete_date",
                                               null=True)
    delete_by: CharField = CharField(db_column="delete_by",
                                     max_length=50,
                                     null=True)
    is_readable: BooleanField = BooleanField(db_column="is_readable",
                                             null=False)
    is_writeable: BooleanField = BooleanField(db_column="is_writeable",
                                              null=False)
    is_executable: BooleanField = BooleanField(db_column="is_executable",
                                               null=False)
    posix_permission: CharField = CharField(db_column="posix_permission",
                                            max_length=4,
                                            null=True)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<File(id='{}')>".format(self.id)

    class Meta(FileUUIDModel.Meta):
        db_table = '"file"."file"'


class EventLevel(FileModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=100,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<EventLevel(code='{}')>".format(self.code)

    class Meta(FileModel.Meta):
        db_table = '"file"."event_level"'


class EventGroup(FileModel):
    """
    classdocs
    """

    code: CharField = CharField(db_column="code",
                                max_length=10,
                                null=False,
                                blank=False,
                                primary_key=True)
    name: CharField = CharField(db_column="name",
                                max_length=100,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<EventGroup(code='{}')>".format(self.code)

    class Meta(FileModel.Meta):
        db_table = '"file"."event_group"'


class Action(FileModel):
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
                                max_length=50,
                                null=False,
                                blank=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Action(id='{}')>".format(self.id)

    class Meta(FileUUIDModel.Meta):
        db_table = '"file"."action"'


class Event(FileUUIDModel):
    """
    classdocs
    """

    level: ForeignKey = ForeignKey(EventLevel,
                                   db_column="level_code",
                                   on_delete=CASCADE,
                                   null=False)
    group: ForeignKey = ForeignKey(EventGroup,
                                   db_column="group_code",
                                   on_delete=CASCADE,
                                   null=False)
    action: ForeignKey = ForeignKey(Action,
                                    db_column="action_id",
                                    on_delete=CASCADE,
                                    null=True)
    msg: CharField = CharField(db_column="name",
                               max_length=250,
                               null=False,
                               blank=False)
    source: CharField = CharField(db_column="source",
                                  max_length=80,
                                  null=True)
    create_date: DateTimeField = DateTimeField(db_column="create_date",
                                               null=False)
    create_by: CharField = CharField(db_column="create_by",
                                     max_length=50,
                                     null=False,
                                     blank=False)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<Event(id='{}')>".format(self.id)

    class Meta(FileUUIDModel.Meta):
        db_table = '"file"."event"'
