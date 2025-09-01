from abc import ABC, ABCMeta
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from importlib import invalidate_caches, import_module, reload
from inspect import signature, Signature, ismethod, isfunction
from logging import getLogger, Logger
from multiprocessing import Process, Pipe, Queue
from multiprocessing.connection import Connection, wait
from random import randint
from time import sleep
from traceback import format_exc
from types import UnionType
from typing import Optional, Type, Tuple, Callable, Union, Generic, TypeVar, Never, get_args, Iterable, get_origin

from edri.abstract.manager.worker import Worker
from edri.abstract.worker import WorkerThread, WorkerProcess
from edri.dataclass.event import Event
from edri.dataclass.health_checker import Status
from edri.events.edri.group import Manager
from edri.events.edri.manager import StreamCreate, StreamMessage, StreamClose, WorkerQuit, Restart
from edri.events.edri.router import Subscribe, HealthCheck, UnsubscribeAll
from edri.events.edri.store import Get
from edri.utility.storage import Storage

T = TypeVar("T", bound=Event)


@dataclass
class ManagerWorkerEvent(Generic[T]):
    """
    Data class for associating events with worker types and specifying if they are requests.

    Attributes:
        event (Type[Event]): The event class.
        request (bool): Indicates if the event is a request (True) or a response (False).
        worker (WorkerLike): The worker type associated with the event.
    """
    event: Type[Event]
    request: bool
    worker: Union[Type[WorkerThread[T]], Type[WorkerProcess[T]]]


class ManagerBaseMeta(ABCMeta):

    def __new__(mcls, name, bases, namespace, /, **kwargs):
        for attr_name, attr_value in list(namespace.items()):
            if callable(attr_value) and (purpose := getattr(attr_value, "__purpose__", None)):  # Check for the decorator's marker
                if purpose == "request":
                    new_name = f"solve_req_{attr_name}"
                elif purpose == "response":
                    new_name = f"solve_res_{attr_name}"
                else:
                    raise ValueError(f"Invalid purpose: {purpose}")
                if new_name in namespace:
                    raise KeyError(f"This method is in conflict: {attr_name}")
                namespace[new_name] = namespace.pop(attr_name)
        return super().__new__(mcls, name, bases, namespace, **kwargs)


