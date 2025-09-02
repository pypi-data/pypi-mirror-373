from collections import defaultdict
from logging import getLogger
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from multiprocessing.queues import Queue as MPQueue
from threading import Thread
from time import sleep
from typing import Type
from uuid import UUID, uuid1

from edri.config.setting import CACHE_TIMEOUT
from edri.dataclass.event import Event, SwitchInfo
from edri.events.edri.router import SubscribeConnector, SubscribedExternal, SubscribedNew, SendFrom, LastEvents, Demands
from edri.router.connector import Socket
from edri.utility.queue import Queue


class Connector(Process):
    def __init__(self, router_queue: MPQueue[Event], router_id: UUID | None = None) -> None:
        super(Connector, self).__init__()
        self.router_queue = router_queue
        self.local_requests: set[Type[Event]] = set()
        self.local_responses: set[Type[Event]] = set()
        self.remote_request: dict[Type[Event], set[UUID]] = defaultdict(set)
        self.remote_response: dict[Type[Event], set[UUID]] = defaultdict(set)
        self.logger = getLogger(__name__)
        self.router_pipe: Connection | None = None

        self.sender_queue: Queue[tuple[Event | False, UUID | None]] | None = None
        self.sender_thread: Thread | None = None
        self.receiver_thread: Thread | None = None

        if router_id is not None:
            self.router_id = router_id
        else:
            self.router_id = uuid1(clock_seq=0)
        if CACHE_TIMEOUT < 10:
            raise ValueError("CACHE_TIMEOUT must be greater than 10s")
        self.socket: Socket | None = None

    def sender(self) -> None:
        while True:
            event, router_id = self.sender_queue.get()
            if event is False:
                break
            event._switch = SwitchInfo(router_id=self.router_id)
            self.logger.debug("Sender sending event type: %s", event.__class__)
            if router_id:
                try:
                    self.socket.send_router(router_id, event)
                except BrokenPipeError as e:
                    self.logger.warning("Event cannot be send: %s", event, exc_info=e)
                    self.sender_queue.unget((event, router_id))
                    self.socket.reconnect()
                    return
            if not event.has_response():
                router_id_list = self.remote_request[event.__class__]
            else:
                router_id_list = self.remote_response[event.__class__]
            for router_id in router_id_list:
                try:
                    self.socket.send_router(router_id, event)
                except BrokenPipeError as e:
                    self.logger.warning("Event cannot be send: %s", event, exc_info=e)
                    self.sender_queue.unget((event, None))
                    self.socket.reconnect()
                    return

        self.logger.error("Sender se ukončil")

    def receiver(self) -> None:
        while True:
            event = self.socket.receive()
            if not event:
                self.logger.warning("Received no Event!")
                continue
            self.logger.debug("New event: %s", event)
            if isinstance(event, Demands):
                self.logger.info("New event with demands from remote router: %s", event.router_id)
                self.logger.debug("Demands - requests: %s responses: %s", event.requests, event.responses)
                for demand in event.requests:
                    self.remote_request[demand].add(event.router_id)
                    subscribe = SubscribeConnector(event=demand, request=True)
                    self.router_queue.put(subscribe)

                for demand in event.responses:
                    self.remote_response[demand].add(event.router_id)
                    subscribe = SubscribeConnector(event=demand, request=False)
                    self.router_queue.put(subscribe)
            elif isinstance(event, LastEvents):
                self.logger.debug("Request for cached events from remote router: %s", event.router_id)
                last_event = event.response.last_events.get(self.router_id, None)
                if last_event:
                    self.router_queue.put(SendFrom(router_id=event.router_id, key=last_event))
                else:
                    self.router_queue.put(SendFrom(router_id=event.router_id))
            else:
                if event._switch is None:
                    self.logger.warning("Event has no switch information: %s", event)
                    continue
                event._switch.received = True
                self.logger.info("-> Router %s", event)
                self.router_queue.put(event)


    def request_last_events(self) -> None:
        self.router_queue.put(LastEvents(self.router_id))

    def send_basic_info(self) -> None:
        self.logger.debug("Sending information to switch")
        self.socket.send_router_id(self.router_id)
        self.socket.send_demands(self.router_id, self.local_requests, self.local_responses)
        self.request_last_events()

    def run(self) -> None:
        sleep(5)
        self.logger.debug(f"SwitchConnector is running!")
        self.logger.info("Router ID: %s", self.router_id)
        self.socket = Socket()
        self.socket.reconnect()
        self.router_pipe, pipe = Pipe(duplex=False)
        subscribe_connector = SubscribedExternal(pipe=pipe)
        self.router_queue.put(subscribe_connector)
        while True:
            event = self.router_pipe.recv()
            if isinstance(event, SubscribedExternal):
                self.logger.debug("Received %s events from router", len(event.response.demands.requests) + len(event.response.demands.responses))
                self.local_requests = event.response.demands.requests
                self.local_responses = event.response.demands.responses
                break
            else:
                self.logger.error("Unexpected event: %s", event)
        pipe.close()

        self.send_basic_info()

        self.receiver_thread = Thread(target=self.receiver)
        self.receiver_thread.start()

        self.sender_queue = Queue()
        self.sender_thread = Thread(target=self.sender)
        self.sender_thread.start()

        while True:
            if self.router_pipe.poll(timeout=5):
                event = self.router_pipe.recv()
                self.logger.debug("<- Router - %s", event)
                if isinstance(event, SubscribedNew):
                    if event.request:
                        self.local_requests.add(event.event)
                    else:
                        self.local_responses.add(event.event)
                    self.socket.send_demands(self.router_id, self.local_requests, self.local_responses)
                elif isinstance(event, LastEvents):
                    self.socket.send_request_last_events(event)
                elif isinstance(event, SendFrom):
                    self.sender_queue.put((event.response.event, event.router_id))
                else:
                    self.sender_queue.put((event, None))
            if not self.receiver_thread.is_alive():
                self.logger.error("Receiver was shut down")
                self.sender_queue.put((False, None))
                self.sender_thread.join()
                self.socket.reconnect()
                self.send_basic_info()
                self.receiver_thread = Thread(target=self.receiver)
                self.receiver_thread.start()

                self.sender_thread = Thread(target=self.sender)
                self.sender_thread.start()

    def quit(self) -> None:
        if self.sender_queue:
            self.sender_queue.put((False, None))
        self.socket.close()
