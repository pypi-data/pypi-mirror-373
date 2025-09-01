from typing import Type

from edri.dataclass.event import Event, event
from edri.events.edri.group import Router


@event
class SubscribedNew(Router):
    event: Type[Event]
    request: bool
