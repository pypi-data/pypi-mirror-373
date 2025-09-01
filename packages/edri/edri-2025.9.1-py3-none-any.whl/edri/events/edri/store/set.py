from typing import Any

from edri.dataclass.event import event
from edri.events.edri.group import Store


@event
class Set(Store):
    name: str
    value: Any
