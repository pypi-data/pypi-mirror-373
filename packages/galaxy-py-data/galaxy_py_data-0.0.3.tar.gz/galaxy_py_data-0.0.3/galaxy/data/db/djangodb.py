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

import getpass
from uuid import uuid4
import socket
from typing import Tuple
from django.db.models.base import Model
from django.db.models.manager import Manager
from django.db.models.fields import Field,              \
                                    CharField,          \
                                    UUIDField,          \
                                    DateTimeField
from django.contrib.admin import ModelAdmin
from django.utils import timezone
from django.utils.translation import gettext
from django.apps import apps
from django.conf import settings

from galaxy.data import constant


class UserField(CharField):
    """
    classdocs
    """

    description = gettext("Custom field for user created")

    def __init__(self, *args, **kwargs) -> None:
        """
        Constructor
        """
        #kwargs.setdefault("blank", True)
        CharField.__init__(self, *args, **kwargs)

    def get_os_username(self) -> str:
        return getpass.getuser()

    def pre_save(self, model_instance: Field, add) -> str:
        """Updates username created on ADD only."""
        value = super(UserField, self).pre_save(model_instance, add)
        if not value and not add:
            # fall back to OS user if not accessing through browser
            # better than nothing ...
            value = self.get_os_username()
            setattr(model_instance, self.attname, value)
            return value
        return value


class UUIDAutoField(UUIDField):
    """
    AutoField for Universally unique identifier.
    """

    def pre_save(self, model_instance, add):
        value = super(UUIDAutoField, self).pre_save(model_instance, add)
        if not value and add:
            value = uuid4()
            setattr(model_instance, self.attname, value)
        else:
            if not value:
                value = uuid4()
                setattr(model_instance, self.attname, value)
        return value


class HostnameField(CharField):
    """
    classdocs
    """

    description = gettext("Custom field for hostname modified")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("blank", True)
        CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        """Updates socket.gethostname() on each save."""
        value = socket.gethostname()
        setattr(model_instance, self.attname, value)
        return value


def update_device_fields(instance: "AuditableModel") -> Tuple[str, str]:
    device_id = getattr(settings, "DEVICE_ID", None)
    try:
        app_config = apps.get_app_config("edc_device")
    except LookupError:
        pass
    else:
        device_id = device_id or app_config.device_id

    if not instance.id:
        device_created = device_id or "00"
    else:
        device_created = instance.device_created
    device_modified = device_id or "00"
    return device_created, device_modified


class AuditableModel(Model):
    """
    Base model class for all models. Adds created and modified'
    values for user, date and hostname (computer).
    """

    get_latest_by: str = "modified"

    meta_create_date: DateTimeField = DateTimeField(db_column="meta_create_date",
                                                    null=False,
                                                    blank=False,
                                                    editable=False)
    meta_create_by: UserField = UserField(db_column="meta_create_by",
                                          max_length=50,
                                          null=False,
                                          blank=False,
                                          editable=False,
                                          verbose_name="create by",
                                          help_text="Updated by admin.save_model")
    meta_update_date: DateTimeField = DateTimeField(db_column="meta_update_date",
                                                    null=True,
                                                    blank=False,
                                                    editable=False)
    meta_update_by: UserField = UserField(db_column="meta_update_by",
                                          max_length=50,
                                          null=True,
                                          blank=False,
                                          editable=False,
                                          verbose_name="user modified",
                                          help_text="Updated by admin.save_model")
    #hostname_created: CharField = CharField(max_length=60,
    #                             blank=True,
    #                             default=socket.gethostname,
    #                             help_text="System field. (modified on create only)")
    #hostname_modified: HostnameField = HostnameField(max_length=50,
    #                                        blank=True,
    #                                        help_text="System field. (modified on every save)")
    #device_created: CharField = CharField(max_length=10, blank=True)
    #device_modified: CharField = CharField(max_length=10, blank=True)
    meta_comment: CharField = CharField(db_column="meta_comment",
                                        max_length=255,
                                        null=True,
                                        blank=True,
                                        editable=False)

    objects = Manager()

    def save(self, *args, **kwargs):
        try:
            # don't allow update_fields to bypass these audit fields
            update_fields = kwargs.get("update_fields", None) + constant.AUDIT_UPDATE_FIELDS
        except TypeError:
            pass
        else:
            kwargs.update({"update_fields": update_fields})
        dte_modified = timezone.now()
        if self.meta_create_date is None:
            self.meta_create_date = dte_modified
            if not self.meta_create_by:
                # fall back to OS user if not accessing through browser
                # better than nothing ...
                self.meta_create_by = getpass.getuser()
            self.meta_update_by = None
            # self.hostname_created = self.hostname_created[:60]
            # self.device_created, self.device_modified = update_device_fields(self)
        else:
            self.meta_update_date = dte_modified
            # fall back to OS user managed by  pre_save() method...

            # self.hostname_updated = self.hostname_modified[:50]
            # self.device_updated, self.device_updated = update_device_fields(self)

        super().save(*args, **kwargs)

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    class Meta:
        get_latest_by = "meta_update_date"
        ordering = ("-meta_update_date", "-meta_create_date")
        abstract = True


class UUIDAuditableModel(AuditableModel):
    """
    Base model class for all models using an UUID and not
    an INT for the primary key.
    """

    id: UUIDAutoField = UUIDAutoField(db_column="id",
                                      blank=False,
                                      editable=False,
                                      help_text="System auto field. UUID primary key.",
                                      primary_key=True)

    class Meta(AuditableModel.Meta):
        abstract = True


class AdminAuditableModel(ModelAdmin):
    """
    classdocs
    """

    def save_model(self, request, obj, form, change) -> None:
        """Update audit fields from request object before save."""
        if not change:
            obj.meta_create_by = request.user.username
            obj.meta_create_date = timezone.now()
        else:
            obj.meta_update_by = request.user.username
            obj.meta_update_date = timezone.now()
        super().save_model(request, obj, form, change)

    def get_list_filter(self, request) -> tuple:
        """Add audit fields to end of list display."""
        list_filter = super().get_list_filter(request)
        list_filter = [f for f in list_filter if f not in constant.AUDIT_FIELDS] + constant.AUDIT_FIELDS
        if list_filter:
            return tuple(list_filter)
        return tuple()

    def get_readonly_fields(self, request, obj = None) -> tuple:
        """Add audit fields to readonly_fields."""
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        readonly_fields = list(readonly_fields) + [f for f in constant.AUDIT_FIELDS if f not in readonly_fields]
        return tuple(readonly_fields)
