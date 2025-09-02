from edri.dataclass.event import event
from edri.events.edri.group import Scheduler


@event
class Cancel(Scheduler):
    identifier: str
