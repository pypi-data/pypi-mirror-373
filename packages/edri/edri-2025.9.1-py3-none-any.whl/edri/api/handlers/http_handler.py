from abc import ABC, abstractmethod
from asyncio import create_task
from base64 import b64decode
from enum import Enum
from http import HTTPStatus, HTTPMethod
from http.cookies import SimpleCookie, Morsel
from io import BytesIO
from json import loads, JSONDecodeError
from logging import warning
from mimetypes import guess_type
from pathlib import Path
from re import compile, escape, sub
from tempfile import NamedTemporaryFile, TemporaryFile
from types import NoneType
from typing import Callable, Type, Pattern, Any, Unpack, TypedDict, NotRequired, AnyStr, BinaryIO, Self, Literal, get_args, get_origin, \
    Union
from urllib.parse import parse_qsl, quote
from uuid import UUID

from multipart import MultipartParser

from edri.api import Headers
from edri.api.dataclass import File
from edri.api.dataclass.api_event import api_events
from edri.api.handlers import BaseHandler
from edri.api.handlers.base_handler import BaseDirectiveHandlerDict
from edri.config.constant import ApiType
from edri.config.setting import MAX_BODY_SIZE, ASSETS_PATH, UPLOAD_FILES_PREFIX, ENVIRONMENT, CORS_HEADERS, CORS_ORIGINS, CORS_CREDENTIALS, \
    CORS_MAX_AGE, UPLOAD_FILES_PATH
from edri.dataclass.directive import HTTPResponseDirective, ResponseDirective
from edri.dataclass.directive.base import InternalServerErrorResponseDirective, UnauthorizedResponseDirective
from edri.dataclass.directive.http import CookieResponseDirective, AccessDeniedResponseDirective, NotFoundResponseDirective, \
    ConflictResponseDirective, HeaderResponseDirective, UnprocessableContentResponseDirective, BadRequestResponseDirective
from edri.dataclass.event import Event
from edri.dataclass.injection import Injection
from edri.utility import NormalizedDefaultDict
from edri.utility.function import camel2snake
from edri.utility.shared_memory_pipe import SharedMemoryPipe
from edri.utility.validation import StringValidation


class EventTypesExtensionsDict(TypedDict):
    url: str
    url_re: NotRequired[Pattern[AnyStr]]
    url_original: NotRequired[str]
    method: HTTPMethod
    cookies: dict[str, str]
    headers: dict[str, str]
    scope: dict[str, str]
    template: str | None


type EventTypesExtensions = dict[Type[Event], EventTypesExtensionsDict]


class ResponseKW(TypedDict):
    headers: NormalizedDefaultDict[str, Headers]


class ResponseErrorKW(TypedDict):
    headers: NotRequired[NormalizedDefaultDict[str, Headers]]


class HTTPDirectiveHandlerDict[T](BaseDirectiveHandlerDict):
    routine: NotRequired[
        Callable[[T, dict[str, Headers]], NormalizedDefaultDict[str, Headers]] | Callable[[T], NormalizedDefaultDict[str, Headers]]]
    status: NotRequired[HTTPStatus]
    headers: NotRequired[list[str]]


class HTTPCrossOriginResourceSharing(TypedDict):
    origins: list[str]
    headers: str


