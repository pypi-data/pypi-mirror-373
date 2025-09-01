from dataclasses import dataclass


@dataclass
class ResponseDirective:
    """Base class for all response directives"""
    pass


@dataclass
class HTTPResponseDirective(ResponseDirective):
    """Base class for all HTTP directives"""
    pass


@dataclass
class WebSocketResponseDirective(ResponseDirective):
    """Base class for all WebSocket directives"""
    pass


@dataclass
class HTMLResponseDirective(HTTPResponseDirective):
    """Base class for all HTML directives"""
    pass


@dataclass
class RESTResponseDirective(HTTPResponseDirective):
    """Base class for all HTML directives"""
    pass
