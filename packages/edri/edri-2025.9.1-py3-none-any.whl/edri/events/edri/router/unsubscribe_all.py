from edri.dataclass.event import event
from edri.dataclass.response import response, Response
from edri.events.edri.group import Router

@response
class UnsubscribeAllResponse(Response):
    pass


@event
class UnsubscribeAll(Router):
    name: str
    response: UnsubscribeAllResponse
