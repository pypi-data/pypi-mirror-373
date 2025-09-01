from typing import Any

from edri.dataclass.event import event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Store


@response
class DeleteResponse(Response):
    value: Any


@event
class Delete(Store):
    name: str
    response: DeleteResponse
