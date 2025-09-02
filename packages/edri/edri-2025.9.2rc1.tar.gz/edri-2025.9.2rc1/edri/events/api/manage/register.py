from typing import Any

from edri.api.dataclass.api_event import api
from edri.config.constant import ApiType
from edri.dataclass.response import Response, response
from edri.events.api.group import Manage


@response
class RegisterResponse(Response):
    pass


@api(resource="register", exclude=[ApiType.REST, ApiType.HTML])
class EdriRegister(Manage):
    event: str
    param_set: dict[str, Any]
    response: RegisterResponse
