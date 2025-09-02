from typing import Dict
from uuid import UUID

from edri.dataclass.event import event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Router


@response
class ResponseLastEvents(Response):
    last_events: Dict[UUID, str]

@event
class LastEvents(Router):
    router_id: UUID
    response: ResponseLastEvents
