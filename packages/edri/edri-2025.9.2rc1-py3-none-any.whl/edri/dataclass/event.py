from dataclasses import _process_class, dataclass, field, replace, asdict, fields, MISSING
from datetime import datetime
from enum import IntFlag, auto
from http import HTTPMethod
from random import choices
from string import ascii_letters, digits
from typing import Optional, Any, Type
from uuid import UUID
from zlib import adler32

from edri.api.dataclass import File, Header, Cookie, Scope
from edri.config.constant import ApiType
from edri.config.setting import SWITCH_KEY_LENGTH
from edri.dataclass.response import Response, ResponseStatus
from edri.utility.function import snake2camel


@dataclass
class ApiInfo:
    _key: str
    type: ApiType = field(compare=False)

    @property
    def key(self) -> str:
        return self._key


@dataclass
class SwitchInfo:
    router_id: Optional[UUID] = None
    key: str = field(default_factory=lambda: "".join(choices(ascii_letters + digits, k=SWITCH_KEY_LENGTH)))
    received: bool = False


@dataclass
class TimingEvent:
    name: str
    description: str | None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Timing:
    events: list[TimingEvent] = field(default_factory=list)

    def stamp(self, name: str, description: str | None = None) -> None:
        self.events.append(TimingEvent(name=name, description=description))


@dataclass
class Event:
    _api: Optional[ApiInfo] = field(init=False, default=None)
    _stream: Optional[str] = field(init=False, default=None)
    _switch: Optional[SwitchInfo] = field(init=False, default=None)
    _worker: str | None = field(init=False, default=None)
    _timing: Timing = field(init=False, default_factory=Timing, compare=False)
    _is_file_only: str | None = field(default=None, init=False)
    response: Optional[Response] = field(init=False, default=None)
    method: Optional[HTTPMethod] = field(init=False, default=None)

    def get_response(self) -> Optional[Response]:
        if self.response and self.response.get_status() != ResponseStatus.NONE:
            return self.response
        return None

    def has_response(self) -> bool:
        return self.response is not None and self.response.get_status() != ResponseStatus.NONE

    def set_response(self, response: Response) -> None:
        self._switch = None
        self.response = response

    def remove_response(self) -> None:
        self._switch = None
        self.response = None

    def get_context(self) -> dict[str, Any]:
        """
        Retrieve a dictionary of all keyword-only fields from the dataclass.

        This method inspects the dataclass and extracts all fields that are
        marked as `kw_only=True`, returning their names and current values.

        Returns:
            dict[str, Any]: A dictionary where the keys are the names of keyword-only
                            fields and the values are their corresponding values
                            in the dataclass instance.
        """
        return {
            f.name: getattr(self, f.name) for f in fields(self)
            if f.kw_only  # Check if the field is keyword-only
        }

    @classmethod
    def hash_name(cls) -> int:
        return adler32(f"{cls.__module__}.{cls.__qualname__}".encode())

    def copy_sender(self, event: "Event") -> None:
        if event._api:
            self._api = replace(event._api)

    def as_dict(self, /, *, transform: bool, keep_concealed: bool) -> dict[str, Any]:
        self._directives = []
        response = self.response
        event = asdict(self)
        event.pop("method", None)
        event.pop("response", None)

        if transform:
            event = {snake2camel(key, exceptions=("_", "id_")): value for key, value in event.items() if
                     keep_concealed or not key.startswith("_")}
        else:
            event = {key: value for key, value in event.items() if keep_concealed or not key.startswith("_")}

        if response:
            event["response"] = response.as_dict(transform=transform, keep_concealed=keep_concealed)
        return event


