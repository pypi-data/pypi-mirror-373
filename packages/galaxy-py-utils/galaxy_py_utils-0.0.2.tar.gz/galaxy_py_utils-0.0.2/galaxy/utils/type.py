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

from typing import NewType
from uuid import UUID

Id = NewType("Id", UUID)
CompId = NewType("CompId", Id)


class TypeUtility(object):
    """
    classdocs
    """

    @staticmethod
    def classname(obj):
        cls = type(obj)
        module = cls.__module__
        name = cls.__qualname__
        if module is not None and module != "__builtin__":
            name = "{}.{}".format(module, name)
        return name
