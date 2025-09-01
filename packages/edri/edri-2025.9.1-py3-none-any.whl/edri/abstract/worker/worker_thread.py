from abc import ABC
from multiprocessing.connection import Connection
from threading import Thread
from typing import TypeVar

from edri.dataclass.event import Event
from edri.abstract.worker import Worker

T = TypeVar('T', bound=Event)


class WorkerThread(Worker[T], Thread, ABC):
    """
    A WorkerThread class that combines the custom Worker class with threading
    capabilities, designed to run as a separate thread. This class is abstract
    and should be subclassed to implement specific worker behavior in a threaded
    environment.

    Attributes:
        Inherits all attributes from the Worker class and the Thread class.

    Methods:
        __init__(pipe: Connection, event, name: str): Initializes a new instance
        of the WorkerThread.

    Parameters:
        pipe (Connection): A connection object used for communication between
        threads. This should be an instance of multiprocessing.Connection,
        although it's used here in a threading context for inter-thread
        communication.
        event: The event type that the worker will handle. The specific type is
        determined by the EventType generic type variable, which should be
        defined in the subclass.
        name (str): A name for the thread. This is used internally by the
        threading module to identify the thread, especially useful for debugging
        and logging.

    Returns:
        None: The constructor initializes the thread but does not return a value.

    Raises:
        Inherits any exceptions raised by the Worker class or the Thread class
        constructors.

    Note:
        As this class is abstract, it cannot be instantiated directly. It requires
        subclassing and implementation of the abstract methods defined in the
        Worker class. This approach allows for the creation of specialized worker
        threads that can handle specific types of events or tasks in a multi-threaded
        application.
    """

    def __init__(self, pipe: Connection, event: T, name: str, *args, **kwargs) -> None:  # pragma: no cover
        Worker.__init__(self, pipe, event, name, *args, **kwargs)
        Thread.__init__(self)
