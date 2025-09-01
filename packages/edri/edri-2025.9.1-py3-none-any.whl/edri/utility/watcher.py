from dataclasses import dataclass
from inspect import getfile
from logging import Logger, getLogger
from multiprocessing import Queue
from threading import Timer
from typing import Type

from watchdog.events import FileSystemEventHandler, FileModifiedEvent, DirModifiedEvent
from watchdog.observers import Observer

from edri.abstract import ManagerBase
from edri.config.setting import ENVIRONMENT
from edri.events.edri.manager import Restart


@dataclass
class WatcherHandlerComponent:
    """
    Data container for a file-watched component.

    Attributes:
        type (Type[ManagerBase]): The manager class associated with the watched file.
        timer (Timer | None): Timer used to delay the restart event for the component.
    """
    type: Type[ManagerBase]
    timer: Timer | None = None


class WatcherHandler(FileSystemEventHandler):
    """
    Handles filesystem events and queues restart events for changed components.

    Attributes:
        router_queue (Queue): Queue to communicate with the router by sending Restart events.
        components (dict[str, WatcherHandlerComponent]): Maps file paths to their associated component handlers.
        logger (Logger): Logger for debug and info messages.
        delay (int): Delay in seconds before sending a restart event after modification.
    """

    def __init__(self, components: dict[str, Type[ManagerBase]], router_queue: Queue, logger: Logger):
        """
        Initializes the WatcherHandler.

        Args:
            components (dict[str, Type[ManagerBase]]): Mapping of file paths to component classes.
            router_queue (Queue): Queue to send restart events to.
            logger (Logger): Logger instance for logging.
        """
        self.router_queue = router_queue
        self.components: dict[str, WatcherHandlerComponent] = {
            path: WatcherHandlerComponent(component) for path, component in components.items()
        }
        self.logger = logger
        self.delay = 1 if ENVIRONMENT == "development" else 10

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        """
        Called when a file or directory is modified.

        Args:
            event (FileModifiedEvent | DirModifiedEvent): The filesystem event.
        """
        if isinstance(event, FileModifiedEvent):
            component = self.components[event.src_path]
            self.logger.debug("Manager %s was changed", component.type.__name__)
            if component.timer is not None:
                self.logger.debug("Resetting timer: %s", component.type.__name__)
                component.timer.cancel()
            component.timer = Timer(self.delay, self._send_restart_event, args=(component.type,))
            component.timer.start()

    def _send_restart_event(self, manager_type: Type[ManagerBase]):
        """
        Sends a restart event to the router queue for the specified manager type.

        Args:
            manager_type (Type[ManagerBase]): The manager class to restart.
        """
        self.logger.info("Restart event queued for manager: %s", manager_type.__name__)
        restart = Restart(manager=manager_type)
        self.router_queue.put(restart)

    def quit(self):
        """
        Cancels any running timers for the components.
        """
        for component in self.components.values():
            if component.timer:
                component.timer.cancel()


class Watcher:
    """
    Observes filesystem changes and triggers restarts for modified components.

    Attributes:
        router_queue (Queue): Queue to send restart events to.
        logger (Logger): Logger for this watcher.
        observer (Observer): Watchdog observer monitoring file changes.
    """

    def __init__(self, router_queue: Queue, components: set[ManagerBase]) -> None:
        """
        Initializes the Watcher and starts observing specified components.

        Args:
            router_queue (Queue): Queue to send restart events.
            components (set[ManagerBase]): Set of manager instances to watch.
        """
        self.router_queue = router_queue
        self.logger = getLogger(__name__)
        self.observer = Observer()
        components = {getfile(component.__class__): component.__class__ for component in components}
        handler = WatcherHandler(components, self.router_queue, self.logger)
        for path in components.keys():
            self.observer.schedule(handler, path)
        self.observer.start()

    def quit(self) -> None:
        """
        Stops the observer and quits watching.
        """
        self.observer.stop()
