from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from multiprocessing.connection import Connection
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from edri.abstract import ManagerBase


class Status(Enum):
    OK = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass
class Record:
    """
    Represents the health status of a system component.

    Attributes:
        name (str):
            The name of the component.
        pipe (Optional[Connection]):
            A connection object used for inter-process communication with the component.
            Defaults to None if not applicable.
        definition (Optional[ManagerBase]):
            The class definition of the component, if available, providing metadata or
            configuration details.
        timestamp (datetime):
            The timestamp of the last recorded health check. Defaults to the current time.
        status (Status):
            The current health status of the component, represented by a `Status` enum.
            Defaults to `Status.WARNING`.
        exceptions (list[tuple[str, dict, Exception, str]]):
            A list of recorded exceptions related to the component. Each entry is a tuple
            containing:
                - A string identifier for the error.
                - A dictionary with relevant context data.
                - The actual exception object.
                - A string message or traceback describing the issue.
    """
    name: str
    pipe: Connection | None = None
    definition: Optional["ManagerBase"] = None
    timestamp: datetime = datetime.now()
    status: Status = Status.WARNING
    exceptions: list[tuple[str, dict, Exception, str]] = field(default_factory=list)
