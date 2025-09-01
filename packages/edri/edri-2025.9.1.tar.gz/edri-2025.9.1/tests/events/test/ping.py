from edri.dataclass.event import event
from edri.events.edri.group import Test


@event
class Ping(Test):
    pass
