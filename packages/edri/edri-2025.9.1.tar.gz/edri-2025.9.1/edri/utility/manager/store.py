from dataclasses import dataclass
from logging import getLogger
from multiprocessing import Queue
from typing import Any, Callable

from edri.dataclass.event import Event
from edri.abstract import ManagerBase
from edri.events.edri.store import Set, Get, Delete, GetCallback


@dataclass
class Callback:
    condition: Callable[[Any], bool] | None


class Store(ManagerBase):
    """
    A simple key-value store that processes set and get requests for storing and retrieving
    data, respectively. Inherits from ManagerBase to integrate with the system's event-driven
    architecture.

    Attributes:
        router_queue (Queue): The messaging queue for receiving and sending events.
        store (Dict[str, Any]): A dictionary acting as the internal store for key-value pairs.
        logger (Logger): Logger instance for logging operations within the Store.

    Methods:
        solve_req_set(event: Set): Handles requests to set (store) a value associated with a key.
        solve_req_get(event: Get): Handles requests to get (retrieve) a value by its key.
    """
    def __init__(self, router_queue: "Queue[Event]") -> None:
        """
        Initializes the Store with a router queue for communication and an empty dictionary
        for storing key-value pairs.

        Parameters:
            router_queue (Queue): The messaging queue for communicating with other system components.
        """
        super().__init__(router_queue, getLogger(__name__))
        self.store: dict[str, Any] = {}
        self.callbacks: dict[str, list[Callback]] = {}

    def solve_req_set(self, event: Set) -> None:
        """
        Processes a set request by storing the provided value associated with the specified key
        in the internal store.

        Parameters:
            event (Set): The event containing the key (name) and the value to be stored.
        """
        self.store[event.name] = event.value
        self.logger.debug("Value set for key '%s': %s", event.name, event.value)

        for callback in self.callbacks.get(event.name, []):
            if callback.condition is None or callback.condition(event.value):
                event_callback = GetCallback(name=event.name)
                event_callback.response.value = event.value
                self.router_queue.put(event_callback)
                self.logger.debug("Sending callback item for '%s'", event.name)

    def solve_req_get(self, event: Get) -> None:
        """
        Processes a get request by retrieving the value associated with the specified key from
        the internal store. If the key does not exist, None is returned.

        Parameters:
            event (Get): The event containing the key (name) for which the value is requested.
        """
        event.response.value = self.store.get(event.name, None)
        if event.response.value is not None:
            self.logger.debug("Value retrieved for key '%s': %s", event.name, event.response.value)
        else:
            self.logger.debug("No value found for key '%s'", event.name)

    def solve_req_delete(self, event: Delete) -> None:
        """
        Processes a delete request by removing the specified key and its associated value
        from the internal store. If the key does not exist, no action is taken.

        Parameters:
            event (Delete): The event containing the key (name) of the item to be deleted.
        """
        if event.name in self.store:
            del self.store[event.name]
            self.logger.debug("Deleted item with key '%s'", event.name)
        else:
            self.logger.debug("Attempted to delete non-existent key '%s'", event.name)

    def solve_req_get_callback(self, event: GetCallback) -> None:
        callbacks = self.callbacks.get(event.name, [])
        callbacks.append(Callback(event.condition))
        self.callbacks[event.name] = callbacks
        self.logger.debug("Callback added for key '%s'", event.name)
