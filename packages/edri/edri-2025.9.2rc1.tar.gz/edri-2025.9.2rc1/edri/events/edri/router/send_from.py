from typing import Optional
from uuid import UUID

from edri.dataclass.event import Event, event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Router


@response
class SendFromResponse(Response):
    event: Event


@event
class SendFrom(Router):
    router_id: UUID
    key: Optional[str] = None
    response: SendFromResponse