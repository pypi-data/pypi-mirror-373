from json import loads, JSONDecodeError, dumps
from typing import Callable, Type, Unpack, TypedDict, NotRequired

from edri.api import Headers
from edri.api.dataclass.api_event import api_events
from edri.api.handlers import BaseHandler
from edri.api.handlers.base_handler import BaseDirectiveHandlerDict
from edri.config.constant import ApiType
from edri.dataclass.directive import ResponseDirective, WebSocketResponseDirective
from edri.dataclass.directive.base import InternalServerErrorResponseDirective, UnauthorizedResponseDirective
from edri.dataclass.event import Event
from edri.dataclass.response import ResponseStatus
from edri.utility import NormalizedDefaultDict
from edri.utility.function import camel2snake


class ResponseKW(TypedDict):
    headers: NormalizedDefaultDict[str, Headers]

class WebSocketDirectiveHandlerDict[T](BaseDirectiveHandlerDict):
    routine: NotRequired[
        Callable[[T, dict[str, Headers]], NormalizedDefaultDict[str, Headers]] | Callable[[T], NormalizedDefaultDict[str, Headers]]]
    error: NotRequired[bool]


class WebsocketHandler(BaseHandler):
    _events = None
    _commands = None

    _directive_handlers: dict[Type[WebSocketResponseDirective], WebSocketDirectiveHandlerDict[WebSocketResponseDirective]] = {
        InternalServerErrorResponseDirective: {
            "error": True,
        },
        UnauthorizedResponseDirective: {
            "error": True,
        },
    }

    def handle_directives(self, directives: list[ResponseDirective]) -> bool:
        error = False
        for directive in directives:
            try:
                directive_handler = self.directive_handlers()[directive.__class__]
            except KeyError as e:
                self.logger.warning("Unknown directive: %s", directive, exc_info=e)
            else:
                if "error" in directive_handler:
                    error = directive_handler["error"]

        return error

    def __init__(self, scope: dict, receive: Callable, send: Callable, headers: NormalizedDefaultDict[str, Headers]):
        super().__init__(scope, receive, send)
        self.command: str | None = None
        self.headers = headers

    @classmethod
    def events(cls) -> dict[str, Type[Event]]:
        if cls._events is None:
            cls._events, cls._commands = cls.sort_events()
        return cls._events

    @classmethod
    def commands(cls) -> dict[Type[Event], str]:
        if cls._commands is None:
            cls._events, cls._commands = cls.sort_events()
        return cls._commands

    @staticmethod
    def sort_events() -> tuple[dict[str, Type[Event]], dict[Type[Event], str]]:
        resources = {}
        for event in api_events:
            if ApiType.WS in event.exclude:
                continue
            if event.resource in resources:
                raise KeyError(f"Duplicate key found: {event.resource}")
            resources[event.resource] = event.event

        return resources, {event.event: event.resource for event in api_events if ApiType.WS not in event.exclude}

    @classmethod
    def api_type(cls) -> ApiType:
        return ApiType.WS

    @classmethod
    def directive_handlers(cls) -> dict[Type[ResponseDirective], WebSocketDirectiveHandlerDict]:
        handlers = {}
        for class_obj in reversed(cls.mro()):
            if hasattr(class_obj, "_directive_handlers"):
                # noinspection PyProtectedMember
                handlers.update(class_obj._directive_handlers)
        return handlers

    async def accept_client(self) -> bool:
        data = await self.receive()
        if "type" in data and data["type"] == "websocket.connect":
            await self.send({"type": "websocket.accept"})
            return True
        else:
            return False

    async def parse_body(self, data) -> bool:
        if data["type"] == "websocket.receive":
            if data["text"] is not None:
                received_data = data["text"]
            else:
                received_data = data["bytes"].decode("utf-8", errors="replace")
        elif data["type"] == "websocket.disconnect":
            return False
        else:
            self.logger.error("Parse body failed")
            await self.response_error(1003, None,{
                "status": ResponseStatus.FAILED.name,
                "reasons": ["Parse body failed"]
            })
            return False
        try:
            self.parameters.update({camel2snake(key): value for key, value in loads(received_data).items()})
        except JSONDecodeError as e:
            self.logger.warning("Cannot process json data", exc_info=e)
            await self.response_error(1003, None, {
                "status": ResponseStatus.FAILED.name,
                "reasons": ["Cannot process json data"]
            })
            return False
        except Exception as e:
            self.logger.error("Unknown error", exc_info=e)
            await self.response_error(1002, None, {
                "status": ResponseStatus.FAILED.name,
                "reasons": ["Unknown error"]
            })
            return False
        return True

    async def get_event_constructor(self) -> Type[Event] | None:
        self.command = self.parameters.pop("command", None)
        if self.command is None:
            raise ResourceWarning("Missing command")
        return self.events().get(self.command, None)

    async def response(self, status, data, *args, **kwargs: Unpack[ResponseKW]) -> None:
        event = {
            "command": self.commands()[data.__class__],
        }
        event.update(data.as_dict(transform=True, keep_concealed=False))
        response = data.get_response()
        if response:
            event["response"] = response.as_dict(transform=True, keep_concealed=False)
        else:
            event.pop("response")
        await self.send({"type": "websocket.send", "text": dumps(event)})

    async def response_error(self, status: int | None, event: Event | None, data: dict | None = None, *args, **kwargs) -> None:
        if event:
            data = self.response_error_prepare(event, data)
        if status:
            await self.send({"type": "websocket.close", "code": status, "reason": dumps(data)})
        elif isinstance(data, dict):
            await self.send({"type": "websocket.send", "text": dumps(data)})

    def response_error_prepare(self, event: Event, data: dict | None) -> dict:
        event_data = event.as_dict(transform=True, keep_concealed=False)
        response = event.get_response()
        event_data["response"]["reasons"] = []
        for directive in response.get_directives():
            handler: WebSocketDirectiveHandlerDict | None = self.directive_handlers().get(directive.__class__, None)
            if not handler:
                continue
            if handler.get("error", False):
                message = getattr(directive, "message", None)
                if message:
                    event_data["response"]["reasons"].append(message)
        if isinstance(data, dict):
            event_data["response"] = data
        return event_data

    async def clear(self):
        self.headers = {}
        self.parameters = self.parse_url_parameters()
        self.command = None