class URLNode:
    DATA_TYPE_REGEX: dict[Any, Any] = {
        int: lambda name, _: rf"^(?P<{escape(name)}>\d+)$",
        str: lambda name, _: rf"^(?P<{escape(name)}>[-A-z0-9._~]+)$",
        float: lambda name, _: rf"^(?P<{escape(name)}>\d+\.\d+)$",
        bool: lambda param, _: rf"^(?P<{escape(param)}>(true|false|1|0))$",
        UUID: lambda name, _: rf"^(?P<{escape(name)}>[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-5][0-9a-f]{{3}}-[089ab][0-9a-f]{{3}}-[0-9a-f]{{12}})$",
        Literal: lambda name, type_: rf"^(?P<{escape(name)}>{'|'.join(map(escape, map(str, get_args(type_))))})$",
        Enum: lambda name, type_: rf"^(?P<{escape(name)}>{'|'.join(escape(str(member.value)) for member in type_)})$",
    }

    def __init__(self, url: str, is_dynamic: bool = False):
        if url.endswith("/"):
            url = url[:-1]
        self.url: str = url
        self.is_dynamic = is_dynamic
        self.children: dict[str, Self] = {}
        self.dynamic_children: dict[Pattern[AnyStr], Self] = {}
        self.methods: dict[HTTPMethod, Type[Event]] = {}

    def insert(self, url: str, method: HTTPMethod, event: Type[Event]):
        if url.startswith("/"):
            url = url[1:]
        if url.endswith("/"):
            url = url[:-1]
            warning("URLs are not supposed to end with the /")
        parts = url.split("/")  # Split URL by "/"
        node = self

        for part in parts:
            if part.startswith("{") and part.endswith("}"):  # Detect dynamic part
                part = part[1:-1]
                try:
                    data_type = event.__annotations__[part]
                except KeyError as e:
                    raise KeyError(f"Parameter in URL is missing in data class items: {event}") from e
                try:
                    regex_pattern, optional = self._convert_to_regex(part, data_type)
                except TypeError as e:
                    raise TypeError(f"Parameter in URL cannot be converted: {event}") from e
                for child_url, child_node in node.children.items():
                    if regex_pattern.match(child_url):
                        raise ValueError(f"Dynamic url in conflict with static url: {child_url} {event}")
                if regex_pattern not in node.dynamic_children:
                    node.dynamic_children[regex_pattern] = URLNode(part, is_dynamic=True)
                node = node.dynamic_children[regex_pattern]
            else:
                for child_pattern, child_node in node.dynamic_children.items():
                    if child_pattern.match(part):
                        raise ValueError(f"Dynamic url in conflict with static url: {part} {event}")
                if part not in node.children:
                    node.children[part] = URLNode(part)
                node = node.children[part]

        if method in node.methods:
            raise KeyError(f"Method {method} already exists for this URL: {url}")
        if method is None:
            raise ValueError(f"Method for event {event} is not defined")
        node.methods[method] = event

    def _find(self, url: str) -> tuple[dict[HTTPMethod, Type[Event]] | None, dict[str, Any]]:
        if url.startswith("/"):
            url = url[1:]
        parts = url.split("/")  # Split URL by "/"
        node = self
        parameters: dict[str, Any] = {}

        for part in parts:
            child = node.children.get(part, None)
            if not child:
                for pattern, child in node.dynamic_children.items():
                    match = pattern.match(part)
                    if match:
                        parameters.update(match.groupdict())
                        break
                else:
                    child = None
            if not child:
                return None, parameters
            node = child

        return node.methods, parameters

    def find_methods(self, url: str) -> tuple[dict[HTTPMethod, Type[Event]], dict[str, Any]] | None:
        methods, parameters = self._find(url)
        return methods, parameters

    @classmethod
    def _convert_to_regex(cls, parameter_name: str, type_: type) -> tuple[Pattern[str], bool]:
        """Converts a dynamic URL parameter to a regex pattern"""

        # Select the appropriate lambda function
        optional = False
        origin = get_origin(type_)
        if origin is not None:
            if origin is Union:
                args = get_args(type_)
                if NoneType in args:
                    optional = True
                    args = tuple(arg for arg in args if arg is not type(None))
                if len(args) > 1:
                    raise TypeError("Union is supported only with NoneType")
                type_ = args[0]
                origin = get_origin(type_)
                if not origin:
                    origin = type_

            regex_function = cls.DATA_TYPE_REGEX.get(origin)
        elif isinstance(type_, Injection):
            previous_regex = None
            for vot in type_.classes:
                for base in vot.__mro__[1:]:  # Skip the type itself
                    regex_function = cls.DATA_TYPE_REGEX.get(base)

                    if regex_function:
                        if previous_regex is None:
                            previous_regex = regex_function
                        elif previous_regex != regex_function:
                            raise TypeError("All classes in 'inject' must have the same base class when used as URL parameters.")
                        break  # Only check the first valid base class regex

            if vot is StringValidation:
                regex = type_.parameters.get("regex", None)
                if regex is not None:
                    regex_function = lambda name, _: rf"^(?P<{escape(name)}>{sub(r'^\^(.*)\$$', r'\1', regex.pattern)})$"

        elif issubclass(type_, Enum):
            regex_function = cls.DATA_TYPE_REGEX.get(Enum)
        else:
            regex_function = cls.DATA_TYPE_REGEX.get(type_)
            # Resolve deeper inheritance
            if not regex_function:
                for base in type_.__mro__[1:]:  # Skip the type itself
                    regex_function = cls.DATA_TYPE_REGEX.get(base)
                    if regex_function:
                        break

        if not regex_function:
            raise TypeError(f"Data type {type_} is not allowed in URL")

        pattern = regex_function(parameter_name, type_)
        return compile(rf"({pattern})?" if optional else pattern), optional

    def __repr__(self, level=0) -> str:
        """Recursively represents the URL tree structure."""
        indent = "  " * level  # Indentation for tree hierarchy
        methods_str = f" [{', '.join(m.value for m in self.methods)}]" if self.methods else ""

        if self.is_dynamic:
            repr_str = f"{indent}- {{{self.url}}}{methods_str}\n"
        else:
            repr_str = f"{indent}- {self.url}{methods_str}\n"

        # Static children
        for child in self.children.values():
            repr_str += child.__repr__(level + 1)

        # Dynamic children
        for dyn_key, dyn_child in self.dynamic_children.items():
            #     repr_str += f"{indent}  * {dyn_key} (Dynamic)\n"
            repr_str += dyn_child.__repr__(level + 1)

        return repr_str


