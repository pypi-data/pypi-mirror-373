from multiprocessing.connection import Connection
from typing import Optional

from edri.dataclass.event import event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Router
from edri.events.edri.router import Demands


@response
class SubscribedExternalResponse(Response):
    demands: Demands


@event
class SubscribedExternal(Router):
    pipe: Optional[Connection]
    response: SubscribedExternalResponse
