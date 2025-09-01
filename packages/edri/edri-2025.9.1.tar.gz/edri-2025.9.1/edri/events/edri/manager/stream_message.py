from edri.dataclass.event import Event, event
from edri.events.edri.group import Manager


@event
class StreamMessage(Manager):
    event: Event
