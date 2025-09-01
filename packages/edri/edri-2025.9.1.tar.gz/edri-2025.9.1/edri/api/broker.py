from collections import defaultdict
from dataclasses import dataclass, fields, MISSING
from logging import getLogger
from multiprocessing.connection import wait, Connection
from multiprocessing.queues import Queue
from re import findall
from typing import Any, DefaultDict, Type, Never

from edri.abstract.manager.manager_base import ManagerBase
from edri.api.dataclass import Client
from edri.api.dataclass.api_event import api_events, ApiEvent, Header, Cookie, Scope
from edri.api.middleware import Middleware, MiddlewareControl
from edri.config.constant import ApiType
from edri.dataclass.directive.base import InternalServerErrorResponseDirective
from edri.dataclass.event import Event, EventHandlingType, ApiInfo
from edri.dataclass.injection import Injection
from edri.dataclass.response import ResponseStatus, Response
from edri.events.api import group, manage, client
from edri.events.edri.router import HealthCheck, Subscribe
from edri.utility import Storage
from edri.utility.validation import StringValidation, IntegerValidation, FloatValidation, DateValidation, TimeValidation, DateTimeValidation


class TrieNode:
    def __init__(self, key=None):
        self.key = key
        self.children: dict[tuple[str, Any], TrieNode] = {}
        self.is_end: bool = False
        self.clients: set[Client] = set()

    def __repr__(self) -> str:
        """
        Returns a tree-like string representation of the trie starting from this node.

        Returns:
            str: String representation of the trie starting from this node.
        """
        return self._build_repr(level=0)

    def _build_repr(self, level: int = 0, max_depth: int | None = None, max_children: int | None = None) -> str:
        """
        Recursively builds the string representation of the trie.

        Parameters:
            level (int): Current depth level in the trie.
            max_depth (int | None): Maximum depth to traverse for the representation.
            max_children (int | None): Maximum number of children to display per node.

        Returns:
            str: String representation of the trie starting from this node.
        """
        indent = "    " * level
        node_label = f"TrieNode(key={self.key}, is_end={self.is_end}, clients={len(self.clients)})"
        representation = f"{indent}{node_label}\n"

        if max_depth is not None and level >= max_depth:
            return representation

        children_keys = sorted(self.children.keys())
        displayed_children = children_keys
        if max_children is not None and len(children_keys) > max_children:
            displayed_children = children_keys[:max_children] + ['...']

        for child_key in displayed_children:
            if child_key == '...':
                representation += f"{indent}    ...\n"
                break
            child_node = self.children[child_key]
            representation += child_node._build_repr(level=level + 1, max_depth=max_depth, max_children=max_children)

        return representation


@dataclass
class EventInfo:
    resource: str
    handling_type: EventHandlingType


