from abc import ABC
from multiprocessing import Process
from multiprocessing.connection import Connection
from typing import TypeVar

from edri.dataclass.event import Event
from edri.abstract.worker import Worker

T = TypeVar('T', bound=Event)


class WorkerProcess(Worker[T], Process, ABC):
    """
    A WorkerProcess class that integrates functionality from a custom Worker
    class with multiprocessing capabilities, designed to run as a separate
    process. This class is abstract and should be subclassed to implement
    specific worker behavior in a multiprocessing environment.

    Attributes:
        Inherits all attributes from the Worker class and the Process class.

    Methods:
        __init__(pipe: Connection, event, name: str): Initializes a new instance
        of the WorkerProcess.

    Parameters:
        pipe (Connection): A connection object used for communication between
        processes. This should be an instance of multiprocessing.Connection.
        event: The event type that the worker will handle. The specific type is
        determined by the EventType generic type variable, which should be
        defined in the subclass.
        name (str): A name for the process. This is used internally by the
        multiprocessing module to identify the process, especially useful for
        debugging.

    Returns:
        None: The constructor initializes the process but does not return a value.

    Raises:
        Inherits any exceptions raised by the Worker class or the Process class
        constructors.

    Note:
        As this class is abstract, it cannot be instantiated directly. It requires
        subclassing and implementation of the abstract methods defined in the
        Worker class.
    """

    def __init__(self, pipe: Connection, event, name: str, *args, **kwargs) -> None:  # pragma: no cover
        Worker.__init__(self, pipe, event, name, *args, **kwargs)
        Process.__init__(self)
