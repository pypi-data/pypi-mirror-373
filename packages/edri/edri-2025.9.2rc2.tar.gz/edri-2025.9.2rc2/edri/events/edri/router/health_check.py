from http import HTTPMethod

from edri.api.dataclass.api_event import api
from edri.dataclass.event import event, Event
from edri.dataclass.response import Response, response
from edri.events.edri.group import Router
from edri.dataclass.health_checker import Status, Record


@response
class HealthCheckResponse(Response):
    name: str
    status: Status
    exceptions: list[tuple[str, dict, Exception, str]]


@event
class HealthCheck(Router):
    response: HealthCheckResponse


@response
class EdriHealthResponse(Response):
    statuses: list[Record]


@api(url="/edri/health-check-status", resource="health-check-status", template="health_check_status.j2")
class EdriHealth(Router):
    method: HTTPMethod = HTTPMethod.GET
    response: EdriHealthResponse
