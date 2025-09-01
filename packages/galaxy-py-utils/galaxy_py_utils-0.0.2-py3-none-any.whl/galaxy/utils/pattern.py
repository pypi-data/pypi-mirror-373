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

from typing import Any
from abc import ABC,                        \
                abstractmethod


class Singleton(object):
    """
    classdocs
    """

    def __new__(cls, *args, **kwargs):
        it_id = "__it__"
        # getattr will dip into base classes, so __dict__ must be used
        it = cls.__dict__.get(it_id, None)
        if it is not None:
            return it
        it = object.__new__(cls)
        setattr(cls, it_id, it)
        it.init(*args, **kwargs)
        return it

    def init(self, *args, **kwargs):
        pass


class Visitor(ABC):
    """
    classdocs
    """

    @abstractmethod
    def visit(self) -> None:
        raise NotImplementedError("Should implement visit()")


class Builder(ABC):
    """
    classdocs
    """

    @abstractmethod
    def build(self) -> Any:
        raise NotImplementedError("Should implement build()")
