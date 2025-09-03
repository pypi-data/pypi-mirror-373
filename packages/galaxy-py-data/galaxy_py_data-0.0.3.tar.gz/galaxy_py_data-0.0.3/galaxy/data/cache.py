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

from galaxy.service.service import Manager,              \
                                   AsyncManager,         \
                                   Service,              \
                                   AsyncService


class CacheManager(Manager):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def __repr__(self):
        return "<CacheManager(id='{}')>".format(self.id)


class CacheAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def __repr__(self):
        return "<CacheAsyncManager(id='{}')>".format(self.id)


class CacheService(Service):
    """
    classdocs
    """

    def __init__(self):
        super(CacheService, self).__init__()

    def _start(self):
        pass

    def _stop(self):
        pass

    def __repr__(self):
        return "<CacheService(id='{}')>".format(self.id)


class CacheAsyncService(AsyncService):
    """
    classdocs
    """

    def __init__(self):
        super(CacheAsyncService, self).__init__()

    async def _start(self):
        pass

    async def _stop(self):
        pass

    def __repr__(self):
        return "<CacheAsyncService(id='{}')>".format(self.id)
