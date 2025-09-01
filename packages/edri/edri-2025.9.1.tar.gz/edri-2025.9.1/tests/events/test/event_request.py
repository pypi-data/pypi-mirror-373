from typing import Optional

from edri.dataclass.event import event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Test as GroupTest


@response
class EventResponse(Response):
    random: Optional[int]


@event
class EventRequest(GroupTest):
    response: EventResponse
