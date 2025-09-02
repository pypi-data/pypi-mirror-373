from datetime import datetime, timedelta
from typing import Optional

from edri.dataclass.event import Event, event
from edri.dataclass.response import Response, response


@event
class SetUpdate(Event):
    event: Event
    when: datetime
    repeat: Optional[timedelta] = None
    identifier: Optional[str] = None
