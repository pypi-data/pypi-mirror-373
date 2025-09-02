from dataclasses import dataclass, fields, MISSING
from enum import Enum
from http import HTTPMethod
from inspect import isclass
from logging import getLogger
from types import NoneType, UnionType
from typing import Type, get_origin, get_args
from uuid import UUID

from typeguard import check_type

from edri.api.dataclass import Cookie, Header, Scope
from edri.api.dataclass.file import File
from edri.api.extensions.url_prefix import PrefixBase
from edri.config.constant import ApiType
from edri.dataclass.event import EventHandlingType, _event, Event
from edri.utility.function import camel2snake


@dataclass
class ApiEvent:
    url: str
    resource: str | None
    method: HTTPMethod | None
    handling: EventHandlingType
    event: Type[Event]
    exclude: list[ApiType]
    cookies: dict[str, str]
    headers: dict[str, str]
    scope: dict[str, str]
    template: str | None


api_events: list[ApiEvent] = list()
allowed_types = (str, int, float, bool, File, UUID)
logger = getLogger(__name__)


def api(cls=None, /, *, init=True, repr=True, eq=True, order=False,
        unsafe_hash=False, frozen=False, match_args=True,
        kw_only=False, slots=False, weakref_slot=None, url=None, resource=None, handling=None, exclude=None, template=None,
        shareable=False, method=None):
    exclude = exclude or set()
    exclude = set(exclude) if isinstance(exclude, list) else exclude

    def wrapper(cls):
        cookies = {}
        headers = {}
        scope = {}
        response_file_only = False

        url_prefix = url if url else f"/{camel2snake(cls.__name__)}"
        resource_prefix = resource if resource else camel2snake(cls.__name__).replace("_", "-")

        is_event_subclass = False
        prefixes = set()
        for base in reversed(cls.__bases__):
            if is_event_subclass or issubclass(base, Event):
                is_event_subclass = True

            if issubclass(base, PrefixBase):
                prefixes.add(base)
                url_prefix = base.url_prefix() + url_prefix
                resource_prefix = base.resource_prefix() + resource_prefix
        if not is_event_subclass:
            cls = type(cls.__name__, (Event, *tuple(base for base in cls.__bases__ if base not in prefixes)), dict(cls.__dict__))
        else:
            cls = type(cls.__name__, tuple(base for base in cls.__bases__ if base not in prefixes), dict(cls.__dict__))
        cls.__annotations__.pop('method', None)
        dataclass = _event(cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                           frozen=frozen, match_args=match_args, kw_only=kw_only, slots=slots,
                           weakref_slot=weakref_slot, shareable=shareable)

        for field in fields(dataclass):
            if field.name.startswith("_"):
                continue
            if field.name == "response" and field.type and field.default_factory != MISSING:
                response_file_only = field.type._is_file_only
                continue
            if field.name == "method":
                continue
            elif isinstance(field.default, Cookie):
                cookies[field.name] = field.default.name
            elif isinstance(field.default, Header):
                item_type = get_origin(field.type)
                if get_origin(field.type) == UnionType:
                    item_args = get_args(field.type)
                    position = 0 if item_args.index(NoneType) == 1 else 1
                    item_type = get_origin(item_args[position])
                if item_type != list:
                    raise TypeError(f"{field.name} has to be type of list if used with Header")
                headers[field.name] = field.default.name
            elif isinstance(field.default, Scope):
                scope[field.name] = field.default.name
            elif field.type not in allowed_types and (isclass(field.type) and not any(issubclass(field.type, t) for t in allowed_types) and not issubclass(field.type, Enum)):
                item_type = get_origin(field.type)
                item_args = get_args(field.type)
                if item_type == UnionType:
                    position = 0 if item_args.index(NoneType) == 1 else 1
                    item_type = item_args[position]
                    if item_type in (list, tuple):
                        item_args = get_args(item_type)
                if item_type in (list, tuple):
                    if len(item_args) > 1:
                        raise TypeError(f"Only one child type is allowed got {len(item_args)}")
                    elif item_args[0] not in allowed_types and not hasattr(item_args[0], "fromisoformat"):
                        raise TypeError(f"{item_args[0]} cannot be used as a type for API event")
                elif item_type not in allowed_types and not hasattr(field.type, "fromisoformat"):
                    raise TypeError(f"{field.type} cannot be used as a type for API event")

        http_method = method or dataclass.method
        if http_method is None:
            if ApiType.REST not in exclude or ApiType.HTML not in exclude:
                exclude.add(ApiType.REST)
                exclude.add(ApiType.HTML)
                logger.debug(f"ApiType.REST and ApiType.HTML was excluded for {dataclass} - method is missing")
        else:
            check_type(http_method, HTTPMethod)

        if template is None and ApiType.HTML not in exclude and not response_file_only:
            exclude.add(ApiType.HTML)
            logger.debug(f"ApiType.HTML was excluded for {dataclass} - template is missing")

        api_events.append(ApiEvent(
            url_prefix,
            resource_prefix,
            http_method,
            handling if handling else EventHandlingType.SPECIFIC,
            dataclass,
            exclude,
            cookies,
            headers,
            scope,
            template))

        return dataclass

    if cls is None:
        return wrapper

    return wrapper(cls)