class HTTPHandler[T: HTTPResponseDirective](BaseHandler, ABC):
    _directive_handlers: dict[Type[T], HTTPDirectiveHandlerDict[T]] = {
        CookieResponseDirective: {
            "routine": lambda directive, headers: (
                {"cookie": HTTPHandler._create_cookie(directive, headers)}
            ),
            "headers": ["cookie"],
        },
        AccessDeniedResponseDirective: {
            "status": HTTPStatus.FORBIDDEN,
        },
        InternalServerErrorResponseDirective: {
            "status": HTTPStatus.INTERNAL_SERVER_ERROR,
        },
        UnauthorizedResponseDirective: {
            "status": HTTPStatus.UNAUTHORIZED,
        },
        NotFoundResponseDirective: {
            "status": HTTPStatus.NOT_FOUND,
        },
        ConflictResponseDirective: {
            "status": HTTPStatus.CONFLICT,
        },
        HeaderResponseDirective: {
            "routine": lambda directive: (
                {directive.name: [directive.value]}
            ),
        },
        UnprocessableContentResponseDirective: {
            "status": HTTPStatus.UNPROCESSABLE_ENTITY,
        },
        BadRequestResponseDirective: {
            "status": HTTPStatus.BAD_REQUEST,
        }
    }

    event_type_extensions: dict[Type[Event], Any] = {}
    event_type_names = {}
    url_root = None
    cors: HTTPCrossOriginResourceSharing = {
        "headers": "Accept,Accept-Language,Content-Language,Content-Type,Filename",
        "origins": [],
    }
    if CORS_HEADERS:
        if CORS_HEADERS.startswith(","):
            headers = CORS_HEADERS[1:]
        cors["headers"] += f",{CORS_HEADERS}"
    if CORS_ORIGINS:
        cors["origins"] = [origin.strip() for origin in CORS_ORIGINS.split(",")]

    def __init__(self,
                 scope: dict,
                 receive: Callable,
                 send: Callable,
                 headers: NormalizedDefaultDict[str, Headers]):
        super().__init__(scope, receive, send)
        self.headers = headers
        self.cookies = self.parse_cookies(self.headers.get("cookie", ""))
        self.body = BytesIO()

        if HTTPHandler.url_root is None:
            HTTPHandler.url_root = URLNode("")
            for api_event in api_events:
                HTTPHandler.event_type_extensions[api_event.event] = {}
                HTTPHandler.event_type_extensions[api_event.event]["cookies"] = api_event.cookies
                HTTPHandler.event_type_extensions[api_event.event]["headers"] = api_event.headers
                HTTPHandler.event_type_extensions[api_event.event]["scope"] = api_event.scope
                HTTPHandler.event_type_extensions[api_event.event]["template"] = api_event.template
                HTTPHandler.event_type_extensions[api_event.event]["url"] = api_event.url

                if ApiType.HTML in api_event.exclude and ApiType.REST in api_event.exclude:
                    continue

                HTTPHandler.event_type_names[api_event.event.__name__] = api_event.event
                HTTPHandler.url_root.insert(api_event.url, api_event.method, api_event.event)

    @classmethod
    @abstractmethod
    def api_type(cls) -> ApiType:
        pass

    @classmethod
    def get_event_type_extensions(cls):
        return HTTPHandler.event_type_extensions

    @classmethod
    def directive_handlers(cls) -> dict[Type[ResponseDirective], HTTPDirectiveHandlerDict]:
        handlers = {}
        for class_obj in reversed(cls.mro()):
            if hasattr(class_obj, "_directive_handlers"):
                # noinspection PyProtectedMember
                handlers.update(class_obj._directive_handlers)
        return handlers

    @staticmethod
    def _create_cookie(directive: CookieResponseDirective, headers: NormalizedDefaultDict[str, Headers]) -> SimpleCookie:
        """
        Creates a SimpleCookie object using the attributes from the CookieResponseDirective.

        Args:
            directive (CookieResponseDirective): The directive containing cookie attributes.
            headers (Dict[str, Any]): The current headers, potentially containing existing cookies.

        Returns:
            SimpleCookie: A SimpleCookie object with the cookie set according to the directive.
        """

        # Initialize the SimpleCookie object with existing cookies, if any
        if headers["cookie"]:
            cookie = headers["cookie"]
            cookie[directive.name] = directive.value
        else:
            cookie = SimpleCookie({directive.name: directive.value})

        # Set additional attributes for the specified cookie name
        if directive.path:
            cookie[directive.name]['path'] = directive.path
        if directive.expires:
            cookie[directive.name]['expires'] = directive.expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')
        if directive.comment:
            cookie[directive.name]['comment'] = directive.comment
        if directive.domain:
            cookie[directive.name]['domain'] = directive.domain
        if directive.max_age is not None:
            cookie[directive.name]['max-age'] = directive.max_age
        if directive.secure:
            cookie[directive.name]['secure'] = 'True'
        if directive.version is not None:
            cookie[directive.name]['version'] = directive.version
        if directive.httponly:
            cookie[directive.name]['httponly'] = 'True'
        if directive.samesite:
            cookie[directive.name]['samesite'] = directive.samesite

        return cookie

    def get_headers_binary(self, headers: NormalizedDefaultDict[str, Headers]) -> list[tuple[bytes, bytes]]:
        response_headers = self.get_default_headers()
        response_headers.update(headers)
        headers_list = []
        for header, values in response_headers.items():
            if header == "cookie" and isinstance(values, SimpleCookie):
                for cookie in values.values():
                    headers_list.append((b"Set-Cookie", cookie.OutputString().encode(errors="replace")))
                continue
            for value in values:
                headers_list.append((header.encode(errors="replace"), value.encode(errors="replace")))
        return headers_list

    def get_default_headers(self) -> NormalizedDefaultDict[str, Headers]:
        response_headers = NormalizedDefaultDict[str, Headers](list)
        response_headers["Access-Control-Allow-Headers"].append(self.cors["headers"])
        if CORS_MAX_AGE:
            response_headers["Access-Control-Max-Age"].append(CORS_MAX_AGE)
        response_headers["Access-Control-Allow-Credentials"].append("true" if CORS_CREDENTIALS else "false")
        origin = self.headers.get("origin", [])
        if len(origin) > 0:
            if origin[0] in self.cors["origins"]:
                response_headers["Access-Control-Allow-Origin"].append(origin[0])
            elif ENVIRONMENT == "development":
                self.logger.warning("Please set CORS Origin properly")
                self.logger.debug("Allow origins: %s", self.cors["origins"])
                response_headers["Access-Control-Allow-Origin"].append(origin[0])
        return response_headers

    async def response_error(self, status, data: bytes | None = None, *args, **kwargs: Unpack[ResponseErrorKW]) -> None:
        headers = kwargs.get("headers", None)
        if headers is None:
            headers = NormalizedDefaultDict[str, Headers](list)
        if data is None:
            data = 'No more information'.encode("utf-8")
        await self.response(status, data, headers=headers)

    @staticmethod
    def parse_cookies(cookie: str) -> SimpleCookie[str]:
        return SimpleCookie(cookie)

    def handle_multipart(self, data: BinaryIO) -> None:
        try:
            content_type = self.headers.get("content-type", [])
            if len(content_type) < 2:
                raise ValueError("Boundary not found in content-type header")
            boundary = content_type[1].split("=")[1] if "=" in content_type[1] else None
            if not boundary:
                raise ValueError("Boundary not found in content-type header")
            multipart = MultipartParser(data, boundary, charset="utf-8")
            for part in multipart:
                if not part.filename:
                    self.parameters[camel2snake(part.name)] = part.file.read().decode("utf-8", errors="replace")
                else:
                    with NamedTemporaryFile(prefix=UPLOAD_FILES_PREFIX, dir=UPLOAD_FILES_PATH, delete=False) as received_temp_file:
                        received_temp_file.write(part.file.read())
                        received_file = File(
                            file_name=part.filename,
                            mime_type=part.content_type,
                            path=Path(received_temp_file.name),
                        )

                        self.parameters[camel2snake(part.name)] = received_file
        except ValueError as e:
            raise Exception("Input values not in expected format") from e
        except Exception as e:
            raise Exception("Unknown error") from e

    def handle_json(self) -> None:
        self.body.seek(0, 2)
        if self.body.tell() == 0:
            return
        self.body.seek(0)
        try:
            self.parameters.update({camel2snake(key): value for key, value in loads(self.body.read()).items()})
        except JSONDecodeError as e:
            self.logger.warning("Cannot process json data", exc_info=e)
            raise e
        except Exception as e:
            self.logger.error("Unknown error", exc_info=e)
            raise e

    def handle_url_encoded(self) -> None:
        self.body.seek(0, 2)
        if self.body.tell() == 0:
            return
        self.body.seek(0)
        body_parsed = parse_qsl(
            self.body.read().decode(errors="ignore"),
            keep_blank_values=True,
        )
        for key, value in body_parsed:
            if key.endswith("[]"):
                key = key[:-2]
                if key not in self.parameters:
                    self.parameters[key] = [value]
                else:
                    self.parameters[key].append(value)
            else:
                self.parameters[key] = value

    async def parse_body_smp(self, smp: SharedMemoryPipe):
        while data := await self.receive():
            body = data.get("body")
            if body is not None:
                smp.write(body)
            if not data.get("more_body"):
                smp.close()
                break

    async def parse_body(self, event: Type[Event]) -> None:
        if not self.headers["content-type"]:
            return

        if event._is_file_only is None:
            while self.body.tell() < MAX_BODY_SIZE:
                body = await self.receive()
                data = body.get("body", None)
                self.body.write(data)
                if not body["more_body"]:
                    if "application/json" in self.headers["content-type"]:
                        self.handle_json()
                        self.body.close()
                        return
                    elif "application/x-www-form-urlencoded" in self.headers["content-type"]:
                        self.handle_url_encoded()
                        self.body.close()
                        return
                    else:
                        raise ValueError(f"Request is bigger then {MAX_BODY_SIZE=}B")

        if "100-continue" in self.headers["expect"]:
            if len(self.headers["filename"]) == 1:
                try:
                    file_name = b64decode(self.headers["filename"][0]).decode(errors="replace")
                except Exception:
                    raise ValueError("Filename cannot be extracted")
                else:
                    smp = SharedMemoryPipe()
                    self.parameters[event._is_file_only] = File(
                        file_name=file_name,
                        mime_type=self.headers["content-type"][0],
                        path=smp.reader(),
                    )
                    create_task(self.parse_body_smp(smp))
            else:
                raise ValueError("Filename header in wrong format")
        else:
            if "multipart/form-data" in self.headers["content-type"]:
                with TemporaryFile(prefix=UPLOAD_FILES_PREFIX) as temporary_file:
                    while data := await self.receive():
                        temporary_file.write(data.get("body", None))
                        if not data["more_body"]:
                            break
                    temporary_file.flush()
                    temporary_file.seek(0)
                    self.handle_multipart(temporary_file)
            else:
                if len(self.headers["filename"]) == 1:
                    try:
                        file_name = b64decode(self.headers["filename"][0]).decode(errors="replace")
                    except Exception:
                        raise ValueError("Filename cannot be extracted")
                    else:
                        named_temporary_file = NamedTemporaryFile(prefix=UPLOAD_FILES_PREFIX, dir=UPLOAD_FILES_PATH,
                                                                  delete=False)
                        named_temporary_file_path = Path(named_temporary_file.name)
                        while data := await self.receive():
                            named_temporary_file.write(data.get("body", None))
                            if not data["more_body"]:
                                break
                        named_temporary_file.flush()
                        named_temporary_file.seek(0)
                        self.parameters[event._is_file_only] = File(
                            file_name=file_name,
                            mime_type=self.headers["content-type"][0],
                            path=named_temporary_file_path,
                        )
                else:
                    raise ValueError("Filename header in wrong format")

    async def response(self, status: HTTPStatus, data: bytes, *args, **kwargs: Unpack[ResponseKW]):
        headers = kwargs["headers"]
        if headers is None:
            headers = NormalizedDefaultDict(list)
        headers["Content-Length"].append(str(len(data)))
        await self.send({
            'type': 'http.response.start',
            'status': status,
            'headers': self.get_headers_binary(headers),
        })

        await self.send({
            'type': 'http.response.body',
            'body': data,
            'more_body': False
        })

    def response_error_prepare(self, status: HTTPStatus, response: Event | dict | None) -> dict:
        data = {
            "status_code": status.value,
            "status": status.name,
            "description": status.description,
            "reasons": []
        }

        if isinstance(response, Event):
            directives = response.get_response().get_directives()
            for directive in directives:
                handler: HTTPDirectiveHandlerDict | None = self.directive_handlers().get(directive.__class__, None)
                if not handler:
                    continue
                handler_status = handler.get("status", None)
                if not handler_status:
                    continue
                if handler_status.is_client_error or handler_status.is_server_error:
                    message = getattr(directive, "message", None)
                    if message:
                        data["reasons"].append({"message": message, "status_code": handler_status.value})
        elif isinstance(response, dict):
            data.update(response)
        return data

    async def response_assets(self, file) -> bool:
        asset_file = Path(ASSETS_PATH, file if file[0] != "/" else file[1:])
        if not asset_file.is_file():
            self.logger.warning("File not found")
            return False
        mime_types = guess_type(asset_file)
        headers = NormalizedDefaultDict[str, Headers](list)
        headers["Content-Type"].append(mime_types[0] if mime_types[0] else "text/html")
        headers["Content-Length"].append(str(asset_file.lstat().st_size))

        with asset_file.open("rb") as asset_file_descriptor:
            await self.response_file_path(asset_file_descriptor, headers)
        return True

    async def response_file(self, event: Event, *args, **kwargs: Unpack[ResponseKW]):
        headers = kwargs["headers"]
        file = event.response.file

        headers["Content-Type"].append(file.mime_type)
        headers["Content-Disposition"].append(f"attachment;filename*=UTF-8''{quote(file.file_name, encoding='utf-8')}")

        if isinstance(file.path, Path):
            headers["Content-Length"].append(str(file.path.lstat().st_size))
            try:
                with file.path.open("rb") as data:
                    await self.response_file_path(data, headers)
            except FileNotFoundError as e:
                await self.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": "Response atribute 'file' path is invalid",
                    }, {
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": e,
                    }]
                })
            except IsADirectoryError as e:
                await self.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": "Response atribute 'file' is directory",
                    }, {
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": e,
                    }]
                })
            except AttributeError as e:
                await self.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": "Response atribute 'file' is not filled",
                    }, {
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": e,
                    }]
                })
            except Exception as e:
                await self.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": e,
                    }]
                })
        else:
            if file.path.total_size:
                headers["Content-Length"].append(str(file.path.total_size))
            else:
                headers["Transfer-Encoding"].append("chunked")
            try:
                await self.response_file_shared_memory_pipe(file.path, headers)
            except Exception as e:
                await self.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": e,
                    }]
                })

    async def response_file_path(self, file: BinaryIO, headers: NormalizedDefaultDict[str, Headers]):
        try:
            await self.send({
                'type': 'http.response.start',
                'status': HTTPStatus.OK,
                'headers': self.get_headers_binary(headers),
            })
            chunk_size = 1024 * 1024
            while data := file.read(chunk_size):
                await self.send({
                    'type': 'http.response.body',
                    'body': data,
                    'more_body': len(data) == chunk_size
                })
        except Exception as e:
            self.logger.error(e, exc_info=e)

    async def response_file_shared_memory_pipe(self, smp: SharedMemoryPipe, headers: NormalizedDefaultDict[str, Headers]):
        try:
            await self.send({
                'type': 'http.response.start',
                'status': HTTPStatus.OK,
                'headers': self.get_headers_binary(headers),
            })
            with smp as pipe:
                while True:
                    data = pipe.read()
                    if data is None:
                        await self.send({
                            'type': 'http.response.body',
                            'body': data or b'',
                            'more_body': False
                        })
                        break
                    await self.send({
                        'type': 'http.response.body',
                        'body': data ,
                        'more_body': True
                    })
        except Exception as e:
            self.logger.error(e, exc_info=e)
    def get_event_constructors(self) -> tuple[dict[HTTPMethod, Type[Event]], dict[str, Any]]:
        return self.url_root.find_methods(self.scope["path"].lower())

    def get_event_constructor(self) -> tuple[Type[Event] | None, dict[str, Any]]:
        method = HTTPMethod(self.scope["method"])
        event_constructor, parameters = self.url_root.find_event(self.scope["path"], method)
        if not event_constructor:
            raise ResourceWarning()
        return event_constructor, parameters

    def get_method(self) -> HTTPMethod:
        return HTTPMethod(self.scope["method"])

    def create_event(self, event_constructor: Type[Event]) -> Event:
        event_extension = self.event_type_extensions.get(event_constructor, None)
        if event_extension:
            headers = event_extension.get("headers", None)
            if headers:
                for event_argument, header_name in headers.items():
                    header_data = self.headers.get(header_name)
                    if not header_data:
                        position = 0
                        header_data_split = ""
                        while header_name + f".{position}" in self.headers:
                            header_data_split += self.headers.get(header_name + f".{position}")[0]
                            position += 1
                        if position > 0:
                            self.parameters[event_argument] = [header_data_split]
                            continue
                    self.parameters[event_argument] = header_data
            cookies = event_extension.get("cookies", None)
            if cookies:
                for event_argument, cookie_name in cookies.items():
                    cookie_data = self.cookies.get(cookie_name)
                    if not cookie_data:
                        position = 0
                        cookie_data_split = ""
                        while cookie_name + f".{position}" in self.cookies:
                            cookie_data_split += self.cookies.get(cookie_name + f".{position}").value
                            position += 1
                        if position > 0:
                            self.parameters[event_argument] = cookie_data_split
                            continue
                    self.parameters[event_argument] = cookie_data
            scope = event_extension.get("scope", None)
            if scope:
                self.parameters.update({k: self.scope.get(v, None) for k, v in scope.items()})
        return super().create_event(event_constructor)

    def handle_directives(self, directives: list[ResponseDirective]) -> tuple[HTTPStatus, NormalizedDefaultDict[str, Headers]]:
        status, headers = HTTPStatus.OK, NormalizedDefaultDict[str, Headers](list)
        for directive in directives:
            try:
                directive_handler = self.directive_handlers()[directive.__class__]
            except KeyError as e:
                self.logger.warning("Unknown directive: %s", directive, exc_info=e)
            else:
                if "status" in directive_handler:
                    status = directive_handler["status"]
                if "routine" in directive_handler:
                    if "headers" in directive_handler:
                        headers_demand = directive_handler["headers"]
                        partial_headers = directive_handler["routine"](directive, {k: headers[k] for k in headers_demand})
                        headers.update(partial_headers)
                    else:
                        partial_headers = directive_handler["routine"](directive)
                        for key, value in partial_headers.items():
                            headers[key].extend(value)

        return status, headers

    def convert_type(self, value: Any, annotation: Type) -> Any:
        if isinstance(value, Morsel):
            if annotation == Morsel:
                return value
            else:
                return super().convert_type(value.value, annotation)

        return super().convert_type(value, annotation)
