from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from edri.dataclass.directive import HTTPResponseDirective


@dataclass
class CookieResponseDirective(HTTPResponseDirective):
    """
    Represents a directive for setting an HTTP cookie in a response.

    Attributes:
        name (str): The name of the cookie.
        value (str): The value of the cookie.
        expires (Optional[datetime]): The date and time when the cookie expires. If not set, the cookie will be a session cookie.
        path (Optional[str]): The path within the domain where the cookie is valid. Defaults to the root path ('/').
        comment (Optional[str]): A comment for the cookie, providing additional information to the client. This is rarely used.
        domain (Optional[str]): The domain where the cookie is valid. If not set, defaults to the host of the request URL.
        max_age (Optional[int]): The maximum age of the cookie in seconds. If set, it overrides the `expires` attribute.
        secure (bool): Indicates if the cookie should only be transmitted over secure protocols like HTTPS.
        version (Optional[int]): The version of the cookie. Version 0 is the default and refers to "old" cookies, while version 1 is the newer cookie format.
        httponly (bool): Indicates if the cookie is accessible only through HTTP(S) and not available to JavaScript (helps mitigate cross-site scripting attacks).
        samesite (Optional[str]): Controls whether a cookie is sent with cross-site requests. Possible values are 'Lax', 'Strict', or 'None'.
    """
    name: str
    value: str
    expires: Optional[datetime] = None
    path: Optional[str] = None
    comment: Optional[str] = None
    domain: Optional[str] = None
    max_age: Optional[int] = None
    secure: bool = False
    version: Optional[int] = None
    httponly: bool = False
    samesite: Optional[str] = None


@dataclass
class AccessDeniedResponseDirective(HTTPResponseDirective):
    message: str | None = None


@dataclass
class NotFoundResponseDirective(HTTPResponseDirective):
    message: str | None = None


@dataclass
class ConflictResponseDirective(HTTPResponseDirective):
    message: str | None = None


@dataclass
class HeaderResponseDirective(HTTPResponseDirective):
    name: str
    value: str


@dataclass
class UnprocessableContentResponseDirective(HTTPResponseDirective):
    message: str | None = None


@dataclass
class BadRequestResponseDirective(HTTPResponseDirective):
    message: str | None = None
