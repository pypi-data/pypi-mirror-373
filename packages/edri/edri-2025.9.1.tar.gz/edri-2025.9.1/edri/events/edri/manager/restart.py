from typing import Type

from edri.dataclass.event import event
from edri.events.edri.group import Manager


@event
class Restart(Manager):
    manager: Type[Manager]
