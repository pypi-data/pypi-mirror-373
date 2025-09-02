from contextlib import contextmanager
from logging import getLogger
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Optional, Type, Generic, TypeVar
from abc import abstractmethod, ABC

from edri.config.constant import STREAM_CLOSE_MARK
from edri.dataclass.event import Event
from edri.events.edri.manager import StreamCreate, StreamMessage, StreamClose
from edri.events.edri.manager.worker_quit import WorkerQuit

T = TypeVar("T", bound=Event)


class Worker(Generic[T], ABC):
    """
    A generic worker class designed to communicate with a manager through events. It supports sending and receiving events,
    creating event streams for continuous communication, and handling the lifecycle of these streams.

    Attributes:
        _name (str): The name of the worker, used for logging purposes.
        _manager_pipe (Connection): The communication pipe to the manager.
        event (EventType): The initial event associated with the worker.
        logger (Logger): Logger instance for logging messages.
        _buffer (List[Event]): A buffer for storing received events that are not yet processed.
        _stream_buffer (Optional[Event]): A buffer for the last received stream event.
        _stream_key (Optional[str]): The unique key identifying the current stream.

    Methods:
        __init__: Initializes a new Worker instance.
        do: Abstract method defining the main logic of the worker; to be implemented by subclasses.
        message_send: Sends a message to the manager.
        message_receive: Receives a message from the manager, blocking if no message is available.
        run: Entry point for the worker's execution, wrapping the `do` method with error handling and cleanup.
        stream_close: Closes the current message stream.
        stream_create: Initiates a stream for sending and receiving messages of a specific type.
        stream_exists: Checks if a message stream currently exists.
        stream_poll: Checks if there are messages available in the stream.
        stream_receive: Receives a message from the stream.
        stream_send: Sends a message through the stream.
        stream_wait: Waits for a message in the stream, with an optional timeout.
    """
    def __init__(self, pipe: Connection, event: T | None, name: str) -> None:
        """
        Initializes a new Worker instance.

        Parameters:
            pipe (Connection): The communication pipe to the manager.
            event (EventType): The initial event associated with this worker.
            name (str): A name for the worker, used for logging.
        """
        self._manager_pipe = pipe
        self._name = name
        self.event = event
        self.logger = getLogger(self._name)

        self._buffer: list[Event] = []
        self._stream_buffer: Event | None = None
        self._stream_key: str | None = getattr(self.event, "_stream", None)

    def event_send(self, event: Event) -> None:
        """
        Sends an event to the manager.

        Parameters:
            event (Event): The event to be sent.
        """
        event._timing.stamp(self.__class__.__name__, "Sent")
        self._manager_pipe.send(event)
        self.logger.debug("Event was sent: %s", event)

    def event_receive(self) -> Event:
        """
        Receives an event from the manager. This method blocks until an event is available.

        Returns:
            Event: The received event.
        """
        if self._buffer:
            return self._buffer.pop(0)
        while True:
            event: Event = self._manager_pipe.recv()
            event._timing.stamp(self.__class__.__name__, "Received")

            if isinstance(event, StreamClose):
                if self._stream_key == event._stream:
                    self._stream_key = None
                    self.logger.debug("Stream closed")
                else:
                    self.logger.warning("Wrong key for closing stream: %s", event._stream)
                continue

            return event

    def stream_create(self, event: Event) -> bool:
        """
        Initiates a event stream for continuous communication with the manager, or potentially other workers,
        using a specific type of event.

        Parameters:
            event (Event): The initial event for which the stream is to be created.

        Returns:
            bool: True if the stream was successfully created; False otherwise.
        """
        self.event_send(StreamCreate(event=event))
        reply = self.event_receive()
        if not isinstance(reply, StreamCreate) or reply._response._status:
            return False

        self._stream_key = reply._stream
        return True

    @property
    def stream_exists(self) -> bool:
        """
        Checks whether a event stream is currently active for this worker.

        Returns:
            bool: True if a stream exists; False otherwise.
        """
        return self._stream_key is not None

    def stream_poll(self) -> bool:
        """
        Non-blocking check to determine if there are events available in the current stream.

        Returns:
            bool: True if there is at least one event available in the stream; False otherwise.
        """
        if self._stream_buffer:
            return True
        while self._manager_pipe.poll():
            event = self._manager_pipe.recv()
            if event._stream:
                self._stream_buffer = event
                return True
            else:
                self._buffer.append(event)
        return False

    def stream_wait(self, timeout: Optional[int] = None) -> bool:
        """
         Waits for a event to be available in the stream, optionally with a timeout. This method is blocking
         and will pause execution until a event is received or the timeout is reached.

         Parameters:
             timeout (Optional[int]): The maximum time to wait for a event, in seconds. If None, waits indefinitely.

         Returns:
             bool: True if a event became available in the stream; False if the timeout was reached without receiving a event.
         """
        if self._stream_buffer:
            return True
        while self.stream_exists:
            if self._manager_pipe.poll(timeout) is not None:
                event = self._manager_pipe.recv()
                if event._stream is None:
                    self._buffer.append(event)
                elif event._stream.endswith(STREAM_CLOSE_MARK):
                    self.logger.debug("Stream closed on both ends: %s", event._stream[:-len(STREAM_CLOSE_MARK)])
                    self._stream_key = None
                    return False
                else:
                    self._stream_buffer = event
                    return True
        return False

    def stream_receive(self) -> Event:
        """
        Receives a event from the current stream. This method should be called after confirming that a event
        is available via `stream_poll` or `stream_wait`.

        Returns:
            Event: The next event from the stream.

        Raises:
            BlockingIOError: If called when no events are available in the stream.
        """
        if self._stream_buffer:
            event = self._stream_buffer
            self._stream_buffer = None
            return event
        else:
            raise BlockingIOError

    def stream_send(self, event: Event) -> None:
        """
        Sends a event through the current stream to the manager or another worker.

        Parameters:
            event (Event): The event to be sent through the stream.
        """
        stream_event = StreamMessage(event=event)
        self._manager_pipe.send(stream_event)

    def stream_close(self, event: Optional[Type[Event]] = None) -> bool:
        """
        Closes the current event stream, optionally sending a final event as part of the closure process.

        Parameters:
            event (Optional[Type[Event]]): The type of the final event to send before closing the stream, if any.

        Returns:
            bool: True if the stream was successfully closed; False if there was an issue closing the stream.
        """
        self.logger.debug("Closing the stream...")
        if not self._stream_key:
            self.logger.warning("Key was not provided")
            return False
        stream_close = StreamClose(event=event)
        stream_close._stream = self._stream_key
        self.event_send(stream_close)
        self.logger.debug("Stream closed: %s", self._stream_key)
        self._stream_key = None
        return True

    @contextmanager
    def stream(self, opener: Event):
        """
        `with worker.stream(opener_event) as send:`:
            send(msg)            # convenience wrapper
            ev = worker.stream_receive()
        """
        if not self.stream_create(opener):
            raise RuntimeError("manager refused to create stream")

        try:
            yield self.stream_send
        finally:
            self.stream_close()

    @staticmethod
    def _fix_environment():
        import site, sys, os

        exe = Path(sys.executable)
        venv_root = exe.parent.parent


        version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = venv_root / "lib" / version / "site-packages"

        # prepend new site-packages:
        prev = set(sys.path)
        site.addsitedir(str(site_packages))
        sys.path[:] = [p for p in sys.path if p not in prev] + list(prev)

        os.environ["VIRTUAL_ENV"] = str(venv_root.resolve())
        sys.real_prefix = sys.prefix
        sys.prefix = str(venv_root)

    @abstractmethod
    def do(self) -> None:
        """
        Abstract method that should be implemented by subclasses to define the worker's main logic.
        """
        pass

    def run(self) -> None:
        """
        The main entry point for the worker's execution. It calls the `do` method and handles any exceptions,
        ensuring proper cleanup and communication with the manager upon termination.
        """
        self._fix_environment()
        if self.event:
            self.event._timing.stamp(self.__class__.__name__, "Started")
        try:
            self.do()
        except Exception as e:
            self.logger.error("Worker %s was closed unexpectedly", self._name, exc_info=e)
        finally:
            worker_quit = WorkerQuit()
            self.event_send(worker_quit)
            self._manager_pipe.close()
