from datetime import datetime, timedelta
from typing import Optional

from edri.dataclass.event import Event, event
from edri.events.edri.group import Scheduler


@event
class Update(Scheduler):
    identifier: str
    event: Optional[Event] = None
    when: Optional[datetime] = None
    repeat: Optional[timedelta] = None
