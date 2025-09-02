from edri.dataclass.event import event
from edri.events.api.group import Client


@event
class Unregister(Client):
    pass
