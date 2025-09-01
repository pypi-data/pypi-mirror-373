from typing import Type

from edri.dataclass.event import Event, event
from edri.dataclass.response import response, Response
from edri.events.edri.group import Router


@response
class UnsubscribeResponse(Response):
    pass


@event
class Unsubscribe(Router):
    name: str
    event_type: Type[Event]
    request: bool
    response: UnsubscribeResponse
