from dataclasses import dataclass, field
from multiprocessing.connection import Connection
from multiprocessing.process import BaseProcess
from threading import Thread
from typing import Type

from edri.dataclass.event import Event


@dataclass
class Worker:
    pipe: Connection
    event: Event | None
    worker: Thread | BaseProcess
    streams: dict[Type[Event], str] = field(default_factory=dict)
