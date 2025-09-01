from logging import getLogger
from pickle import dumps, loads
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, SOL_SOCKET, SO_KEEPALIVE, IPPROTO_TCP, TCP_KEEPIDLE, \
    TCP_KEEPINTVL, TCP_KEEPCNT
from time import sleep
from typing import Type
from uuid import UUID

from edri.config.constant import SWITCH_BYTES_LENGTH, SwitchMessages, SWITCH_MAX_SIZE
from edri.config.setting import SWITCH_HOST, SWITCH_PORT, CACHE_TIMEOUT
from edri.dataclass.event import Event
from edri.events.edri.router import Demands, LastEvents


class Socket:
    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        self.switch_socket: socket | None = None

    def reconnect(self) -> None:
        if self.switch_socket is not None:
            self.switch_socket.close()
        delay = 5
        while True:
            self.logger.debug("Connecting to switch on %s:%s", SWITCH_HOST, SWITCH_PORT)
            self.switch_socket = socket(AF_INET, SOCK_STREAM)
            self.switch_socket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
            self.switch_socket.setsockopt(IPPROTO_TCP, TCP_KEEPIDLE, 5)
            self.switch_socket.setsockopt(IPPROTO_TCP, TCP_KEEPINTVL, 5)
            self.switch_socket.setsockopt(IPPROTO_TCP, TCP_KEEPCNT, 3)
            try:
                self.switch_socket.settimeout(None)
                self.switch_socket.connect((SWITCH_HOST, SWITCH_PORT))
                delay = 5
                self.logger.info("Connected")
                break
            except ConnectionRefusedError as e:
                self.logger.warning("Connection failed - connection was refused", exc_info=e)
                sleep(delay)
            except TimeoutError as e:
                self.logger.warning("Connection failed - connection takes too long", exc_info=e)
                sleep(delay)
            except Exception as e:
                self.logger.warning("Connection failed - unknown error", exc_info=e)
                sleep(delay)
            delay = min(delay + 5, CACHE_TIMEOUT)

    def send_router_id(self, router_id: UUID) -> None:
        self.logger.debug("Sending router id to switch")
        self._send(router_id.bytes)

    def send_demands(self, router_id: UUID, requests: set[Type[Event]], responses: set[Type[Event]]) -> None:
        data = SwitchMessages.NEW_DEMANDS.to_bytes(SWITCH_BYTES_LENGTH, "big", signed=False)
        demands = Demands(
            router_id=router_id,
            requests=requests,
            responses=responses
        )
        self.logger.info("Sending demands to switch: %s", demands)
        local_messages_bytes = dumps(demands)
        data += len(local_messages_bytes).to_bytes(SWITCH_BYTES_LENGTH, "big", signed=False)
        data += local_messages_bytes
        self._send(data)

    def send_router(self, router_id: UUID, event: Event) -> None:
        self.logger.debug("Sending event to switch: %s", event)
        data = router_id.bytes
        message_bytes = dumps(event)
        data += len(message_bytes).to_bytes(SWITCH_BYTES_LENGTH, "big", signed=False)
        data += message_bytes
        self._send(data)

    def send_request_last_events(self, event: LastEvents) -> None:
        self.logger.info("Sending request for last events to remote routers")
        data = SwitchMessages.LAST_MESSAGES.to_bytes(SWITCH_BYTES_LENGTH, "big", signed=False)
        message_bytes = dumps(event)
        data += len(message_bytes).to_bytes(SWITCH_BYTES_LENGTH, "big", signed=False)
        data += message_bytes
        self._send(data)

    def _send(self, data: bytes) -> None:
        if len(data) > SWITCH_MAX_SIZE:
            self.logger.error("Message is too big")
            return
        self.logger.debug("Sending message to switch: %s %s", len(data), data[SWITCH_BYTES_LENGTH:SWITCH_BYTES_LENGTH * 2])
        self.switch_socket.send(data)

    def _load(self, amount: int) -> bytes | None:
        data = bytes()
        while len(data) < amount:
            data += self.switch_socket.recv(amount - len(data))
            if not data:
                return None
        return data

    def receive(self) -> Event | None:
        message_size_bytes = self._load(SWITCH_BYTES_LENGTH)
        if not message_size_bytes:
            self.switch_socket.shutdown(SHUT_RDWR)
            self.switch_socket.close()
            self.logger.error("Received no message size")
            raise ConnectionError
        message_size = int.from_bytes(message_size_bytes, "big", signed=False)
        self.logger.debug("Receiving size message: %s", message_size)
        message = self._load(message_size)
        try:
            event: Event = loads(message)
        except ModuleNotFoundError as e:
            self.logger.error("Event file was not found", exc_info=e)
        except AttributeError as e:
            self.logger.error("Event is not the same", exc_info=e)
        except Exception as e:
            self.logger.critical("Unknown error while loading Event", exc_info=e)
        else:
            self.logger.debug("Received: %s", event)
            return event

    def close(self) -> None:
        if self.switch_socket:
            self.switch_socket.shutdown(SHUT_RDWR)
            self.switch_socket.close()
