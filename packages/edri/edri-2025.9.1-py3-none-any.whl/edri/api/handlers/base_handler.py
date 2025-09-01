from abc import ABC, abstractmethod
from dataclasses import fields, MISSING
from logging import getLogger
from types import UnionType, NoneType
from typing import Callable, Type, get_origin, Union, get_args, Any, TypedDict, Literal
from urllib.parse import parse_qs, unquote

from edri.dataclass.directive import ResponseDirective
from edri.dataclass.event import Event
from edri.dataclass.injection import Injection
from edri.utility.function import camel2snake


class BaseDirectiveHandlerDict[T](TypedDict):
    pass


class BaseHandler[T: ResponseDirective](ABC):
    _directive_handlers: dict[Type[T], BaseDirectiveHandlerDict[T]] = {}

    def __init__(self,
                 scope: dict,
                 receive: Callable,
                 send: Callable):
        super().__init__()
        self.send = send
        self.scope = scope
        self.receive = receive
        self.scope = scope
        self.logger = getLogger(__name__)

        self.parameters: dict[str, Any] = self.parse_url_parameters()

    @classmethod
    def directive_handlers(cls) -> dict[Type[ResponseDirective], BaseDirectiveHandlerDict]:
        handlers = {}
        for class_obj in reversed(cls.mro()):
            if hasattr(class_obj, "_directive_handlers"):
                # noinspection PyProtectedMember
                handlers.update(class_obj._directive_handlers)
        return handlers

    @abstractmethod
    async def response(self, status: Any, data: Any, *args, **kwargs) -> None:
        pass

    @abstractmethod
    async def response_error(self, status: Any, response: Any, *args, **kwargs) -> None:
        pass

    def check_parameters(self, event_constructor: Type[Event]) -> None:
        check_parameters = {}
        for name, annotation in ((f.name, f.type) for f in fields(event_constructor)):
            if name.startswith("_") or name == "method" or name == "response":
                continue
            try:
                value = self.parameters.pop(name)
            except KeyError:
                raise ValueError(f"Missing value for parameter {name}")
            try:
                value = self.convert_type(value, annotation)
            except TypeError:
                raise ValueError(f"Wrong type {type(value)} for {name}:{annotation}")
            except Exception:
                raise ValueError("Unknown error during type checking")
            check_parameters[name] = value
        if self.parameters:
            raise ValueError(f"Unknown parameters: {self.parameters}")
        self.parameters = check_parameters

    def create_event(self, event_constructor: Type[Event]) -> Event:
        self.insert_default_parameters(event_constructor)
        self.check_parameters(event_constructor)
        # noinspection PyArgumentList
        event = event_constructor(**self.parameters)
        event._timing.stamp(self.__class__.__name__, "Created")
        return event

    def convert_type(self, value: Any, annotation: type) -> Any:
        """
        Validates and converts input values to the specified annotation type,
        supporting basic types, Optional, and lists with type annotations.

        Parameters:
            value: The input value to be validated and converted.
            annotation: The target type annotation for the conversion.

        Returns:
            The converted value if conversion is successful.

        Raises:
            TypeError: If the value cannot be converted to the specified type.
        """
        if get_origin(annotation) or isinstance(annotation, UnionType):
            if isinstance(annotation, UnionType) or get_origin(annotation) == Union:
                annotations = get_args(annotation)
                if value is None:
                    if NoneType in annotations:
                        return None
                    else:
                        raise TypeError(f"Value '{value}' cannot be converted to type {annotation}")
                for annotation in annotations:
                    try:
                        return self.convert_type(value, annotation)
                    except TypeError:
                        continue
                else:
                    raise TypeError(f"Value '{value}' cannot be converted to type {annotation}")
            elif get_origin(annotation) == list and isinstance(value, list):
                if len(get_args(annotation)) != 1:
                    raise TypeError("Type of list item must be specified")
                return [self.convert_type(value, get_args(annotation)[0]) for value in value]
            elif get_origin(annotation) == tuple and isinstance(value, tuple):
                return tuple(self.convert_type(v, a) for v, a in zip(value, get_args(annotation)))
            elif get_origin(annotation) == Literal and isinstance(value, str) and value in get_args(annotation):
                return value
            elif get_origin(annotation) == dict and isinstance(value, dict):
                a_args = get_args(annotation)
                return {self.convert_type(k, a_args[0]): self.convert_type(v, a_args[1]) for k, v in value.items()}
            else:
                raise TypeError(f"Value '{value}' cannot be converted to type {annotation}")
        else:
            if annotation is Any:
                return value
            elif isinstance(annotation, Injection):
                try:
                    for validator in annotation:
                        value = validator(value)
                    return value
                except ValueError:
                    raise TypeError(f"Value '{value}' cannot be converted to type {annotation}")
            elif isinstance(value, annotation):
                return value
            elif isinstance(value, str) and value.lower() == "false" and annotation == bool:
                return False
            try:
                return annotation(value)
            except Exception:
                if hasattr(annotation, "fromisoformat"):
                    try:
                        return annotation.fromisoformat(value)
                    except Exception:
                        raise TypeError(
                            "Value '%s' cannot be converted from isoformat to type %s" % (value, annotation))
                else:
                    raise TypeError(f"Value '{value}' cannot be converted to type {annotation}")

    @abstractmethod
    def handle_directives(self, directives: list[ResponseDirective]) -> ...:
        pass

    def insert_default_parameters(self, event_constructor: Type[Event]) -> None:
        for field in fields(event_constructor):
            if field.name.startswith("_") or field.name in ("response", "method"):
                continue
            if field.name in self.parameters:
                continue
            if field.default is not MISSING:
                self.parameters[field.name] = field.default
                continue
            if field.default_factory is not MISSING:
                self.parameters[field.name] = field.default_factory()
                continue

    def parse_url_parameters(self) -> dict[str, Any]:
        url_parameters = parse_qs(unquote(self.scope["query_string"].decode()), keep_blank_values=True)
        return {
            camel2snake(key.strip("[]")): value if key.endswith("[]") else value[-1] for key, value in
            url_parameters.items()
        }