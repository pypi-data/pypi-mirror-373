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

from galaxy.data.db.djangodb import AuditableModel,         \
                                    UUIDAuditableModel


class ProgModel(AuditableModel):
    """
    classdocs
    """

    class Meta(AuditableModel.Meta):
        app_label = "prog"
        abstract = True


class ProgUUIDModel(UUIDAuditableModel):
    """
    classdocs
    """

    class Meta(UUIDAuditableModel.Meta):
        app_label = "prog"
        abstract = True
