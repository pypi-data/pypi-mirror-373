from multiprocessing.connection import Connection
from dataclasses import dataclass

from edri.config.constant import ApiType


@dataclass(frozen=True, eq=True)
class Client:
    socket: Connection
    type: ApiType
