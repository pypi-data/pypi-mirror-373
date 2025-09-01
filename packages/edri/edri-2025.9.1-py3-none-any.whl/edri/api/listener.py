from asyncio import get_event_loop, create_task, wait, Event as AEvent, run
from http import HTTPStatus
from importlib import util
from json import JSONEncoder
from logging import getLogger
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from multiprocessing.queues import Queue
from os import makedirs
from typing import Callable, Type

from edri.api import Headers, Middleware
from edri.api.handlers import RESTHandler, HTMLHandler, WebsocketHandler
from edri.config.constant import ApiType
from edri.config.setting import HOST, PORT, API_RESPONSE_TIMEOUT, SSL_KEY, SSL_CERTIFICATE, UPLOAD_FILES_PATH
from edri.dataclass.directive import HTTPResponseDirective
from edri.dataclass.event import Event, ApiInfo
from edri.dataclass.response import ResponseStatus
from edri.events.api.client import Register, Unregister
from edri.utility import NormalizedDefaultDict


class Listener(Process):
    def __init__(self, api_broker_queue: Queue[Event], middlewares: list[Middleware], json_encoder: Type[JSONEncoder]) -> None:
        """
        Initializes the Listener class with the specified API broker queue and list of middlewares.

        Parameters:
            api_broker_queue (Queue[Event]): The queue for receiving events from the API broker.
            middlewares (list[Middleware]): The list of middleware components to be applied to the events.

        """
        super().__init__()
        self.api_broker_queue = api_broker_queue
        self.logger = getLogger(__name__)
        self.middlewares = middlewares
        self.json_encoder = json_encoder
        makedirs(UPLOAD_FILES_PATH, exist_ok=True)

    def run(self) -> None:
        if self.is_installed("uvicorn"):
            from uvicorn import Config, Server
            if SSL_KEY and SSL_CERTIFICATE:
                config = Config(
                    self.App(self.api_broker_queue, self.middlewares, self.json_encoder),
                    host=HOST,
                    port=PORT,
                    log_level="debug",
                    log_config=None,
                    ssl_keyfile=SSL_KEY,
                    ssl_certfile=SSL_CERTIFICATE
                )
            else:
                config = Config(
                    self.App(self.api_broker_queue, self.middlewares, self.json_encoder),
                    host=HOST,
                    port=PORT,
                    log_level="debug",
                    log_config=None
                )
            server = Server(config)
            server.run()

        elif self.is_installed("hypercorn"):
            from hypercorn.config import Config
            from hypercorn.asyncio import serve

            config = Config()
            config.bind = [f"{HOST}:{PORT}"]
            config.certfile = SSL_CERTIFICATE
            config.keyfile = SSL_KEY
            config.use_reloader = False
            config.loglevel = "debug"

            run(serve(
                self.App(self.api_broker_queue, self.middlewares, self.json_encoder),
                config
            ))
        else:
            raise RuntimeError("No supported ASGI server installed (uvicorn or hypercorn).")

    @staticmethod
    def is_installed(package_name: str) -> bool:
        return util.find_spec(package_name) is not None

    class App:
        def __init__(self, api_broker_queue: Queue[Event], middlewares: list[Middleware], json_encoder: Type[JSONEncoder]) -> None:
            self.ab_queue = api_broker_queue
            self.logger = getLogger(__name__)
            self._middlewares = middlewares
            self.handler_wrappers: dict[str, Callable] = {
                "http": self.http,
                "websocket": self.websocket,
                "lifespan": self.lifespan
            }
            self.json_encoder = json_encoder

        async def __call__(self, scope, receive, send) -> None:
            try:
                handler_wrapper = self.handler_wrappers.get(scope['type'])
            except KeyError as e:
                self.logger.error("Unknown type: %s", scope['type'], exc_info=e)
            else:
                headers = self.parse_headers(scope.get("headers", {}))
                await handler_wrapper(scope, receive, send, headers)

        @staticmethod
        def parse_headers(headers) -> NormalizedDefaultDict[str, Headers]:
            parsed_headers = NormalizedDefaultDict[str, Headers](list)
            for header, value in headers:
                header = header.decode(errors="replace").lower()
                if header == "cookie":
                    parsed_headers[header] = value.decode(errors="replace")
                    continue
                parsed_headers[header].extend(
                    value.decode(errors="replace").split(";"))
            return parsed_headers

        @staticmethod
        async def lifespan(_, receive, send, __) -> None:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})

        @staticmethod
        async def is_rest_request(headers: NormalizedDefaultDict[str, Headers]) -> bool:
            if "xmlhttprequest" in map(lambda x: x.lower(), headers.get("x-requested-with", [])):
                return True
            elif "application/json" in headers.get("accept", []):
                return True
            else:
                return False

        async def http(self, scope, receive, send, headers) -> None:
            if await self.is_rest_request(headers):
                handler = RESTHandler[HTTPResponseDirective](scope, receive, send, headers, self.json_encoder)
                api_type = ApiType.REST
            else:
                handler = HTMLHandler[HTTPResponseDirective](scope, receive, send, headers)
                api_type = ApiType.HTML

            event_constructors, parameters = handler.get_event_constructors()
            if not event_constructors:
                self.logger.debug("Resource not found, trying file")
                if isinstance(handler, HTMLHandler):
                    if await handler.response_assets(scope["path"]):
                        return
                self.logger.debug("Unknown url %s", scope["path"])
                await handler.response_error(HTTPStatus.NOT_FOUND, {
                    "reasons": [{
                        "status_code": HTTPStatus.NOT_FOUND,
                        "message": "Unknown url %s" % scope["path"],
                    }]
                })
                return
            if scope["method"] == "OPTIONS":
                if event_constructors:
                    headers = NormalizedDefaultDict[str, Headers](list, {
                        "Access-Control-Allow-Methods": [
                            ", ".join(x.value for x in event_constructors.keys())
                        ]
                    })
                    await handler.response(HTTPStatus.OK, data=b"", headers=headers)
                    return
            else:
                method = handler.get_method()
                event_constructor = event_constructors.get(method)
                if event_constructor:
                    handler.parameters = handler.parameters | parameters
                else:
                    self.logger.debug("There is no event for method %s url %s", scope["method"], scope["path"])
                    await handler.response_error(HTTPStatus.METHOD_NOT_ALLOWED, {
                        "reasons": [{
                            "status_code": HTTPStatus.METHOD_NOT_ALLOWED,
                            "message": "There is no event for method %s url %s" % (scope["method"], scope["path"]),
                        }]
                    })
                    return

            try:
                await handler.parse_body(event_constructor)
            except Exception as e:
                self.logger.error("Parse of body failed", exc_info=e)
                reasons = [{
                        "status_code": HTTPStatus.BAD_REQUEST,
                        "message": "Parse of body failed",
                    }]
                current_exception = e
                while current_exception:
                    reasons.append({
                        "message": str(current_exception)
                    })
                    # Move to the next exception in the chain
                    current_exception = current_exception.__context__
                await handler.response_error(HTTPStatus.BAD_REQUEST, {
                    "reasons": reasons
                })
                return
            # Create Event
            try:
                event = handler.create_event(event_constructor)
            except ValueError as e:
                self.logger.warning("Cannot create %s", event_constructor, exc_info=e)
                reasons = [{
                    "status_code": HTTPStatus.BAD_REQUEST,
                    "message": "Cannot create %s" % event_constructor,
                }]

                # Collect error messages for the initial exception
                current_exception = e
                while current_exception:
                    reasons.append({
                        "message": str(current_exception)
                    })
                    # Move to the next exception in the chain
                    current_exception = current_exception.__context__
                await handler.response_error(HTTPStatus.BAD_REQUEST, {
                    "reasons": reasons
                })
                return
            #
            if (register := self.register(handler.api_type())) is None:
                self.logger.error("Registration failed")
                await handler.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": "Registration failed",
                    }]
                })
                return
            pipe, key = register
            event._api = ApiInfo(key, api_type)

            event_loop = get_event_loop()
            await event_loop.run_in_executor(None, self.ab_queue.put, event)
            available_data = await event_loop.run_in_executor(None, pipe.poll, API_RESPONSE_TIMEOUT)

            if not available_data:
                self.logger.error("No response was returned in %ss", API_RESPONSE_TIMEOUT)
                await handler.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": "No response was returned in %ss" % API_RESPONSE_TIMEOUT,
                    }]
                })
                self.unregister(pipe, event._api)
                return

            event_response: Event = pipe.recv()
            if event_response.get_response() is None:
                self.logger.warning("No Response was found in the event: %s", event_response)
                await handler.response_error(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "reasons": [{
                        "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "message": "No Response was found in the event: %s" % event_response,
                    }]
                })
                self.unregister(pipe, event._api)
                return

            status, headers = handler.handle_directives(event_response.get_response().get_directives())
            if status.is_success:
                if event_response.get_response().is_file_only:
                    await handler.response_file(event_response, headers=headers)
                else:
                    await handler.response(status, event_response, headers=headers)
            else:
                await handler.response_error(status, event_response, headers=headers)
            self.unregister(pipe, event._api)

        async def websocket(self, scope, receive, send, headers) -> None:
            handler = WebsocketHandler(scope, receive, send, headers)
            if scope["path"] != "/":
                await handler.response_error(1011, None, {
                    "status": ResponseStatus.FAILED.name,
                    "reasons": ["Only root path is allowed"]
                })
                return
            if not await handler.accept_client():
                await handler.response_error(1011, None, {
                    "status": ResponseStatus.FAILED.name,
                    "reasons": ["Missing command"]
                })
                return

            # Attempt to register the client
            if (register := self.register(handler.api_type())) is None:
                self.logger.error("Registration failed")
                await handler.response_error(1011, None, {
                    "status": ResponseStatus.FAILED.name,
                    "reasons": ["Server error during event registration"]
                })
                return
            pipe, key = register
            api_info = ApiInfo(key, ApiType.WS)
            event_loop = get_event_loop()

            try:
                frame_available = AEvent()
                event_loop.add_reader(pipe.fileno(), frame_available.set)

                from_core = create_task(frame_available.wait())
                from_client = create_task(handler.receive())
                tasks = {from_core, from_client}

                while True:
                    done, pending = await wait(tasks, return_when="FIRST_COMPLETED")
                    tasks = set()

                    for task in done:
                        if task == from_client:
                            await handler.clear()
                            data = task.result()

                            # Parse received message
                            if not await handler.parse_body(data):
                                return

                            try:
                                event_constructor = await handler.get_event_constructor()
                            except ResourceWarning as e:
                                self.logger.debug("Missing command", exc_info=e)
                                await handler.response_error(1003, None, {
                                    "status": ResponseStatus.FAILED.name,
                                    "reasons": ["Command is missing in the message"]
                                })
                                continue

                            if not event_constructor:
                                self.logger.debug("Unknown command: %s", handler.command)
                                await handler.response_error(1003, None, {
                                    "status": ResponseStatus.FAILED.name,
                                    "reasons": [f"Command '{handler.command}' was not found"]
                                })
                                continue

                            try:
                                event = handler.create_event(event_constructor)
                            except ValueError as e:
                                self.logger.warning("Cannot create Event: %s", event_constructor, exc_info=e)
                                await handler.response_error(1003, None, {
                                    "status": ResponseStatus.FAILED.name,
                                    "reasons": [f"Command '{handler.command}' cannot be converted to event"]
                                })
                                continue

                            event._api = api_info
                            await event_loop.run_in_executor(None, self.ab_queue.put, event)

                            # Recreate the client task for the next message
                            from_client.cancel()
                            from_client = create_task(handler.receive())
                            tasks.add(from_client)

                        elif task == from_core:
                            event_response = pipe.recv()
                            if not event_response.has_response():
                                self.logger.warning("No Response was found in the event: %s", event_response)
                                await handler.response_error(None, event_response, {
                                    "status": ResponseStatus.FAILED.name,
                                    "reasons": [f"No Response was found in the event: {event_response}"]
                                })
                                self.unregister(pipe, api_info)
                                return
                            error = handler.handle_directives(event_response.get_response().get_directives())
                            if not error:
                                await handler.response(None, event_response, headers=NormalizedDefaultDict[str, Headers](list))
                            else:
                                await handler.response_error(None, event_response)

                            # Recreate the core task for the next response
                            from_core.cancel()
                            frame_available = AEvent()
                            event_loop.add_reader(pipe.fileno(), frame_available.set)
                            from_core = create_task(frame_available.wait())
                            tasks.add(from_core)

                    # Add any remaining pending tasks
                    tasks = tasks | pending
                    if len(tasks) == 0:
                        break

            finally:
                event_loop.remove_reader(pipe.fileno())
                self.unregister(pipe, api_info)

        def register(self, api_type: ApiType) -> tuple[Connection, str] | None:
            """
            Attempts to register a new client with the API. This involves sending a
            registration request through the queue and waiting for a response.

            Returns:
                Tuple[Connection, str] | None: A tuple containing the client connection
                and a registration key if registration is successful; None otherwise.
            """
            client_pipe, client_ab_pipe = Pipe()
            self.ab_queue.put(Register(socket=client_ab_pipe, type=api_type))
            if not client_pipe.poll(timeout=10):
                self.logger.critical("Client registration timeout!")
                client_pipe.close()
                return None
            event = client_pipe.recv()
            if not isinstance(event, Register):
                self.logger.critical("Client registration failed!")
                client_pipe.close()
                return None
            # noinspection PyProtectedMember
            if not event._api.key:
                self.logger.critical("Key is missing, client registration failed!")
                client_pipe.close()
                return None
            client_ab_pipe.close()
            # noinspection PyProtectedMember
            self.logger.debug("Client was registered %s", event._api.key)
            # noinspection PyProtectedMember
            return client_pipe, event._api.key

        def unregister(self, client_pipe: Connection, api_info: ApiInfo) -> None:
            """
            Unregisters a client based on the provided key and closes their communication pipe.

            Parameters:
                client_pipe (Connection): The communication pipe for the client.
                api_info (ApiInfo): The api info of the client to be unregistered.
            """
            unregister = Unregister()
            unregister._api = api_info
            self.ab_queue.put(unregister)
            client_pipe.close()
            self.logger.debug("Client has left - %s", api_info)
