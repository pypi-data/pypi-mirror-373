from dataclasses import dataclass, field
from typing import Type

from edri.api.handlers import HTTPHandler
from edri.dataclass.event import Event
from edri.dataclass.directive import HTMLResponseDirective
from edri.utility.function import format_url


@dataclass
class RedirectResponseDirective(HTMLResponseDirective):
    """Directive for redirecting to another URL, status 302 will be used"""
    location: Type[Event] | str  # The explicitly required parameter
    kwargs: dict = field(init=False, repr=False, default=None)

    def __init__(self, location: Type[Event] | str, /, **kwargs):
        self.location = location
        self.kwargs = kwargs

    @property
    def path(self) -> str:
        if isinstance(self.location, type) and issubclass(self.location, Event):
            extensions = HTTPHandler.event_type_extensions[self.location]
            return format_url(extensions["url"], **self.kwargs)
        return self.location