class Broker(ManagerBase):
    """
    The ApiBroker class acts as an intermediary between the central router and all API handlers,
    managing client registrations, event dispatching, and communication in a multiprocessing
    environment. It extends ManagerBase to leverage common management functionalities and
    adds capabilities specific to API interactions.

    Attributes:
        api_broker_queue (Queue): A multiprocessing queue used to receive events specifically for the API broker.
        clients (Optional[Storage[Client]]): A storage mechanism for registered clients, allowing for quick access and management.
        db: Placeholder attribute for potential database connections or operations, not implemented by default.
        events (dict): A mapping of event resources to event classes, derived from the global api_events definition.
        middlewares_request (list[Middleware]): List of middlewares applied to incoming requests.
        middlewares_response (list[Middleware]): List of middlewares applied to outgoing responses.

    Methods:
        __init__(router_queue: "Queue[Event]", api_broker_queue: "Queue[Event]", middlewares: list[Middleware]):
            Constructor for the ApiBroker class.
        name (property): Returns the name of the ApiBroker instance.
        send_specific(event: Event): Sends an event to a specific client based on the event's key.
        send_all(event: Event): Broadcasts an event to all clients of a specific API type.
        client_register(event: client.Register): Registers a new client and sends a confirmation event.
        client_unregister(event: Event): Unregisters a client based on the event's key.
        event_register(event: manage.Register): Registers a client for specific events and parameters.
        solve(event: Event): Determines the appropriate method to handle an incoming event.
        _prepare(): Prepares the ApiBroker for operation by initializing storage for clients.
        additional_pipes (property): Returns a set of additional pipes to monitor for incoming events.
        run_resolver(): Main loop for processing incoming events and dispatching them to the appropriate handlers.
        resolve_callback(event: Event, pipe: Connection): Callback method for handling events received from clients.
        _prepare_resolvers(): Prepares resolvers for handling specific types of events.
        resolve(event: Event): Processes an event through the appropriate middlewares and forwards it to its destination.

    Usage:
        This class is instantiated with specific queues and is used within a multiprocessing
        application to manage communications between the router and API handlers. It handles
        client registrations, event dispatching, and utilizes middlewares for request and
        response processing.
    """

    def __init__(self, router_queue: Queue[Event], api_broker_queue: Queue[Event], middlewares: list[Middleware]) -> None:
        """
        Initializes an ApiBroker instance with specific queues for routing and
        API broker events.

        Parameters:
            router_queue (Queue): The queue for receiving routed events from other
            components of the system.
            api_broker_queue (Queue): The queue specifically for the API broker to
            receive events.

        Returns:
            None
        """
        super().__init__(router_queue)
        self.api_broker_queue = api_broker_queue
        self.logger = getLogger(__name__)
        self.clients: Storage[Client]
        self.db = None
        self.events = {event.event: EventInfo(event.resource, event.handling) for event in api_events}

        self.middlewares_request = []
        self.middlewares_response = []
        for middleware in middlewares:
            if middleware.is_request:
                self.middlewares_request.append(middleware)
            if middleware.is_response:
                self.middlewares_response.append(middleware)

            requests, responses = middleware.register_events()
            for event in api_events:
                if event in requests or event in responses:
                    self.events[event.event] = EventInfo(event.resource, event.handling)
        self.roots: DefaultDict[Type[Event], TrieNode] = defaultdict(TrieNode)

    @property
    def name(self) -> str:
        """
        Property returning the name of the ApiBroker instance. Primarily used for
        logging and identification purposes.

        Returns:
            str: The name "ApiBroker".
        """
        return "ApiBroker"

    def _send(self, client: Client, event: Event) -> None:
        """
        Attempts to send an event to a specific client. If the connection is broken
        or reset during sending, it logs a warning and unregisters the client.

        Parameters:
            client (Client): The client object representing the target for the event.
            event (Event): The event to be sent to the client.

        Returns:
            None
        """
        try:
            client.socket.send(event)
        except (BrokenPipeError, ConnectionResetError) as e:
            self.logger.warning("Cannot be send %s", client.socket, exc_info=e)
            self.client_unregister(event)

    def send_specific(self, event: Event) -> None:
        """
        Sends an event to the specific client identified by the event's key. Logs
        a warning if the client is not found.

        Parameters:
            event (Event): The event containing the key of the target client.

        Returns:
            None
        """
        self.logger.debug("-> %s", event)
        if not event._api or not event._api.key:
            self.logger.error("Key not found in the event %s", event)
            return
        try:
            client = self.clients[event._api.key]
        except KeyError:
            self.logger.warning("Client was not found: %s", event)
            return
        self._send(client, event)

    def send_subscribed(self, event: Event) -> None:
        """
        Sends an event to all clients that are subscribed to the parameters
        matching the event's attributes.

        Parameters:
            event (Event): The event to be sent to subscribed clients.

         Returns:
             None
        """

        clients = self._search_trie(self.roots[event.__class__], event)
        for client in clients:
            self.logger.debug("->? %s", event)
            self._send(client, event)

    def send_all(self, event: Event) -> None:
        """
         Broadcasts an event to all clients that are of a specific API type (e.g., WebSocket).
         It iterates through all clients and sends the event to those matching the type.

         Parameters:
             event (Event): The event to be broadcasted.

         Returns:
             None
         """
        self.logger.debug("->* %s", event)
        for client in self.clients.values():
            if client.type == ApiType.WS:
                self._send(client, event)

    def client_register(self, event: client.Register) -> None:
        """
        Handles the registration of a new client based on the received register event.
        It assigns a unique key to the client, stores it, and acknowledges the registration.

        Parameters:
            event (client.Register): The event containing the client's registration information.

        Returns:
            None
        """
        event._api = ApiInfo(self.clients.append(Client(event.socket, event.type)), event.type)
        event.socket = None
        event.response.set_status(ResponseStatus.OK)
        self.send_specific(event)

    def client_unregister(self, event: Event) -> None:
        """
        Handles the unregistration of a client, removing them from the stored clients
        based on the event's key. It performs cleanup by closing the client's socket
        and removing them from the trie.
        Parameters:
            event (Event): The event containing the key of the client to be unregistered.

        Returns:
            None
        """
        try:
            if event._api and event._api.key:
                client = self.clients[event._api.key]
                client.socket.close()
                del self.clients[event._api.key]
                self._remove_client_from_tries(client)
            else:
                self.logger.warning("Client cant be unregistered because key is missing!")
        except KeyError as e:
            self.logger.debug("Client was not found!", exc_info=e)

    def event_register(self, event: manage.EdriRegister) -> None:
        """
          Registers a client for specific events and their parameters, allowing for
          customized event handling. This method updates the client's event subscriptions
          and their associated parameters based on the provided event registration details.

          Parameters:
              event (manage.Register): An object representing the event registration request.
              This object must include a non-empty `_key` attribute identifying the client,
              a list of `events` the client wishes to subscribe to, and corresponding
              `parameters` and `values` for those events.

          Returns:
              None

          Raises:
              KeyError: If the event `_key` attribute is missing or if the `_key` does not
              correspond to any existing client in the `clients` dictionary.

              ValueError: If the `events` list in the `event` object is empty, indicating
              that no events have been specified for registration.

              LookupError: If any of the events specified in the `event.events` list do not
              exist in the `self.events` mapping, indicating an attempt to register for
              undefined events.

          This method first verifies that the event `_key` is present and corresponds to an
          existing client. It then proceeds to update the client's event subscriptions and
          parameters. If successful, the client's response status is set to `OK`, and the
          updated event registration details are sent back to the client via their socket.
          """
        if not event._api.key:
            raise AttributeError("Event key is missing!")
        try:
            client = self.clients[event._api.key]
        except KeyError as e:
            self.logger.error("Client was not found: %s", event, exc_info=e)
            event.response.set_status(ResponseStatus.FAILED)
            return

        try:
            root = self._find_root(event.event)
        except KeyError as e:
            self.logger.error("Event was not found: %s", event.event, exc_info=e)
            event.response.set_status(ResponseStatus.FAILED)
            client.socket.send(event)
            return

        self._insert_client_to_trie(root, event.param_set, client)

        event.response.set_status(ResponseStatus.OK)
        client.socket.send(event)

    def event_unregister(self, event: manage.EdriUnregister) -> None:
        """
        Unregisters a client from a specific subscription based on the provided param_set.
        Removes the client from the trie along the path defined by param_set.

        Parameters:
            event (manage.Unregister): The event containing unregistration details, including param_set.

         Returns:
             None
        """
        if not event._api and not event._api.key:
            raise AttributeError("Event key is missing!")
        try:
            client = self.clients[event._api.key]
        except KeyError as e:
            self.logger.error("Client was not found: %s", event, exc_info=e)
            event.response.set_status(ResponseStatus.FAILED)
            return

        # Remove client from trie for the given param_set
        param_set = event.param_set
        param_items = list(param_set.items())
        try:
            root = self._find_root(event.event)
        except KeyError as e:
            self.logger.error("Event was not found: %s", event.event, exc_info=e)
            event.response.set_status(ResponseStatus.FAILED)
            client.socket.send(event)
            return

        removed = self._remove_client_from_trie_by_param_set(root, param_items, 0, client)

        if removed:
            self.logger.debug("Client %s successfully unregistered from param_set %s", client, param_set)
            event.response.set_status(ResponseStatus.OK)
        else:
            self.logger.warning("Client %s was not registered for param_set %s", client, param_set)
            event.response.set_status(ResponseStatus.FAILED)
        client.socket.send(event)

    def documentation(self, event: client.EdriDocumentation):
        def split_camel(name: str) -> list[str]:
            """Split a CamelCase name into its component words, preserving acronyms."""
            return findall(r'[A-Z]+(?=[A-Z][a-z0-9])|[A-Z][a-z0-9]+|[A-Z]+|[a-z0-9]+', name)

        def detect_endpoints(api_event: ApiEvent) -> list[str]:
            return [api_type.name for api_type in ApiType if api_type.value not in api_event.exclude]

        def extract_parameters_response(event_cls: Type[Event]) -> tuple[dict[str, Any], dict[str, Any]]:
            VALIDATION_MAP: dict[type, tuple[str, type]] = {
                StringValidation: ("string", StringValidation.__bases__[0]),
                IntegerValidation: ("integer", IntegerValidation.__bases__[0]),
                FloatValidation: ("float", FloatValidation.__bases__[0]),
                DateValidation: ("date", DateValidation.__bases__[0]),
                TimeValidation: ("time", TimeValidation.__bases__[0]),
                DateTimeValidation: ("datetime", DateTimeValidation.__bases__[0]),
            }

            def resolve_validation(field_type: Injection) -> tuple[str | None, dict[str, Any]]:
                for validation_cls, (type_str, base_type) in VALIDATION_MAP.items():
                    if validation_cls in field_type.classes:
                        return str(base_type), {"type": type_str, "parameters": field_type.parameters}
                return None, {"parameters": field_type.parameters}

            def extract_response_info(response_type: Response) -> dict[str, Any]:
                params = {}
                for field in fields(response_type):
                    if field.name.startswith("_"):
                        continue
                    param = {"type": str(field.type)}
                    if field.default is not MISSING:
                        param["default"] = field.default

                    params[field.name] = param

                return {
                    "name": response_type.__name__,
                    "description": response_type.__doc__ or "",
                    "parameters": params,
                }

            params = {}
            response = {}
            for field in fields(event_cls):
                if field.name.startswith("_") or field.name == "method":
                    continue
                if field.name == "response":
                    response = extract_response_info(field.type)

                param: dict[str, Any] = {"type": str(field.type)}

                if isinstance(field.type, Injection):
                    param["type"], param["validation"] = resolve_validation(field.type)

                if field.default is not MISSING:
                    if isinstance(field.default, Cookie):
                        param["note"] = "Value will be load from cookie"
                    elif isinstance(field.default, Header):
                        param["note"] = "Value will be load from header"
                    elif isinstance(field.default, Scope):
                        param["note"] = "Value will be load from scope"
                    else:
                        param["default"] = field.default

                params[field.name] = param

            return params, response

        def sort_api_tree(node: dict) -> dict:
            leaf_nodes = {}
            group_nodes = {}

            for key, value in node.items():
                if isinstance(value, dict) and "_value" in value:
                    leaf_nodes[key] = value
                elif isinstance(value, dict):
                    group_nodes[key] = sort_api_tree(value)  # Recurse into subgroups

            # Combine leaf nodes first, then group nodes
            sorted_node = {**dict(sorted(leaf_nodes.items())), **dict(sorted(group_nodes.items()))}
            return sorted_node

        api_resources = {}

        for api_event in api_events:
            class_name = api_event.event.__name__
            parts = split_camel(class_name)
            node = api_resources

            for part in parts[:-1]:
                node = node.setdefault(part, {})

            leaf = parts[-1]
            parameters, response = extract_parameters_response(api_event.event)
            node[leaf] = {
                "_value": {
                    "name": class_name,
                    "description": api_event.event.__doc__ or "",
                    "url": api_event.url,
                    "method": api_event.method.name if api_event.method else None,
                    "endpoints": detect_endpoints(api_event),
                    "command": api_event.resource,
                    "parameters": parameters,
                    "cookies": api_event.cookies,
                    "headers": api_event.headers,
                    "response": response,
                }
            }

        event.response.api_resources = sort_api_tree(api_resources)
        self.send_specific(event)

    def solve(self, event: Event) -> None:
        """
        Determines the appropriate method to handle an incoming event based on its type and
        handling type specified in the events mapping.

        Parameters:
            event (Event): The event to be handled.

         Returns:
             None
        """
        if (event_info := self.events.get(event.__class__)) is None:
            self.logger.error("Unknown event type: %s", event.__class__)
        else:
            event = self.handle_middlewares(event, self.middlewares_response)
            if event:
                handling_type = event_info.handling_type
                if handling_type & EventHandlingType.SPECIFIC and event._api and event._api.key:
                    self.send_specific(event)
                elif handling_type & EventHandlingType.SUBSCRIBED:
                    self.send_subscribed(event)
                elif handling_type & EventHandlingType.ALL:
                    self.send_all(event)
                else:
                    self.logger.warning("Event %s with unexpected handling type %s", event, handling_type)

    def _prepare(self) -> None:
        """
         Prepares the ApiBroker for operation by initializing necessary components,
         such as client storage.

         Returns:
             None
         """
        super()._prepare()
        self.clients = Storage[Client]()

    @property
    def additional_pipes(self) -> set[Connection]:
        """
        Provides a set of additional pipes that should be monitored for incoming
        events, specifically the API broker queue.

        Returns:
            Set[Connection]: A set containing the reader end of the API broker queue.
        """
        return {self.api_broker_queue._reader}

    def run_resolver(self) -> Never:
        """
        The main event loop of the ApiBroker, continuously checking for and processing incoming events from various sources.
        The loop iterates indefinitely until a KeyboardInterrupt is raised, at which point it returns None.

        Returns:
            None: Raises a KeyboardInterrupt exception upon user termination.
        """
        while True:
            pipes: set[Connection] = set()
            if self.router_pipe:
                pipes.add(self.router_pipe)
            if self._workers:
                pipes.update(worker.pipe for worker in self._workers.values())
            pipes.update(self.additional_pipes)
            try:
                active_pipes = wait(pipes, timeout=10)
                for active_pipe in active_pipes:
                    if active_pipe == self.router_pipe:
                        event: Event = self.router_pipe.recv()
                        event._timing.stamp(self.__class__.__name__, "Received")
                        self.logger.debug("Received event: %s", event)
                        self.resolve(event)
                    else:
                        try:
                            event = active_pipe.recv()
                        except EOFError as e:
                            self.logger.error("Communication problems", exc_info=e)
                            continue
                        except OSError as e:
                            self.logger.error("OS problems", exc_info=e)
                            continue
                        else:
                            event._timing.stamp(self.__class__.__name__, "Received")
                            self.resolve_callback(event, active_pipe)

            except KeyboardInterrupt:
                return None

    def resolve_callback(self, event: Event, pipe: Connection) -> None:
        """
        Handles incoming events received from clients or other components, dispatching
        them to the appropriate handling method based on their type.

        Parameters:
            event (Event): The incoming event to be handled.
            pipe (Connection): The communication pipe from which the event was received.

        Returns:
            None
        """
        self.logger.debug("<- Client %s", event)
        if isinstance(event, group.Client):
            if isinstance(event, client.Register):
                self.client_register(event)
            elif isinstance(event, client.Unregister):
                self.client_unregister(event)
            elif isinstance(event, client.EdriDocumentation):
                self.documentation(event)
        elif isinstance(event, group.Manage):
            if isinstance(event, manage.EdriRegister):
                self.event_register(event)
            elif isinstance(event, manage.EdriUnregister):
                self.event_unregister(event)
        else:
            self.logger.debug("Router <- API Broker %s", event)
            try:
                event = self.handle_middlewares(event, self.middlewares_request)
            except Exception as e:
                self.logger.exception("Exception during middleware running", exc_info=e)
            else:
                if event:
                    self.router_queue.put(event)

    def handle_middlewares(self, event: Event, middlewares: list[Middleware]) -> Event | None:
        event_info = self.events.get(event.__class__, None)
        for middleware in middlewares:
            try:
                event._timing.stamp(middleware.__class__.__name__, "Started")
                if not event.has_response():
                    control = middleware.process_request(event, event_info)
                else:
                    control = middleware.process_response(event, event_info)
                event._timing.stamp(middleware.__class__.__name__, "Finished")
                if not isinstance(control, MiddlewareControl):
                    self.logger.error("Middleware %s suppose to return MiddlewareControl object", middleware.__class__.__name__)
                    event.response.set_status(ResponseStatus.FAILED)
                    event.response.add_directive(InternalServerErrorResponseDirective(
                        f"Middleware  {middleware.__class__.__name__} suppose to return MiddlewareControl object"))
                    self.resolve(event)
                    raise TypeError("Middleware %s suppose to return MiddlewareControl object" % middleware.__class__.__name__)

                if control.action == MiddlewareControl.ActionType.CONTINUE:
                    continue

                elif control.action == MiddlewareControl.ActionType.STOP:
                    self.logger.info("Processing stopped: %s", middleware.__class__.__name__)
                    return None

                elif control.action == MiddlewareControl.ActionType.REPLACE_EVENT:
                    self.logger.debug("Event replaced by middleware: %s. New event: %s", middleware.__class__.__name__, control.event)
                    return control.event

                elif control.action == MiddlewareControl.ActionType.REDIRECT:
                    self.logger.debug("Event redirected by middleware to router: %s. New event: %s", middleware.__class__.__name__,
                                      control.event)
                    if not event.has_response():
                        self.solve(control.event)
                    else:
                        self.router_queue.put(control.event)
                    return None
            except Exception as e:
                self.logger.error("Unknown error while processing request in middleware", exc_info=e)
                event.response.set_status(ResponseStatus.FAILED)
                event.response.add_directive(InternalServerErrorResponseDirective(
                    f"Unknown error while processing request in middleware: {middleware.__class__.__name__}"))
                self.resolve(event)
                raise e

        return event

    def _prepare_resolvers(self) -> None:
        """
        Prepares the resolvers for handling specific types of events, enhancing
        the base implementation with API-specific event handling.

        Returns:
            None
        """
        for event in api_events:
            if "response" not in event.event.__annotations__:
                self._requests[event.event] = self.solve
            else:
                self._responses[event.event] = self.solve
        super()._prepare_resolvers()

    @staticmethod
    def _insert_client_to_trie(node, param_set: dict[str, Any], client: Client) -> None:
        """
        Inserts a client into the trie based on the provided parameter set.

        Parameters:
            node (TrieNode): The current node in the trie.
            param_set (dict[str, Any]): The parameter set defining the subscription path.
            client (Client): The client to be inserted.

        Returns:
            None
        """
        for param, value in param_set.items():
            key = (param, value)
            if key not in node.children:
                node.children[key] = TrieNode(key=key)
            node = node.children[key]
        node.is_end = True
        node.clients.add(client)

    @classmethod
    def _search_trie(cls, node: TrieNode, event: Event, path=None) -> list[Client]:
        """
        Searches the trie to find all clients subscribed to parameters matching the event's attributes.

        Parameters:
            node (TrieNode): The current node in the trie.
            event (Event): The event containing attributes to match.
            path (set): A set to keep track of the current traversal path.

        Returns:
            list[Client]: A list of clients that match the event's parameters.
        """
        if path is None:
            path = set()
        results = []

        if node.is_end:
            results.extend(node.clients)

        for (param, value), child in node.children.items():
            event_fields = {field.name: getattr(event, field.name) for field in fields(event)}
            if param in event_fields and event_fields[param] == value and (param, value) not in path:
                path.add((param, value))
                results.extend(cls._search_trie(child, event, path))
                path.remove((param, value))

        return results

    def _remove_client_from_tries(self, client: Client) -> bool:
        return any([self._remove_client_from_trie(root, client) for root in self.roots.values()])

    @classmethod
    def _remove_client_from_trie(cls, node: TrieNode, client: Client) -> bool:
        """
        Recursively removes the client from the trie. Used when a client unregisters entirely.
        Returns True if the node should be deleted (no clients and no children), False otherwise.

        Parameters:
            node (TrieNode): The current node in the trie.
            client (Client): The client to be removed.

        Returns:
            bool: True if the node can be deleted, False otherwise.
        """
        # Remove the client from the current node if present
        if client in node.clients:
            node.clients.remove(client)

        # Make a list of keys to avoid modifying the dictionary while iterating
        keys = list(node.children.keys())
        for key in keys:
            child = node.children[key]
            # Recursively remove the client from child nodes
            should_delete_child = cls._remove_client_from_trie(child, client)
            if should_delete_child:
                # Delete the child node if it has no clients and no children
                del node.children[key]

        # Determine if the current node should be deleted
        if not node.clients and not node.children:
            return True  # Node can be deleted
        else:
            return False  # Node should remain

    def _remove_client_from_trie_by_param_set(
            self, node: TrieNode, param_items: list[tuple[str, Any]], index: int, client: Client
    ) -> bool:
        """
        Recursive function to remove client from a specific path in trie.
        Returns True if the client was removed, False otherwise.

        Parameters:
            node (TrieNode): The current node in the trie.
            param_items (list[tuple[str, Any]]): The list of parameter items defining the path.
            index (int): The current index in the param_items list.
            client (Client): The client to be removed.

        Returns:
            bool: True if the client was removed, False otherwise.
        """
        if index < len(param_items):
            param, value = param_items[index]
            key = (param, value)
            if key in node.children:
                child = node.children[key]
                client_removed = self._remove_client_from_trie_by_param_set(child, param_items, index + 1, client)
                # After recursion, check if the child node should be deleted
                if client_removed:
                    if not child.clients and not child.children:
                        del node.children[key]
                    return True
                else:
                    return False
            else:
                # The path does not exist; client was not registered for this param_set
                return False
        else:
            # At the leaf node corresponding to param_set
            if client in node.clients:
                node.clients.remove(client)
                return True
            else:
                # Client was not registered for this param_set
                return False

    def after_start(self) -> None:
        for middleware in self.middlewares_request:
            requests, responses = middleware.register_events()

            for request in requests:
                self.router_queue.put(
                    Subscribe(pipe=None, name=self.name, event_type=request, request=True, from_time=self._from_time)
                )
            for response in responses:
                self.router_queue.put(
                    Subscribe(pipe=None, name=self.name, event_type=response, request=False, from_time=self._from_time)
                )

    def resolve_unknown(self, event: Event) -> None:
        if isinstance(event, Subscribe) and event.has_response():
            return
        if not event.has_response():
            for middleware in self.middlewares_request:
                requests, _ = middleware.register_events()
                if event.__class__ in requests:
                    event = self.handle_middlewares(event, [middleware])
                    if event:
                        self.router_queue.put(event)
                    return
        else:
            for middleware in self.middlewares_response:
                _, responses = middleware.register_events()
                if event.__class__ in responses:
                    event = self.handle_middlewares(event, [middleware])
                    if event:
                        self.solve(event)
                    return
        super().resolve_unknown(event)

    def _find_root(self, event_name: str) -> TrieNode:
        for event, event_info in self.events.items():
            if event_info.resource == event_name:
                break
        else:
            raise KeyError(event_name)

        return self.roots[event]

    def _subscribe_static_resolvers(self) -> None:
        """
         Registers static resolver methods for specific event types, such as health checks and store get requests.
         """
        self.logger.debug("Registering static resolvers")
        self._requests[HealthCheck] = self.health_check
