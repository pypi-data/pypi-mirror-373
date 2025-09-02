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

from galaxy.utils.type import CompId
from galaxy.service.service import Manager,              \
                                   AsyncManager,         \
                                   Service,              \
                                   AsyncService


class PreferenceManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.services: dict[CompId, PreferenceService] = {}

    def __repr__(self) -> str:
        return "<PreferenceManager(id='{}')>".format(self.id)


class PreferenceAyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.services: dict[CompId, PreferenceAsyncService] = {}

    def __repr__(self) -> str:
        return "<PreferenceAyncManager(id='{}')>".format(self.id)


class PreferenceService(Service):
    pass


class PreferenceAsyncService(AsyncService):
    pass
