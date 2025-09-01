from datetime import datetime
from multiprocessing.connection import Connection
from typing import Type, Optional

from edri.dataclass.event import Event, event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Router


@response
class SubscribeResponse(Response):
    pass


@event
class Subscribe(Router):
    event_type: Type[Event]
    name: str
    pipe: Optional[Connection]
    request: bool
    from_time: datetime
    response: SubscribeResponse