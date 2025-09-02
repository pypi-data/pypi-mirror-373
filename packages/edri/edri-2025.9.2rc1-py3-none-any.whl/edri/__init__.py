__all__ = ["EDRI"]

from json import JSONEncoder
from logging import getLogger
from multiprocessing import Queue
from typing import TYPE_CHECKING, Type
from uuid import UUID

from edri.api import Middleware
from edri.api.broker import Broker
from edri.api.handlers import HTMLHandler
from edri.api.listener import Listener
from edri.abstract import ManagerBase
from edri.config.setting import ENVIRONMENT
from edri.dataclass.event import Event
from edri.router import Router
from edri.router.connector import Connector
from edri.utility.manager import Store
from edri.utility.manager.scheduler import Scheduler, Job
from edri.utility.watcher import Watcher

if TYPE_CHECKING:
    from jinja2.ext import Extension
    from multiprocessing.queues import Queue


class EDRI:
    """
    The EDRI class serves as the main orchestrator for the system, initializing and managing
    the core components such as the router, scheduler, store, API, and connector. It provides
    methods to add components, start various services, and run the router.

    Attributes:
        router_queue (:class:`multiprocessing.Queue[Event]`): The queue used for routing events between components.
        components (set[:class:`edri.abstract.ManagerBase`]): A set of manager components that are part of the system.
        store (:class:`edri.utility.manager.Store`): The store component for data storage.
        scheduler (:class:`edri.utility.manager.scheduler.Scheduler`): The scheduler component for scheduling tasks.
        api (:class:`edri.api.listener.Listener`): The API listener component.
        broker (:class:`edri.api.broker.Broker`): The broker component for handling middleware.
        connector (:class:`edri.router.connector.Connector`): The connector component for connecting to external services.
        router (:class:`edri.router.Router`): The router component that routes events.
    """

    def __init__(self) -> None:
        """
        Initializes the EDRI instance, setting up the router queue and initializing component placeholders.
        """
        self.logger = getLogger(__name__)
        self.router_queue: Queue[Event] = Queue()
        self.components: set[ManagerBase] = set()
        self.store: Store
        self.scheduler: Scheduler
        self.api: Listener
        self.broker: Broker
        self.connector: Connector
        self.router: Router
        self.watcher: Watcher

    def add_component(self, component: ManagerBase) -> None:
        """
        Adds a component to the EDRI system.

        :param component: The component to be added.
        :type component: :class:`edri.abstract.ManagerBase`
        """
        self.components.add(component)

    def start_store(self) -> None:
        """
        Initializes and starts the store component.
        """
        self.store = Store(self.router_queue)
        self.store.start()

    def start_scheduler(self, jobs: list[Job] | None = None) -> None:
        """
        Initializes and starts the scheduler component with optional jobs.

        :param jobs: A list of jobs to schedule, defaults to an empty list if None.
        :type jobs: list[Job] | None
        """
        if not jobs:
            jobs = []
        self.scheduler = Scheduler(self.router_queue, jobs)
        self.scheduler.start()

    def start_broker(self, middlewares: list[Middleware]) -> None:
        """
        Initializes and starts the broker component with the provided middlewares.

        :param middlewares: A list of middleware instances.
        :type middlewares: list[Middleware]
        """
        if middlewares is None:
            middlewares = []

        self.broker = Broker(self.router_queue, Queue(), middlewares)
        self.broker.start()

    def start_api(self, middlewares: list[Middleware] | None = None, json_encoder: Type[JSONEncoder] | None = None, jinja_extensions: set[Type["Extension"]] | None = None) -> None:
        """
        Initializes and starts the API listener component with the provided middlewares.

        :param middlewares: A list of middleware instances, defaults to an empty list if None.
        :type middlewares: list[Middleware] | None
        """
        if middlewares is None:
            middlewares = []
        if not hasattr(self, "api_broker"):
            self.start_broker(middlewares=middlewares)
        else:
            self.broker.middlewares_request = [
                middleware for middleware in middlewares if middleware.is_request
            ]
            self.broker.middlewares_response = [
                middleware for middleware in middlewares if middleware.is_response
            ]

        if json_encoder is None:
            from edri.utility.json_encoder import CustomJSONEncoder
            json_encoder = CustomJSONEncoder

        if jinja_extensions is not None:
            HTMLHandler.configure_environment(list(jinja_extensions))

        self.api = Listener(self.broker.api_broker_queue, middlewares, json_encoder)
        self.api.start()

    def start_connector(self, router_id: UUID | None = None) -> None:
        """
        Initializes and starts the connector component with an optional router ID.

        :param router_id: The UUID of the router, defaults to None.
        :type router_id: UUID | None
        """
        self.connector = Connector(self.router_queue, router_id)
        self.connector.start()

    def start_watcher(self):
        self.watcher = Watcher(self.router_queue, self.components)

    def run(self) -> None:
        """
        Runs the router and all added components, handling graceful shutdown on KeyboardInterrupt.
        """
        self.logger.debug("Running EDRI in %s environment", ENVIRONMENT)
        self.router = Router(self.router_queue, self.components)

        for component in self.components:
            component.start(self.router_queue)
        try:
            self.router.run()
        except KeyboardInterrupt:
            self.router.quit()
            for component in self.components:
                component.quit()
            if hasattr(self, "watcher") and self.watcher:
                self.watcher.quit()
            if hasattr(self, "connector") and self.connector:
                self.connector.quit()
