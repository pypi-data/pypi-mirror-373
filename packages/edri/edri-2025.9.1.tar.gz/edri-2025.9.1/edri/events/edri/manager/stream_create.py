from edri.dataclass.event import Event, event
from edri.events.edri.group import Manager


@event
class StreamCreate(Manager):
    event: Event