class ManagerBase(ABC, Process, metaclass=ManagerBaseMeta):
    """
        Base class for a manager that handles events and manages worker processes or threads.
        Inherits from `ABC` to be an abstract base class and `Process` for multiprocessing support.

        Attributes:
            router_queue (Optional["Queue[Event]"]): The queue for communicating with the router.
            logger (Optional[Logger]): Logger instance for logging events.
            _from_time (Optional[datetime]): Start time for filtering events.


        Methods:
            __init__: Constructor for initializing the manager.
            _find_worker: Finds a worker based on its communication pipe.
            _find_stream: Finds a worker associated with a specific stream.
            _prepare: Prepares the manager before starting the event resolver loop.
            _prepare_resolvers: Prepares methods for resolving request and response events.
            _remove_worker: Removes a worker from the manager's tracking.
            _resolve_undelivered_events: Resolves any undelivered events.
            _subscribe: Subscribes to events based on requests and responses.
            _subscribe_static_resolvers: Subscribes to static event resolvers.
            additional_pipes: Property for specifying additional pipes.
            name: Property for specifying the manager's name.
            workers: Property for defining workers and their associated events.
            after_start: Hook for actions after the manager starts.
            get_pipes: Gets a set of all pipes including the router and worker pipes.
            health_check: Handles health check events from the router.
            resolve: The central method for resolving events received by the manager.
            resolve_callback_pipe: Handles events received from unknown pipes.
            resolve_callback_worker: Default method for resolving events received from workers.
            resolve_unknown: Handles unknown events received from the router pipe.
            run: Main entry point for the manager process.
            run_resolver: Main loop for resolving events from all pipes.
            start: Starts the manager process with an optional router queue.
            start_worker: Starts a new worker for handling an event.
            store_get: Handles store get requests.
        """

    def __init__(self, router_queue: Optional[Queue] = None, logger: Optional[Logger] = None,
                 from_time: Optional[datetime] = None) -> None:
        """
        Initializes the manager with an optional router queue, logger, and start time for event filtering.

        Parameters:
            router_queue (Optional["Queue[Event]"]): Queue for communication with the router. Default is None.
            logger (Optional[Logger]): Logger instance for logging. If None, a default logger is created.
            from_time (Optional[datetime]): Start time for filtering events. Default is None.
        """
        super().__init__()
        self.router_queue: Queue
        if router_queue:
            self.router_queue = router_queue
        self.router_pipe: Connection
        self._unresolved: list[Event] = []
        if logger is None:
            self.logger = getLogger(self.name)
        else:
            self.logger = logger
        self._requests: dict[Type[Event], Union[Callable, Event]] = {}
        self._responses: dict[Type[Event], Union[Callable, Event]] = {}
        self._workers: Storage[Worker]
        self._manager_id: str
        self._from_time = from_time
        self._store_get: Optional[Callable] = None
        self._exceptions: list[tuple[str, dict, Exception, str]] = []

    def _subscribe(self) -> None:
        """
        Subscribes the manager to events by sending subscription requests to the router queue.
        It handles both requests and responses, registering them for the manager to resolve.
        """

        count = len(self._requests) + len(self._responses)
        if count == 0:
            self.logger.info("No events to subscribe!")
            return

        self.router_pipe, pipe = Pipe(duplex=False)
        self.logger.debug("Count of events to register: %s", count)

        def register_events(events: dict, is_request: bool) -> None:
            for event_type in events.keys():
                self.logger.debug("Registering of event: %s", event_type)
                self.router_queue.put(
                    Subscribe(pipe=pipe, name=self.name, event_type=event_type, request=is_request, from_time=self._from_time)
                )

                while True:
                    event = self.router_pipe.recv()
                    if isinstance(event, Subscribe):
                        self.logger.debug("Event was registered: %s", event.event_type)
                        break
                    else:
                        self.logger.debug("Unresolved event received during registration: %s", event)
                        self._unresolved.append(event)

        register_events(self._requests, is_request=True)
        register_events(self._responses, is_request=False)

        pipe.close()

        unresolved_count = len(self._unresolved)
        if unresolved_count > 0:
            self.logger.debug("Received %s undelivered events!", unresolved_count)
        self.logger.debug("All events were successfully registered!")

    def _unsubscribe_all(self) -> None:
        """
        ...
        """

        count = len(self._requests) + len(self._responses)
        if count == 0:
            self.logger.info("No events to unsubscribe!")
            return

        self.logger.debug("Count of events to unregister: %s", count)

        self._unresolved: list[Event] = list()
        self.router_queue.put(
            UnsubscribeAll(name=self.name)
        )
        while True:
            event = self.router_pipe.recv()
            if isinstance(event, UnsubscribeAll):
                self.logger.debug("All event was unregistered", )
                break
            else:
                self.logger.debug("Unresolved event received during registration: %s", event)
                self._unresolved.append(event)

        unresolved_count = len(self._unresolved)
        if unresolved_count > 0:
            self.logger.debug("Received %s undelivered events!", unresolved_count)
        self.logger.debug("All events were successfully unregistered!")

    def _resolve_undelivered_events(self) -> None:
        """
        Processes any events that were received but not resolved immediately upon subscription.
        This ensures no events are lost during the setup phase of the manager.
        """
        if self._unresolved:
            while True:
                try:
                    event = self._unresolved.pop(0)
                    self.logger.debug("Solving undelivered event: %s", event)
                except IndexError:
                    self.logger.debug("Unresolved events were resolved!")
                    break
                event._timing.stamp(self.__class__.__name__, "Received as undelivered")
                self.resolve(event)
                event._timing.stamp(self.__class__.__name__, "Resolved")
        else:
            self.logger.debug("No unresolved events!")
        del self._unresolved

    def _resolve_callback_stream_create(self, event: StreamCreate, worker: Worker) -> None:
        """
        Handles the creation of a new stream for communication between workers and the manager.

        Parameters:
            event (StreamCreate): The event indicating a request to create a new stream.
            worker (Worker): The worker instance associated with the stream creation request.
        """
        raise NotImplementedError("yet")
        # stream_event = event.event
        # key = f"{stream_event._command}_{randint(1000, 9999)}"
        # stream_event._stream = key
        # worker.streams[stream_event.__class__] = key
        # self.router_queue.put(stream_event)

    def _resolve_callback_stream_event(self, event: StreamMessage, worker: Worker) -> None:
        """
        Processes an event within an existing stream, routing it appropriately based on the worker and stream state.

        Parameters:
            event (StreamMessage): The event containing a event for a specific stream.
            worker (Worker): The worker instance that sent the stream event or for which the event is intended.
        """
        raise NotImplementedError("yet")
        # stream_event = event.event
        # stream_event._stream = worker.streams[stream_event.__class__]
        # self.router_queue.put(event.event)

    def _prepare_resolvers(self) -> None:
        """
        Prepares the resolvers by dynamically associating methods in the class with
        specific event types for handling requests and responses.

        This method iterates over all methods in the class that have names starting
        with 'solve_req_' or 'solve_res_'. It checks the signature of each method to
        ensure that its parameter is named 'event' and is a subclass of the `Event`
        dataclass. Based on the method's prefix, it associates the method with either
        a request or response handler in the `_requests` or `_responses` dictionaries
        respectively.

        Raises:
         AttributeError: If the parameter of the method is not named 'event'
                         or if the parameter is not a subclass of the `Event` dataclass.

        Methods:
         - `get_event(sig: Signature) -> Type[Event]`: Extracts and validates the event
             parameter from the method's signature. Ensures that the event parameter is
             named 'event' and is a subclass of the `Event` dataclass.

         - `methods_name`: A generator expression that yields method names starting with
             'solve_req_' or 'solve_res_'.

        Workflow:
         1. The method iterates over all the method names in the class that start with
            'solve_req_' or 'solve_res_'.
         2. For each method, it checks if it is a valid instance method. If not, it logs
            a warning message and continues to the next method.
         3. For valid methods, it retrieves the `event` type by calling `get_event()`
            with the method's signature.
         4. If the method name starts with 'solve_req_', it associates the method with
            the event type in the `_requests` dictionary.
         5. If the method name starts with 'solve_res_', it associates the method with
            the event type in the `_responses` dictionary.

        Attributes:
         - `_requests`: A dictionary that stores request handler methods, keyed by event type.
         - `_responses`: A dictionary that stores response handler methods, keyed by event type.
         - `logger`: A logging object used to log warnings for methods that do not meet
             the required criteria.
         """

        def get_events(sig: Signature) -> Iterable[Type[Event]]:
            # Extract the event parameter from the signature
            parameters = list(sig.parameters.values())
            if len(parameters) < 1:
                raise AttributeError("The solve method must have at least two parameters, "
                                     "with the second named 'event'.")

            parameter_event = parameters[0]
            if parameter_event.name != "event":
                raise AttributeError(
                    f"Second parameter of solve method must be named 'event', not '{parameter_event.name}'."
                )

            annotation = parameter_event.annotation

            # Check if it's a union of event types
            if get_origin(annotation) is UnionType:
                args = get_args(annotation)
                # Verify each type in the union is a valid subclass of Event
                for arg in args:
                    if not (isinstance(arg, type) and issubclass(arg, Event)):
                        raise AttributeError(
                            f"Each event type in the union must be a subclass of Event, not: {arg}"
                        )
                return args

            # If not a union, it must be a single event class
            # Check if it's actually a type and a subclass of Event
            if not (isinstance(annotation, type) and issubclass(annotation, Event)):
                raise AttributeError(
                    f"Type of event must be a subclass of Event dataclass, not: {annotation}"
                )

            return (annotation,)

        methods_name = (method_name for method_name in dir(self) if method_name.startswith(("solve_req_", "solve_res_")))
        for method_name in methods_name:
            method = getattr(self, method_name)
            if not (ismethod(method) or isfunction(method)):
                self.logger.warning("%s suppose to be a method", method_name)
                continue

            for event in get_events(signature(method)):
                if method_name.startswith("solve_req_"):
                    if event in self._requests:
                        raise TypeError(f"Event is already registered: {event}")
                    self._requests[event] = method
                else:
                    if event in self._responses:
                        raise TypeError(f"Event is already registered: {event}", )
                    self._responses[event] = method

    @property
    def additional_pipes(self) -> set[Connection]:
        """
        Specifies additional pipes for the manager to listen on. Override to add custom pipes.

        Returns:
            set[Connection]: A set of additional pipes.
        """
        return set()  # pragma: no cover

    @property
    def name(self) -> str:
        """
        Specifies the manager's name. Override to provide a custom name.

        Returns:
            str: The manager's name.
        """
        return self.__class__.__name__

    @property
    def workers(self) -> list[ManagerWorkerEvent]:
        """
        Defines workers and their associated events. Override to specify workers.

        Returns:
            list[ManagerWorkerEvent]: A list of `ManagerWorkerEvent` instances.
        """
        return []  # pragma: no cover

    def resolve_callback_worker(self, event: Event, worker: Worker) -> None:
        """
         Default method for handling events received from workers. It forwards received events to the router queue.

         Parameters:
             event (Event): The received event.
             worker (Worker): Information about the worker that sent the event.
         """
        event._worker = worker.worker.name
        event._timing.stamp(self.__class__.__name__, "Returned from worker")
        self.router_queue.put(event)

    def resolve_callback_pipe(self, event: Event, pipe: Connection) -> None:
        """
         Handles events received from unknown pipes, which are not associated with known workers.

         Parameters:
             event (Event): The received event.
             pipe (Connection): The pipe from which the event was received.
         """
        self.logger.warning("Unknown event from unknown pipe: %s %s", event, pipe)  # pragma: no cover

    def resolve_unknown(self, event: Event) -> None:
        """
        Handles unknown events received from the router pipe that do not match any registered request or response.

        Parameters:
            event (Event): The unknown event received.
        """
        self.logger.warning("Unknown event: %s", event)  # pragma: no cover

    def _prepare(self) -> None:
        """
        Prepares the manager before starting the event resolver loop, initializing necessary attributes and structures.
        """
        self._workers = Storage()

    def _subscribe_static_resolvers(self) -> None:
        """
         Registers static resolver methods for specific event types, such as health checks and store get requests.
         """
        self.logger.debug("Registering static resolvers")
        self._requests[HealthCheck] = self.health_check
        self._requests[Restart] = self._restart
        self._store_get = self._responses.get(Get, None)
        self._responses[Get] = self.store_get

    def _find_stream(self, event: Event, stream: Optional[str] = None) -> Worker:
        """
        Locates a worker handling a specific event stream. This method searches through all available workers to find
        one that is handling the stream associated with the given event. If a specific stream identifier is provided,
        the method attempts to match the worker handling that exact stream. If no specific stream is provided, it looks
        for any worker that handles the event type of the provided event.

        Parameters:
            event (Event): The event for which to find the associated stream. This parameter is used to determine
                           the type of event and, optionally, its specific stream identifier.
            stream (Optional[str]): An optional specific stream identifier to match. If provided, the method
                                    will attempt to find a worker that handles not just the event type but also
                                    this specific stream.

        Returns:
            Worker: The worker instance handling the specified event stream. This worker is capable of processing
                    the event, considering both its type and, if specified, its stream identifier.

        Raises:
            ValueError: If no worker is found that matches the criteria (both event type and, if provided, the
                        specific stream identifier), a ValueError is raised. This exception indicates that there
                        are no available workers for the given event and stream combination.

        Note:
            This method logs debug information about the number of workers and their streams during the search
            process. If the event class does not match any worker's streams or if no worker is found for the
            specified stream, additional debug information is logged.

        Example:
            Given an event of a certain type and, optionally, a specific stream identifier, this method will iterate
            through all workers to find one that matches these criteria. If no match is found, it raises a ValueError.
        """
        self.logger.debug("Count of workers: %s", len(self._workers.values()))
        for worker in self._workers.values():
            if event.__class__ not in worker.streams:
                self.logger.debug("Count of streams: %s", len(worker.streams))
                continue
            if worker.streams[event.__class__] == stream or event._stream:
                return worker
        else:
            raise ValueError

    def _remove_worker(self, worker_key: str) -> None:
        """
        Removes a worker from the manager's tracking based on its unique identifier.

        Parameters:
            worker_key (str): The identifier of the worker to remove.
        """
        worker = self._workers[worker_key]
        worker.pipe.close()
        self._workers.pop(worker_key)

    def _restart(self, event: Restart) -> None:
        if event.manager == type(self):
            self.logger.warning("Restarting manager: %s", self.name)
            self.logger.debug("Reloading manager source code", )
            try:
                invalidate_caches()
                mod = import_module(self.__class__.__module__)
                mod = reload(mod)
            except Exception as e:
                self.logger.error("Unknown error during reloading of manager", exc_info=e)
                return

            try:
                klass_import = getattr(mod, self.__class__.__name__)
            except AttributeError as e:
                self.logger.error("Class %s not found", self.__class__.__name__, exc_info=e)
                return
            except Exception as e:
                self.logger.error("Unknown error during importing of manager", exc_info=e)
                return

            self.logger.info("Removing old subscription: %s", self.name)
            now = datetime.now()
            self._unsubscribe_all()
            self._resolve_undelivered_events()

            self.logger.info("Starting new manager: %s", self.name)
            klass_import(self.router_queue, from_time=now).start()

            self.router_pipe.close()
            self.router_queue.close()

            self.logger.warning("Stopping manager: %s", self.name)
            exit(0)

    def _find_worker(self, pipe: Connection) -> Tuple[str, Worker]:
        """
        Finds and returns the worker associated with a given pipe. This method iterates through all registered
        workers, comparing the given pipe with each worker's associated pipe. When it finds a match, it returns
        both the identifier of the worker and the worker instance itself.

        Parameters:
            pipe (Connection): The communication pipe to match with a worker. This is used to identify the specific
                               worker associated with the given communication channel.

        Returns:
            Tuple[str, Worker]: A tuple containing the worker's identifier and the worker instance itself. The
                                identifier is a unique string that represents the worker, and the Worker is the
                                actual instance handling tasks for a specific pipe.

        Raises:
            ValueError: Raised if no worker is found that matches the given pipe. This exception indicates that
                        the pipe provided does not correspond to any currently registered worker. It's crucial for
                        callers to handle this exception, especially in cases where dynamic registration and
                        deregistration of workers may lead to situations where a pipe is no longer valid.

        Example:
            To find a worker associated with a specific pipe, you would call this method with the pipe as the argument.
            If a worker is found that uses this pipe for communication, the method will return the worker's identifier
            and the worker instance. If no such worker exists, a ValueError will be raised.
        """
        for key, worker in self._workers.items():
            if worker.pipe == pipe:
                return key, worker
        else:
            raise ValueError

    def _resolve_callback_stream_close(self, event: StreamClose, worker: Worker) -> None:
        """
        Handles the closing of a stream, cleaning up any resources or references associated with the stream.

        Parameters:
            event (StreamClose): The event indicating a request to close a specific stream.
            worker (Worker): The worker instance associated with the stream being closed.
        """
        raise NotImplementedError("yet")
        # if len(worker.streams) == 1 and event.event is None:
        #     event, stream_key = worker.streams.popitem()
        #     stream_event = event()
        #     stream_event._stream = stream_key + STREAM_CLOSE_MARK
        # elif event.event:
        #     stream_key = worker.streams.pop(event.event.__class__)
        #     stream_event = event.event()
        #     stream_event._stream = stream_key + STREAM_CLOSE_MARK
        # else:
        #     self.logger.warning("Neočekávaný stav: %s", event)
        #     return
        #
        # request = self._requests.get(stream_event.__class__, None)
        # if not request:
        #     response = self._responses.get(stream_event.__class__, None)
        #     if not response:
        #         self.logger.error("Nelze určit typ zprávy pro ukončení streamu: %s", event)
        # else:
        #     response = Response(0)
        #     stream_event.set_response(response)
        #
        # self.router_queue.put(stream_event)

    def resolve(self, event: Event) -> None:
        """
        The central method for resolving events received by the manager. This method determines how an event
        is processed, whether it's an incoming request, a response to a previous request, or a system event like
        stream creation or closing.

        Parameters:
            event (Event): The event to be resolved by the manager.

        This method performs several key actions:
        - Determines if the event is part of a stream and routes it accordingly.
        - For non-stream events, it looks up the appropriate resolver based on whether the event is a request or response.
        - Executes the resolver, which may process the event immediately or forward it to a worker.
        - Handles unknown or unregistered events by either logging a warning or performing default actions.
        """
        if event._stream is not None:
            raise NotImplementedError("yet")
            # if not event.has_response():
            #     try:
            #         worker = self._find_stream(event)
            #         worker.pipe.send(event)
            #     except ValueError:
            #         if event._stream.endswith(STREAM_CLOSE_MARK):
            #             worker = self._find_stream(event, event._stream[:-len(STREAM_CLOSE_MARK)])
            #             worker.streams.pop(event.__class__)
            #             worker.pipe.send(event)
            #             self.logger.debug("Stream uzavřen: %s", event._stream)
            #             return
            #         resolver = self._requests.get(event.__class__, None)
            #         if not resolver:
            #             response = Response(1)
            #             event.response.set_status(ResponseStatus.FAILED)
            #             self.router_queue.put(event)
            #             return
            #         if ismethod(resolver):
            #             response = Response(2)
            #             event.set_response(response)
            #             self.router_queue.put(event)
            #             return
            #         worker = self._start_worker(event, resolver)
            #         worker.streams[event.__class__] = event._stream
            #         response = Response(0)
            #         event.set_response(response)
            #         self.router_queue.put(event)
            # else:
            #     try:
            #         worker = self._find_stream(event)
            #         worker.pipe.send(event)
            #     except ValueError:
            #         if event._stream.endswith(STREAM_CLOSE_MARK):
            #             worker = self._find_stream(event, event._stream[:-len(STREAM_CLOSE_MARK)])
            #             worker.streams.pop(event.__class__)
            #             worker.pipe.send(event)
            #             self.logger.debug("Stream uzavřen: %s", event._stream)
            #             return
            #         self.logger.warning("Neznámý stream")
        else:
            if not event.has_response():
                resolver = self._requests.get(event.__class__, None)
            else:
                resolver = self._responses.get(event.__class__, None)
            if resolver is None:
                self.resolve_unknown(event)
            else:
                had_response = event.has_response()
                resolver(event)
                if not had_response and event.has_response() and event.response._changed:
                    if event._switch:
                        event._switch.received = False
                    self.router_queue.put(event)

    def get_pipes(self) -> set[Connection]:
        """
        Collects all communication pipes used by the manager, including the router pipe and any worker pipes.

        Returns:
            set[Connection]: A set of all pipes for the manager to listen on.
        """
        pipes = set()
        if self.router_pipe:
            pipes.add(self.router_pipe)
        if self._workers:
            worker_pipes = set(worker.pipe for worker in self._workers.values())
            pipes.update(worker_pipes)
            self.logger.debug("Count of workers to listen to: %s", len(worker_pipes))
        pipes.update(self.additional_pipes)
        return pipes

    def run_resolver(self) -> Never:
        """
        Main event loop of the manager. Listens on all pipes for incoming events and resolves them appropriately.
        """
        while True:
            try:
                pipes = self.get_pipes()
                if not pipes:
                    sleep(1)
                    continue

                active_pipes: list[Connection] = wait(pipes, timeout=1)
                for active_pipe in active_pipes:
                    if active_pipe == self.router_pipe:
                        event: Event = self.router_pipe.recv()
                        self.logger.debug("Received event from router: %s", event)
                        event._timing.stamp(self.__class__.__name__, "Received")
                        try:
                            self.resolve(event)
                        except Exception as e:
                            self.logger.error("Error while resolving event", exc_info=e)
                            self._exceptions.append(
                                (event.__class__.__name__, event.as_dict(transform=False, keep_concealed=False), e, format_exc()))
                        else:
                            event._timing.stamp(self.__class__.__name__, "Resolved")
                    else:
                        try:
                            event = active_pipe.recv()
                            self.logger.debug("Received event: %s", event)
                        except EOFError as e:
                            self.logger.error("Communication problems", exc_info=e)
                            continue
                        except OSError as e:
                            self.logger.error("OS problems", exc_info=e)
                            continue
                        try:
                            key, worker = self._find_worker(active_pipe)
                            if isinstance(event, Manager):
                                # if isinstance(event, StreamCreate):
                                #     self._resolve_callback_stream_create(event, worker)
                                # elif isinstance(event, StreamMessage):
                                #     self._resolve_callback_stream_event(event, worker)
                                # elif isinstance(event, StreamClose):
                                #     self._resolve_callback_stream_close(event, worker)
                                if isinstance(event, WorkerQuit):
                                    self._remove_worker(key)
                            else:
                                self.resolve_callback_worker(event, worker)
                        except ValueError:
                            self.resolve_callback_pipe(event, active_pipe)

            except KeyboardInterrupt:
                return

    def start_worker(self, event: Optional[Event], resolver: Callable, *args, **kwargs) -> Worker:
        """
        Starts a new worker process or thread to handle an event based on the specified resolver.

        Parameters:
            event (Optional[Event]): The event that needs handling.
            resolver (Callable): The function or callable object that will handle the event.
            *args: Additional positional arguments passed to the resolver.
            **kwargs: Additional keyword arguments passed to the resolver.

        Returns:
            Worker: The newly started worker instance.
        """
        pipe_local, pipe_remote = Pipe()
        while True:
            name = f"{self.name}-Worker_{randint(10000, 99999)}"
            if not any(worker.worker.name == name for worker in self._workers.values()):
                break
        event = deepcopy(event)
        worker = Worker(pipe_local,
                        event,
                        resolver(pipe_remote, event, name, *args, **kwargs))
        worker.worker.name = name
        self._workers.append(worker)
        worker.worker.start()
        if isinstance(resolver, WorkerProcess):
            pipe_remote.close()
        self.logger.debug("Worker %s has been started", worker.worker.name)
        return worker

    def health_check(self, event: HealthCheck) -> None:
        """
        Responds to a health check request from the router, indicating the manager's status.

        Parameters:
            event (HealthCheck): The health check event received from the router.
        """
        event.response.name = self.name
        event.response.status = Status.WARNING if self._exceptions else Status.OK
        event.response.exceptions = self._exceptions
        self._exceptions = []

    def store_get(self, event: Get) -> None:
        """
        Handles the store get response for retrieving data from the Store. This method determines whether
        the response should be directed to a specific worker or handled by the manager itself.

        The method first checks if the event is associated with a worker. If the event's `_worker` attribute
        is set and matches a worker managed by this instance, the event is sent to that worker via its communication
        pipe. If no matching worker is found, or if the `_worker` attribute is not set, the method attempts to handle
        the event using the `_store_get` method, if it is defined.

        Parameters:
            event (Get): The get response event, containing details of the data to retrieve and the retrieved data.

        Behavior:
            - If the event specifies a worker (via the `_worker` attribute), the method directs the response to that worker.
            - If no worker is specified or found, the event is passed to the manager's own `_store_get` method for standard handling,
              provided that `_store_get` has been defined. If `_store_get` is not defined, the event is effectively ignored.

        Note:
            - The `_store_get` method is an optional user-defined method. If it is not defined, this method will not attempt to
              handle the event beyond checking for a worker.
        """
        if self._workers and event._worker is not None:
            for worker in self._workers.values():
                if worker.worker.name == event._worker:
                    worker.pipe.send(event)
                    return

        if self._store_get:
            self._store_get(event)

    def run(self) -> Never:
        """
        Main entry point for the manager process. Sets up event subscriptions, prepares the manager,
        and enters the main event resolution loop.
        """
        self.logger.debug(f"{self.name} is running!")
        self._prepare_resolvers()
        self._subscribe_static_resolvers()
        self._subscribe()
        self._prepare()
        self.after_start()
        self._resolve_undelivered_events()
        self.run_resolver()

    def start(self, router_queue: Optional[Queue] = None) -> None:
        """
        Starts the manager process with an optional router queue specified. This method initiates the manager's
        operation, allowing it to begin processing events. The router queue is a crucial component for communication
        between the manager and the router, facilitating the dispatch and handling of events.

        Parameters:
            router_queue (Optional[Queue[Event]]): The event queue used for communication with the router. If provided,
                                                   this queue will be set as the current router queue for the manager.
                                                   This queue is essential for the manager to receive and process events.

        Raises:
            RuntimeError: Raised if no router queue is provided and no router queue has been set previously. This
                          exception ensures that the manager cannot start without a means to communicate with the
                          router, as the lack of a router queue would prevent the manager from functioning correctly.

        Note:
            If a router queue is not provided as an argument to this method, the manager will attempt to use a
            previously set router queue. It's essential to either provide a router queue when calling this method
            or set one before its execution. Failure to do so will result in a RuntimeError, indicating the
            manager's inability to start due to the absence of a communication channel with the router.

        Example:
            To start the manager, you may either provide a router queue directly when calling the start method
            or ensure that the manager has a router queue set beforehand. This flexibility allows for different
            use cases, such as reusing an existing queue or setting a new one as needed.
        """
        if router_queue is not None:
            self.router_queue = router_queue
        if self.router_queue is None:
            raise RuntimeError("Queue must be specified")
        self.router_queue = self.router_queue
        super().start()

    def after_start(self) -> None:
        """
        Hook method called after the manager process starts. Can be overridden to perform initialization tasks.
        """
        pass

    def quit(self) -> None:
        self.router_queue.close()
        count = len(self._requests) + len(self._responses)
        if count > 0:
            self.router_pipe.close()
        for worker in self.workers:
            worker.worker.close()
