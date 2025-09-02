from typing import Any, Callable

from edri.dataclass.event import event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Store


@response
class GetCallbackResponse(Response):
    value: Any


@event
class GetCallback(Store):
    name: str
    condition: Callable[[Any], bool] | None = None
    response: GetCallbackResponse
