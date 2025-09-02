from threading import Thread
from queue import Queue
from socket import socket
from logging import getLogger
from uuid import UUID

from edri.config.constant import SWITCH_BYTES_LENGTH


class Sender(Thread):
    def __init__(self, connection_queue: Queue[bytes], connection: socket, router_id: UUID) -> None:
        super(Sender, self).__init__()
        self.connection_queue = connection_queue
        self.connection = connection
        self.logger = getLogger(f"{__name__}.{router_id}")
        self.router_id = router_id

    def run(self) -> None:
        while True:
            message = self.connection_queue.get()
            self.logger.debug("sending %s bytes",  len(message))
            message_size = len(message)
            try:
                self.connection.sendall(message_size.to_bytes(SWITCH_BYTES_LENGTH, "big", signed=False))
                self.connection.sendall(message)
            except BrokenPipeError:
                self.connection_queue.put(message)
                return
            except Exception:
                self.connection_queue.put(message)
                return
            self.logger.debug("send %s",  len(message))
