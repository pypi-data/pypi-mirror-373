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

from abc import ABC
from transitions import State,                                  \
                        EventData
from datetime import datetime
from transitions.extensions.asyncio import AsyncState
from typing import Any

from galaxy.utils.type import CompId


class Component(ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.id: CompId | None = None
        self.name: str | None = None
        self.desc: str | None = None

    def __str__(self) -> str:
        return "\"{}\" (id: {})".format(self.name, self.id)

    def __repr__(self) -> str:
        return "<Component(id='{}')>".format(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Component):
            return self.id == other.id
        return False

    def __ne__(self, other: object) -> bool:
        if isinstance(other, Component):
            return self.id != other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def visit(self, visitor) -> None:
        visitor.visit(self)


class Configurable(ABC):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self.new_conf: dict[str, Any] | None = None
        self.conf: dict[str, Any] | None = None
        self.old_conf: dict[str, Any] | None = None

    def _load(self) -> None:
        if self.new_conf is not None:
            if self.conf is not None:
                self.old_conf = dict(self.conf)
            self.conf = dict(self.new_conf)
            self.new_conf = None

    def _unload(self) -> None:
        if self.old_conf is not None:
            self.conf = dict(self.old_conf)
            self.old_conf = None


class TimestampedState(State):
    """
    classdocs
    """

    def __init__(self, name: str) -> None:
        """
        Constructor
        """
        super(TimestampedState, self).__init__(name=name)
        self.start_date: datetime | None = None
        self.end_date: datetime | None = None

    def enter(self, event_data: EventData) -> None:
        self.start_date = datetime.now
        self.end_date = None
        super(TimestampedState, self).enter(event_data)

    def exit(self, event_data: EventData) -> None:
        super(TimestampedState, self).enter(event_data)
        self.end_date = datetime.now


class TimestampedAsyncState(AsyncState):
    """
    classdocs
    """

    def __init__(self, name: str) -> None:
        """
        Constructor
        """
        super(TimestampedAsyncState, self).__init__(name=name)
        self.start_date: datetime | None = None
        self.end_date: datetime | None = None

    async def enter(self, event_data: EventData) -> None:
        self.start_date = datetime.now
        self.end_date = None
        await super(TimestampedAsyncState, self).enter(event_data)

    async def exit(self, event_data: EventData) -> None:
        await super(TimestampedAsyncState, self).enter(event_data)
        self.end_date = datetime.now
