from collections import defaultdict
from logging import getLogger
from multiprocessing.connection import Connection
from multiprocessing.queues import Queue
from typing import Type, Optional, TYPE_CHECKING

from edri.dataclass.event import Event, shareable_events
from edri.dataclass.response import ResponseStatus
from edri.events.edri import router, group
from edri.events.edri.router import LastEvents
from edri.router import Cache, HealthChecker

if TYPE_CHECKING:
    from edri.abstract import ManagerBase


class Router:
    """
    Manages routing of events between components within the system, handling subscriptions
    to events, distributing events to subscribed components, and managing health checks.

    Attributes:
        queue (:class:`multiprocessing.Queue[Event]`): A queue for receiving events to be routed.
        logger (Logger): Logger instance for logging routing operations and outcomes.
        connections (Dict[str, Connection]): A dictionary mapping component names to their connections.
        subscribed_requests (Dict[Type[Event], Set[Connection]]): A dictionary mapping event types to sets
           of connections subscribed to those event types for requests.
        subscribed_responses (Dict[Type[Event], Set[Connection]]): Similar to subscribed_requests, but for responses.
        connector_pipe (Optional[Connection]): A special connection for the connector component, if any.
        cache (Cache): An instance of the Cache class for temporarily storing events.
        health_checker (HealthChecker): An instance of the HealthChecker class for monitoring component health.
    """

    def __init__(self, queue: Queue[Event], components: set["ManagerBase"]) -> None:
        """
        Initializes the Router with a queue for incoming events and a set of components to be monitored for health checks.

        :param queue: A queue for receiving events to be routed.
        :type queue: :class:`multiprocessing.queue.Queue`
        :param components: A set of components to be monitored for health checks.
        :type components: Set[:class:`edri.abstract.ManagerBase`]
        """
        super().__init__()
        self.queue: Queue[Event] = queue
        self.logger = getLogger(__name__)
        self.connections: dict[str, Connection] = {}
        self.subscribed_requests: dict[Type[Event], set[Connection]] = defaultdict(set)
        self.subscribed_responses: dict[Type[Event], set[Connection]] = defaultdict(set)
        self.connector_pipe: Optional[Connection] = None
        self.cache = Cache()
        self.health_checker = HealthChecker(self.queue, components)

    @staticmethod
    def _add_subscription(subscriptions: dict[Type[Event], set[Connection]], event_type: Type[Event], pipe: Connection) -> None:
        """
        Adds a subscription for a given event type and connection.

        :param subscriptions: A dictionary mapping event types to sets of connections.
        :type subscriptions: Dict[Type[Event], Set[Connection]]
        :param event_type: The event type to subscribe to.
        :type event_type: Type[Event]
        :param pipe: The connection associated with the subscription.
        :type pipe: Connection
        """
        if event_type in subscriptions:
            subscriptions[event_type].add(pipe)
        else:
            subscriptions[event_type] = {pipe}

    @staticmethod
    def _remove_subscription(subscriptions: dict[Type[Event], set[Connection]], event_type: Type[Event], pipe: Connection) -> None:
        """
        Removes a subscription for a given event type and connection.

        :param subscriptions: A dictionary mapping event types to sets of connections.
        :type subscriptions: Dict[Type[Event], Set[Connection]]
        :param event_type: The event type to unsubscribe from.
        :type event_type: Type[Event]
        :param pipe: The connection associated with the subscription to remove.
        :type pipe: Connection
        """
        if event_type in subscriptions:
            subscriptions[event_type].discard(pipe)

    def subscribe(self, event: router.Subscribe) -> Optional[Connection]:
        """
        Registers a component for receiving events of a specific type.

        :param event: The subscription event containing subscription details.
        :type event: :class:`edri.events.edri.router.Subscribe`
        :return: The connection associated with the component, or None if subscription failed.
        :rtype: Optional[:class:`multiprocessing.connection.Connection`]
        """
        # Every serialized object is different... this should enforce consistency
        saved_pipe = self.connections.get(event.name, None)
        if saved_pipe is not None:
            event.pipe = saved_pipe
        elif event.pipe is not None:
            self.connections[event.name] = event.pipe
        else:
            self.logger.error("Missing pipe in subscribe event!")
            return None

        if event.request:
            self._add_subscription(self.subscribed_requests, event.event_type, event.pipe)
        else:
            self._add_subscription(self.subscribed_responses, event.event_type, event.pipe)

        self.health_checker.component_add(event.name, event.pipe)
        if self.connector_pipe is not None:  # If switch connector is running, send him info about new request
            subscribed_new = router.SubscribedNew(event=event.event_type, request=event.request)
            self.connector_pipe.send(subscribed_new)

        event.response.set_status(ResponseStatus.OK)
        pipe = event.pipe
        event.pipe = None
        pipe.send(event)
        self.logger.debug("Subscribed for %s event: %s", event.name, event.event_type)
        return pipe

    def subscribed_external(self, event: router.SubscribedExternal):
        """
        Handles the SubscribedAll event, sending the connector component the current subscription details.

        :param event: The SubscribedAll event.
        :type event: router.SubscribedExternal
        """
        event.response.demands = router.Demands(
            requests=set(e for e in self.subscribed_requests.keys() if e in shareable_events),
            responses=set(e for e in self.subscribed_responses.keys() if e in shareable_events))
        if event.pipe:
            self.connector_pipe = event.pipe
        else:
            self.logger.warning("Missing pipe in subscribe event!")
        event.pipe = None
        self.connector_pipe.send(event)

    def subscribe_connector(self, event: router.SubscribeConnector) -> None:
        """
        Registers the connector component for receiving specific types of events.

        :param event: The SubscribeConnector event containing subscription details.
        :type event: router.SubscribeConnector
        """
        if not self.connector_pipe:
            self.logger.error("Connector component is not running!")
            return
        if event.event not in shareable_events:
            self.logger.warning("Event %s is not shareable!", event.event)
            return
        if event.request:
            self.subscribed_requests[event.event].add(self.connector_pipe)
        else:
            self.subscribed_responses[event.event].add(self.connector_pipe)

    def unsubscribe(self, event: router.Unsubscribe) -> None:
        """
        Removes a component's subscription for a specific event type.

        :param event: The Unsubscribe event containing unsubscription details.
        :type event: router.Unsubscribe
        """
        pipe = self.connections.get(event.name, None)
        if not pipe:
            self.logger.error("No pipe for name: %s", event.name)
            return

        self._remove_subscription(
            self.subscribed_requests if event.request else self.subscribed_responses,
            event.event_type,
            pipe
        )

        event.response.set_status(ResponseStatus.OK)
        pipe.send(event)

    def unsubscribe_all(self, event: router.UnsubscribeAll) -> None:
        """
        Removes a component's subscription for all event types.

        :param event: The Unsubscribe event containing unsubscription details.
        :type event: router.Unsubscribe
        """
        pipe = self.connections.pop(event.name, None)
        if not pipe:
            self.logger.error("No pipe for name: %s", event.name)
            return

        for subscriptions in self.subscribed_requests.values():
            subscriptions.discard(pipe)

        for subscriptions in self.subscribed_responses.values():
            subscriptions.discard(pipe)

        event.response.set_status(ResponseStatus.OK)
        pipe.send(event)
        pipe.close()

    def unsubscribe_pipe(self, pipe: Connection) -> None:
        """
        Removes all subscriptions associated with a given connection.

        :param pipe: The connection to remove subscriptions for.
        :type pipe: Connection
        """
        self.logger.warning("Removing subscription for this connection: %s", pipe)
        for manager, connection in self.connections.items():
            if connection == pipe:
                del self.connections[manager]
                break

        for event, subscribers in self.subscribed_requests.items():
            self.subscribed_requests[event] = {subscriber for subscriber in subscribers if subscriber != pipe}

        for event, subscribers in self.subscribed_responses.items():
            self.subscribed_responses[event] = {subscriber for subscriber in subscribers if subscriber != pipe}

    def last_events(self, event: LastEvents) -> None:
        """
        Handles the LastEvents event, sending the connector component the last cached events.

        :param event: The LastEvents event.
        :type event: LastEvents
        """
        event.response.last_events = self.cache.last_events()
        self.connector_pipe.send(event)

    def send_from(self, event: router.SendFrom) -> None:
        """
        Sends events from the cache to subscribed components based on specified criteria.

        :param event: The SendFrom event specifying which events to send.
        :type event: router.SendFrom
        """
        if event.key:
            cached_events = self.cache.events_from(event.key)
        else:
            cached_events = [item.event for item in self.cache.items]
        cached_events = [e for e in cached_events if e.__class__ in shareable_events]
        self.logger.debug("Sending cached events: %s", len(cached_events))
        for cache_event in cached_events:
            if not cache_event.has_response():
                if self.connector_pipe in self.subscribed_requests[cache_event.__class__]:
                    self.logger.debug("Sending to switch: %s", cache_event)
                    event.response.event = cache_event
                    self.connector_pipe.send(event)
            else:
                if self.connector_pipe in self.subscribed_responses[cache_event.__class__]:
                    self.logger.debug("Sending to switch: %s", cache_event)
                    event.response.event = cache_event
                    self.connector_pipe.send(event)

    def send(self, event: Event, connections: set[Connection]) -> None:
        """
        Distributes an event to all subscribed components.

        :param event: The event to distribute.
        :type event: :class:`edri.dataclass.event.Event`
        :param connections: The set of connections to send the event to.
        :type connections: Set[:class:`multiprocessing.connection.Connection`]
        """
        time = self.cache.append(event)
        if not connections:
            self.logger.info("Event without subscriber: %s", event)
            return

        for connection in connections:
            if event._switch and event._switch.received and self.connector_pipe == connection:
                self.logger.debug("Event discarded: %s", event)
                continue
            try:
                connection.send(event)
            except BrokenPipeError as e:
                self.logger.error("Broken pipe - %s", connection, exc_info=e)
                self.unsubscribe_pipe(connection)
                self.health_checker.restart_component(connection, time)

    def run(self) -> None:
        """
        Continuously processes incoming events, routing them according to subscriptions
        and managing system health checks.
        """
        self.logger.info("Router has started!")
        while True:
            event: Event = self.queue.get()
            event._timing.stamp(self.__class__.__name__, "Received")
            self.logger.debug("<- %s", event)
            if not event.has_response():
                if isinstance(event, group.Router):
                    if isinstance(event, router.Subscribe):
                        pipe = self.subscribe(event)
                        if not pipe:
                            continue
                        for undelivered_event in self.cache.find(event.event_type, True, event.from_time):
                            self.logger.debug("Sending cached events: %s", undelivered_event)
                            try:
                                pipe.send(undelivered_event)
                            except BrokenPipeError as e:
                                self.logger.error("Broken pipe - %s", pipe, exc_info=e)
                                self.unsubscribe_pipe(pipe)
                    elif isinstance(event, router.Unsubscribe):
                        self.unsubscribe(event)
                    elif isinstance(event, router.UnsubscribeAll):
                        self.unsubscribe_all(event)
                    elif isinstance(event, router.SubscribedExternal):
                        self.subscribed_external(event)
                    elif isinstance(event, router.SubscribeConnector):
                        self.subscribe_connector(event)
                    elif isinstance(event, router.LastEvents):
                        self.last_events(event)
                    elif isinstance(event, router.SendFrom):
                        self.send_from(event)
                    elif isinstance(event, router.HealthCheck):
                        self.health_checker.control_start()
                        self.send(event, self.subscribed_requests.get(event.__class__, set()))
                    elif isinstance(event, router.EdriHealth):
                        self.health_checker.send_status(event)
                    else:
                        self.logger.info("Unknown event: %s", event)
                else:
                    self.send(event, self.subscribed_requests[event.__class__])
            else:
                if isinstance(event, group.Router):
                    if isinstance(event, router.HealthCheck):
                        self.health_checker.control_result(event)
                    elif isinstance(event, router.EdriHealth):
                        self.send(event, self.subscribed_responses.get(event.__class__, set()))
                    else:
                        self.logger.info("Unknown Router event with response: %s", event)
                else:
                    self.send(event, self.subscribed_responses.get(event.__class__, set()))

    def quit(self) -> None:
        """
        Stops the router and performs necessary cleanup operations.
        """
        self.cache.quit()
