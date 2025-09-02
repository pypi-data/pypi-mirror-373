from dataclasses import _process_class, dataclass, field, asdict
from enum import Enum, auto
from typing import Any

from edri.api.dataclass.file import File
from edri.dataclass.directive import ResponseDirective
from edri.utility.function import snake2camel


class ResponseStatus(Enum):
    NONE = auto()
    OK = auto()
    FAILED = auto()


@dataclass
class Response:
    _status: ResponseStatus = field(init=False, default=ResponseStatus.NONE)
    _changed: bool | None = field(init=False, default=None)
    _directives: list[ResponseDirective] = field(init=False, default_factory=list)
    _is_file_only: bool = field(default=False, init=False)

    def as_dict(self, /, *, transform: bool, keep_concealed: bool) -> dict[str, Any]:
        response_keep = {"status": self._status.name}
        response_dict = asdict(self)
        if transform:
            response = {snake2camel(key, exceptions=("_", "id_")): value for key, value in response_dict.items() if
                        keep_concealed or not key.startswith("_")}
        else:
            response = {key: value for key, value in response_dict.items() if keep_concealed or not key.startswith("_")}
        response.update(response_keep)
        return response

    def get_status(self) -> ResponseStatus:
        return self._status

    def set_status(self, status: ResponseStatus) -> None:
        self._status = status

    def __setattr__(self, key: str, value: Any) -> None:
        if self._changed is not None and not self._changed:
            super().__setattr__("_changed", True)
            super().__setattr__("_status", ResponseStatus.OK)
        super().__setattr__(key, value)

    def __post_init__(self) -> None:
        self._directives = []
        self._changed = False  # Has to by the last

    def has_changed(self) -> bool:
        return self._changed if self._changed else False

    def add_directive(self, directive: ResponseDirective) -> None:
        if self._changed is not None and not self._changed:
            super().__setattr__("_changed", True)
            super().__setattr__("_status", ResponseStatus.OK)
        self._directives.append(directive)

    def get_directives(self) -> list[ResponseDirective]:
        return self._directives

    @property
    def is_file_only(self) -> bool:
        return self._is_file_only


def _response(cls, init, repr, eq, order, unsafe_hash, frozen, match_args, kw_only, slots, weakref_slot):
    for name, value in cls.__annotations__.items():
        attribute = getattr(cls, name, False)
        if attribute:
            setattr(cls, name, field(init=False, default=attribute))
        else:
            setattr(cls, name, field(init=False, default=None))

    dataclass = _process_class(cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen, match_args=match_args,
                               kw_only=kw_only, slots=slots, weakref_slot=weakref_slot)

    if len(cls.__annotations__) == 1:
        field_file = cls.__annotations__.get("file")
        if field_file == File:
            dataclass._is_file_only = True

    return dataclass


def response(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False,
             match_args=True, kw_only=False, slots=False, weakref_slot=None):
    def wrapper(cls):
        return _response(cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                         frozen=frozen, match_args=match_args, kw_only=kw_only, slots=slots, weakref_slot=weakref_slot)

    if cls is None:
        return wrapper

    return wrapper(cls)
