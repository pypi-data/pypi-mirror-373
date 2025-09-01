from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from logging import getLogger, DEBUG, StreamHandler
from typing import Dict
from uuid import UUID

from edri.config.constant import SWITCH_BYTES_LENGTH
from edri.switch.connection import Connection
from edri.switch import Forwarder, Receiver, Sender
from edri.config.setting import SWITCH_HOST, SWITCH_PORT
from edri.switch.forwarder import ForwardType
from edri.utility.queue import Queue


class Switch:
    def __init__(self) -> None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.logger = getLogger(__name__)
        self.connections: Dict[UUID, Connection] = {}
        self.forwarder_queue = Queue[tuple[UUID, ForwardType, bytes]]()
        self.forwarder: Forwarder = Forwarder(self.forwarder_queue, self.connections)
        self.forwarder.start()

    def handle_new_connection(self, connection_socket: socket) -> None:
        router_id_bytes = b''
        while len(router_id_bytes) < SWITCH_BYTES_LENGTH:
            chunk = connection_socket.recv(SWITCH_BYTES_LENGTH - len(router_id_bytes))
            if not chunk:
                raise ConnectionError("Socket closed before receiving enough bytes")
            router_id_bytes += chunk
        try:
            router_id = UUID(bytes=router_id_bytes)
        except ValueError:
            connection_socket.close()
            return
        connection = self.connections.get(router_id, None)
        self.logger.info("New connection: %s %s", router_id, connection_socket.getpeername())
        if connection is not None:
            self.logger.info("Resuming connection: %s", router_id)
            connection.socket = connection_socket
            receiver = Receiver(self.forwarder_queue, router_id, connection, self.connections)
            receiver.start()
            sender = Sender(connection.queue, connection_socket, router_id)
            sender.start()
        else:
            self.logger.info("No previous connection found: %s", router_id)
            connection = Connection(Queue(), connection_socket)
            self.connections[router_id] = connection
            receiver = Receiver(self.forwarder_queue, router_id, connection, self.connections)
            receiver.start()
            sender = Sender(connection.queue, connection_socket, router_id)
            sender.start()
        self.logger.debug("Receiver and sender started for %s", router_id)
        for other_router_id, other_connection in self.connections.items():
            if other_router_id != router_id:
                self.logger.debug("Sending demands of: %s", other_router_id)
                connection.queue.put(other_connection.demands)

    def run(self) -> None:
        self.logger.info("Starting switch on %s:%s", SWITCH_HOST, SWITCH_PORT)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((SWITCH_HOST, SWITCH_PORT))
        self.socket.listen()
        self.logger.info("Ready for new connections")
        while True:
            connection, address = self.socket.accept()
            self.logger.debug("New incoming connection: %s", address)
            self.handle_new_connection(connection)


if __name__ == "__main__":
    stream_handler = StreamHandler()
    logger = getLogger()
    logger.setLevel(DEBUG)
    logger.addHandler(stream_handler)
    switch = Switch()
    switch.run()
