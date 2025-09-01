from datetime import datetime, timedelta
from typing import Optional

from edri.dataclass.event import Event, event
from edri.dataclass.response import Response, response


@response
class SetResponse(Response):
    identifier: str


@event
class Set(Event):
    event: Event
    when: datetime
    repeat: Optional[timedelta] = None
    identifier: Optional[str] = None
    response: SetResponse
