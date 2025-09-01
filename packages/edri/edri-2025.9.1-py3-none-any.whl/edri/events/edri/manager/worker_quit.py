from edri.dataclass.event import event
from edri.events.edri.group import Manager


@event
class WorkerQuit(Manager):
    pass
