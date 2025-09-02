from http.cookies import SimpleCookie

from .middleware import Middleware
from .broker import Broker

type Headers = list[str] | SimpleCookie