class EventHandlingType(IntFlag):
    """
    IntFlag representing different modes of event handling in the system.

    The `EventHandlingType` IntFlag categorizes the ways in which events are handled
    and dispatched to clients in the API broker system. Each mode defines a distinct
    strategy for event delivery, ensuring that events reach their intended recipients
    based on the specified criteria. With IntFlag, multiple modes can be combined
    using bitwise operations.

    Attributes:
        SPECIFIC (int): Handles an event in a 1:1 fashion, responding directly to the
        client that requested it. This mode ensures that the event is sent only to
        the client whose request triggered the event. Events in this mode are created
        exclusively by API handlers to fulfill specific client requests.

            Example APIs: Typically used for REST or HTML requests where a client
            makes a direct request, and the server provides a direct response.

        SUBSCRIBED (int): Sends the event exclusively to clients who have registered
        their interest by subscribing to this event type. This mode is used for
        events meant to notify or update only a specific subset of clients.

            Example APIs: Suitable for APIs with asynchronous capabilities, such as
            WebSocket or MQTT, where clients subscribe to events and receive
            notifications asynchronously.

        ALL (int): Broadcasts the event to all clients connected to the system capable
        of receiving asynchronous events, regardless of their specific subscription status.
        This mode does not limit the broadcast to only those who subscribed to a specific type.

            Example APIs: Similar to `SUBSCRIBED`, this mode applies to protocols like
            WebSocket or MQTT, but the event is sent to all clients, not just those
            subscribed to a specific type.

    Combinations:
        SPECIFIC|SUBSCRIBED (int): A flexible mode of event handling where the event can either
        be a direct 1:1 response to a client's request or be broadcasted to all clients
        subscribed to that event type. The handling behavior is determined by the context
        in which the event is created. If the event originates from a REST request or similar,
        it might behave like a SPECIFIC event. If generated internally as part of core logic,
        it might be broadcast to subscribers.

            Example APIs: Can be used for REST or HTML requests but also applies to
            asynchronous protocols like WebSocket or MQTT where clients can subscribe
            to specific events.

        SPECIFIC|ALL (int): Similar to `SPECIFIC|SUBSCRIBED`, but with a broader scope.
        The event can either be sent as a direct response to the specific client that
        requested it or broadcasted to all clients capable of receiving events,
        regardless of their subscription status. The handling behavior is determined
        by the event's context — it is either specific or for all, but it cannot be both
        at the same time.

            Example APIs: Applies to REST, HTML, WebSocket, or MQTT. The event could either
            act like a direct response to a client request or be broadcast to every client,
            but not both simultaneously.
    """

    SPECIFIC = auto()
    SUBSCRIBED = auto()
    ALL = auto()


events: list[Type[Event]] = list()
shareable_events: list[Type[Event]] = list()

ignored_defaults = (Header, Cookie, Scope)
ignored_fields = ("response", "method")


def _event(cls, init, repr, eq, order, unsafe_hash, frozen, match_args, kw_only, slots, weakref_slot, shareable):
    event_response = cls.__annotations__.get("response", False)
    if event_response:
        if not issubclass(event_response, Response):
            raise AttributeError("Event response must be a subclass of Response")
        attribute = getattr(cls, "response", False)
        if attribute:
            attribute.init = False
            attribute.default_factory = event_response
        else:
            setattr(cls, "response", field(init=False, default_factory=event_response))
    dataclass = _process_class(cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen,
                               match_args=match_args, kw_only=kw_only, slots=slots, weakref_slot=weakref_slot)

    valid_fields = []
    for f in fields(dataclass):
        if f.name.startswith('_') or f.name in ignored_fields:
            continue

        if f.kw_only:
            continue

        # Ignore fields with default or default_factory of Header, Cookie, Scope
        default = f.default
        default_factory = f.default_factory if f.default_factory is not MISSING else None

        if isinstance(default, ignored_defaults) or isinstance(default_factory, ignored_defaults):
            continue

        valid_fields.append(f)

    if len(valid_fields) == 1:
        sole_field = valid_fields[0]
        if cls.__annotations__.get(sole_field.name) == File:
            dataclass._is_file_only = sole_field.name

    if shareable:
        shareable_events.append(dataclass)
    return dataclass


def event(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False,
          match_args=True, kw_only=False, slots=False, weakref_slot=False, shareable=False):
    def wrapper(cls):
        return _event(cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen, match_args=match_args,
                      kw_only=kw_only, slots=slots, weakref_slot=weakref_slot, shareable=shareable)

    if cls is None:
        return wrapper

    return wrapper(cls)


__all__ = [Event, event, EventHandlingType, events, shareable_events, SwitchInfo]
