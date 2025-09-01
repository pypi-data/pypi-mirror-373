from enum import IntEnum
from logging import getLogger
from threading import Thread
from typing import Dict
from queue import Queue
from uuid import UUID

from edri.switch.connection import Connection


class ForwardType(IntEnum):
    SPECIFIC = 1
    OTHERS = 2


class Forwarder(Thread):
    def __init__(self, forwarder_queue: Queue[tuple[UUID, ForwardType, bytes]], connections: Dict[UUID, Connection]) -> None:
        super(Forwarder, self).__init__()
        self.forwarder_queue = forwarder_queue
        self.connections = connections
        self.logger = getLogger(__name__)

    def run(self) -> None:
        while True:
            router_id, forward_type, message = self.forwarder_queue.get()
            try:
                connection = self.connections[router_id]
            except KeyError as e:
                self.logger.error("Unknown router id: %s", router_id, exc_info=e)
                continue
            if forward_type == ForwardType.SPECIFIC:
                self.logger.debug("Forwarding to %s", router_id)
                connection.queue.put(message)
            elif forward_type == ForwardType.OTHERS:
                for connection_router_id, connection in self.connections.items():
                    if connection_router_id != router_id:
                        self.logger.debug("Forwarding to %s", connection_router_id)
                        connection.queue.put(message)
