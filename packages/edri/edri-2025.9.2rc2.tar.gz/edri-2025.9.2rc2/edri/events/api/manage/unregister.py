from typing import Any

from edri.api.dataclass.api_event import api
from edri.config.constant import ApiType
from edri.dataclass.response import Response, response
from edri.events.api.group import Manage


@response
class UnregisterResponse(Response):
    pass


@api(resource="unregister", exclude=[ApiType.REST, ApiType.HTML])
class EdriUnregister(Manage):
    event: str
    param_set: dict[str, Any]
    response: UnregisterResponse
