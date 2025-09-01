from typing import Type, Optional

from edri.dataclass.event import Event, event
from edri.events.edri.group import Manager


@event
class StreamClose(Manager):
    event: Optional[Type[Event]] = None
