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


class EnvironmentManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(EnvironmentManager, self).__init__()

    def __repr__(self) -> str:
        return "<EnvironmentManager(id='{}')>".format(self.id)


class EnvironmentAsyncManager(AsyncManager):
    """
    classdocs
    """
    
    def __init__(self) -> None:
        """
        Constructor
        """
        super(EnvironmentAsyncManager, self).__init__()

    def __repr__(self) -> str:
        return "<EnvironmentAsyncManager(id='{}')>".format(self.id)


class EnvironmentService(Service):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(EnvironmentService, self).__init__()

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<EnvironmentService(id='{}')>".format(self.id)


class EnvironmentAsyncService(AsyncService):
    pass
