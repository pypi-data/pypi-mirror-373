from edri.dataclass.event import event
from edri.events.api.group import Manage


@event
class UnregisterAll(Manage):
    pass
