from dataclasses import dataclass, field
from multiprocessing import Process
from multiprocessing.connection import Connection
from threading import Thread
from typing import Type

from edri.dataclass.event import Event


@dataclass
class Worker:
    pipe: Connection
    event: Event | None
    worker: Thread | Process
    streams: dict[Type[Event], str] = field(default_factory=dict)
