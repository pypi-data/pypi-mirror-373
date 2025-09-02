from sys import maxsize
from threading import Thread
from queue import Queue
from socket import SHUT_RDWR
from logging import getLogger
from uuid import UUID

from edri.config.constant import SWITCH_BYTES_LENGTH, SwitchMessages
from edri.switch.connection import Connection
from edri.switch.forwarder import ForwardType


class Receiver(Thread):
    def __init__(self, forwarder_queue: Queue[tuple[UUID, ForwardType, bytes]], router_id: UUID, connection: Connection,
                 connections: dict[UUID, Connection]) -> None:
        super(Receiver, self).__init__()
        self.forwarder_queue = forwarder_queue
        self.connection = connection
        self.connections = connections
        self.router_id = router_id
        self.logger = getLogger(f"{__name__}.{router_id}")

    def run(self) -> None:
        try:
            while True:
                try:
                    message_type_bytes = self.connection.socket.recv(SWITCH_BYTES_LENGTH)
                except ConnectionResetError as e:
                    self.logger.error("Router disconnected", exc_info=e)
                    return
                if not message_type_bytes:
                    self.connection.socket.shutdown(SHUT_RDWR)
                    self.logger.error("Router disconnected")
                    return
                try:
                    message_type = int.from_bytes(message_type_bytes, "big", signed=False)
                except ValueError:
                    self.logger.error("Unknown message from: %s", message_type_bytes)
                    return
                self.logger.debug("Received new message: %s", message_type)
                if message_type == SwitchMessages.NEW_DEMANDS:
                    self.logger.info("New demands")
                    demands_size_bytes = self.connection.socket.recv(SWITCH_BYTES_LENGTH)
                    demands_size = int.from_bytes(demands_size_bytes, "big", signed=False)

                    demands_bytes = b""
                    while len(demands_bytes) < demands_size:
                        chunk = self.connection.socket.recv(demands_size - len(demands_bytes))
                        if not chunk:
                            self.logger.error("Socket closed unexpectedly during message read")
                            return
                        demands_bytes += chunk
                    self.connections[self.router_id].demands = demands_bytes
                    self.forwarder_queue.put((self.router_id, ForwardType.OTHERS, demands_bytes))
                elif message_type == SwitchMessages.LAST_MESSAGES:
                    self.logger.debug("Last messages")
                    last_messages_size_bytes = self.connection.socket.recv(SWITCH_BYTES_LENGTH)
                    demands_size = int.from_bytes(last_messages_size_bytes, "big", signed=False)

                    last_messages_bytes = b""
                    while len(last_messages_bytes) < demands_size:
                        last_messages_bytes += self.connection.socket.recv(demands_size)
                    self.forwarder_queue.put((self.router_id, ForwardType.OTHERS, last_messages_bytes))

                else:
                    try:
                        receiver = UUID(bytes=message_type_bytes)
                    except ValueError as e:
                        self.logger.error("Cannot convert to UUID", exc_info=e)
                        return
                    message_size_bytes = self.connection.socket.recv(SWITCH_BYTES_LENGTH)
                    message_size = int.from_bytes(message_size_bytes, "big", signed=False)
                    self.logger.debug("Received message size: %s %s", receiver, message_size)
                    message = b""
                    while len(message) < message_size:
                        demands_size = message_size - len(message) if message_size - len(message) <= maxsize else maxsize
                        message += self.connection.socket.recv(demands_size)

                    self.logger.debug("Received message: %sb", len(message))
                    self.forwarder_queue.put((receiver, ForwardType.SPECIFIC, message))
        except Exception as e:
            self.logger.error("Neznámá chyba", exc_info=e)
