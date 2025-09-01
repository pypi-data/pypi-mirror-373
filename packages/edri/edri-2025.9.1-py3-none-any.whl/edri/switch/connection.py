from dataclasses import dataclass
from queue import Queue
from socket import socket


@dataclass
class Connection:
    queue: Queue[bytes]
    socket: socket
    demands: bytes | None = None
