import unittest
from multiprocessing.connection import Connection
from unittest.mock import MagicMock, patch
from multiprocessing.queues import Queue

from edri.api import Broker
from edri.api.broker import EventInfo, TrieNode
from edri.api.dataclass import Client
from edri.config.constant import ApiType
from edri.dataclass.event import Event, EventHandlingType, ApiInfo
from edri.dataclass.response import ResponseStatus
from edri.events.api import manage, client
from tests.events.test import Ping
from edri.utility import Storage


class TestBroker(unittest.TestCase):

    def setUp(self):
        self.router_queue = MagicMock(spec=Queue)
        self.api_broker_queue = MagicMock(spec=Queue)
        self.api_broker_queue._reader = MagicMock()
        self.api_broker = Broker(self.router_queue, self.api_broker_queue, middlewares=[])
        self.api_broker.logger = MagicMock()  # Mock logger to prevent actual logging
        self.api_broker.clients = Storage()
        self.api_broker.router_pipe = MagicMock(spec=Connection)
        # Mock the events mapping
        self.api_broker.events = {
            Ping: EventInfo(resource="Ping", handling_type=EventHandlingType.ALL),
            manage.EdriRegister: EventInfo(resource="register", handling_type=EventHandlingType.SPECIFIC),
            manage.EdriUnregister: EventInfo(resource="unregister", handling_type=EventHandlingType.SPECIFIC),
            client.Register: EventInfo(resource="client_register", handling_type=EventHandlingType.SPECIFIC),
            client.Unregister: EventInfo(resource="client_unregister", handling_type=EventHandlingType.SPECIFIC),
            Event: EventInfo(resource="Event", handling_type=EventHandlingType.SUBSCRIBED),
        }
        # Initialize the roots for the trie
        self.api_broker.roots = {Event: TrieNode()}

    def test_send(self):
        client = MagicMock(spec=Client)
        client.socket = MagicMock(spec=Connection)

        self.api_broker.client_unregister = MagicMock()
        error = BrokenPipeError()
        client.socket.send = MagicMock(side_effect=error)
        event = MagicMock(spec=Event)
        self.api_broker._send(client, event)
        self.api_broker.logger.warning.assert_called_once_with("Cannot be send %s", client.socket, exc_info=error)
        self.api_broker.client_unregister.assert_called_once_with(event)

    def test_send_specific(self):
        event = Event()
        event._api = ApiInfo("client1", ApiType.HTML)
        client_mock = MagicMock(spec=Client)
        client_mock.type = ApiType.WS
        client_mock.socket = MagicMock()
        self.api_broker.clients["client1"] = client_mock

        self.api_broker.send_specific(event)
        client_mock.socket.send.assert_called_once_with(event)

        # Test when event._api is None
        event._api = None
        self.api_broker.logger.reset_mock()
        self.api_broker.send_specific(event)
        self.api_broker.logger.error.assert_called_once_with("Key not found in the event %s", event)

        # Test when client is not found
        event._api = ApiInfo("nonexistent_client", ApiType.HTML)
        self.api_broker.logger.reset_mock()
        self.api_broker.send_specific(event)
        self.api_broker.logger.warning.assert_called_once_with("Client was not found: %s", event)

    # def test_send_subscribed(self):
    #     # Prepare clients and subscriptions
    #     client1 = MagicMock(spec=Client)
    #     client1.type = ApiType.WS
    #     client1.socket = MagicMock()
    #     client2 = MagicMock(spec=Client)
    #     client2.type = ApiType.WS
    #     client2.socket = MagicMock()
    #     self.api_broker.clients["client1"] = client1
    #     self.api_broker.clients["client2"] = client2
    #
    #     # Register clients with different param_sets
    #     event_class = Event
    #     root = self.api_broker.roots[event_class]
    #     param_set1 = {"param1": "value1"}
    #     param_set2 = {"param2": "value2"}
    #     self.api_broker._insert_client_to_trie(root, param_set1, client1)
    #     self.api_broker._insert_client_to_trie(root, param_set2, client2)
    #
    #     # Create an event matching param_set1
    #     event = Event()
    #     event.param1 = "value1"
    #     event.param2 = "other_value"
    #     event.__class__ = event_class
    #
    #     self.api_broker.send_subscribed(event)
    #     client1.socket.send.assert_called_once_with(event)
    #     client2.socket.send.assert_not_called()

    def test_send_all(self):
        event = Event()
        client_mock = MagicMock(spec=Client)
        client_mock.type = ApiType.WS
        client_mock.socket = MagicMock()
        self.api_broker.clients["client1"] = client_mock

        self.api_broker.send_all(event)
        client_mock.socket.send.assert_called_once_with(event)

    def test_client_register(self):
        event = client.Register(type=ApiType.REST, socket=MagicMock())
        self.api_broker.send_specific = MagicMock()

        with patch.object(self.api_broker.clients, "append", return_value="client1"):
            self.api_broker.client_register(event)

        self.assertEqual(event._api.key, "client1")
        self.assertIsNone(event.socket)
        self.assertEqual(event.response.get_status(), ResponseStatus.OK)
        self.api_broker.send_specific.assert_called_once_with(event)

    def test_client_unregister(self):
        client_mock = MagicMock(spec=Client)
        client_mock.socket = MagicMock()
        self.api_broker.clients["client1"] = client_mock
        # Mock the _remove_client_from_tries method
        self.api_broker._remove_client_from_tries = MagicMock(return_value=True)

        event = Event()
        event._api = ApiInfo("client1", ApiType.HTML)
        self.api_broker.client_unregister(event)
        self.assertNotIn("client1", self.api_broker.clients)
        client_mock.socket.close.assert_called_once()
        self.api_broker._remove_client_from_tries.assert_called_once_with(client_mock)

        # Test when event._key is None
        event._api = None
        self.api_broker.logger.reset_mock()
        self.api_broker.client_unregister(event)
        self.api_broker.logger.warning.assert_called_with("Client cant be unregistered because key is missing!")

        # Test when client is not found
        event._api = ApiInfo("client2", ApiType.HTML)
        self.api_broker.logger.reset_mock()
        self.api_broker.client_unregister(event)
        self.api_broker.logger.debug.assert_called()
        self.api_broker.logger.debug.assert_called_with("Client was not found!", exc_info=unittest.mock.ANY)

    def test_event_register(self):
        client_mock = MagicMock(spec=Client)
        client_mock.socket = MagicMock()
        self.api_broker.clients["client1"] = client_mock

        event = manage.EdriRegister(event="Event", param_set={"param1": "value1"})
        event._api = ApiInfo("client1", ApiType.HTML)
        event.response = MagicMock()
        self.api_broker.event_register(event)

        # Check that the client was inserted into the trie
        root = self.api_broker.roots[Event]
        self.assertIn(("param1", "value1"), root.children)
        node = root.children[("param1", "value1")]
        self.assertTrue(node.is_end)
        self.assertIn(client_mock, node.clients)

        # Check that response status is OK and event sent back to client
        client_mock.socket.send.assert_called_once_with(event)
        event.response.set_status.assert_called_once_with(ResponseStatus.OK)

        # Test when event._key is None
        event._api = None
        with self.assertRaises(AttributeError):
            self.api_broker.event_register(event)

        # Test when client is not found
        event._api = ApiInfo("nonexistent_client", ApiType.HTML)
        self.api_broker.logger.reset_mock()
        self.api_broker.event_register(event)
        self.api_broker.logger.error.assert_called()
        event.response.set_status.assert_called_with(ResponseStatus.FAILED)

        # Test when event is not found
        event._key = "client1"
        event.event = "UnknownEvent"
        self.api_broker.logger.reset_mock()
        self.api_broker.event_register(event)
        self.api_broker.logger.error.assert_called()
        event.response.set_status.assert_called_with(ResponseStatus.FAILED)
        client_mock.socket.send.assert_called()

    # def test_event_unregister(self):
    #     client_mock = MagicMock(spec=Client)
    #     client_mock.socket = MagicMock()
    #     self.api_broker.clients["client1"] = client_mock
    #
    #     # First, register the client
    #     event_register = manage.Register(event="Event", param_set={"param1": "value1"})
    #     event_register._key = "client1"
    #     event_register.response = MagicMock()
    #     self.api_broker.event_register(event_register)
    #
    #     # Now, unregister the client from the same param_set
    #     event_unregister = manage.Unregister(event="Event", param_set={"param1": "value1"})
    #     event_unregister._key = "client1"
    #     event_unregister.response = MagicMock()
    #     self.api_broker.event_unregister(event_unregister)
    #
    #     # Check that the client was removed from the trie
    #     root = self.api_broker.roots[Event]
    #     self.assertNotIn(client_mock, root.children[("param1", "value1")].clients)
    #
    #     # Check that response status is OK and event sent back to client
    #     client_mock.socket.send.assert_called_with(event_unregister)
    #     event_unregister.response.set_status.assert_called_with(ResponseStatus.OK)

    def test_solve(self):
        # Mock the send_* methods
        self.api_broker.send_specific = MagicMock()
        self.api_broker.send_subscribed = MagicMock()
        self.api_broker.send_all = MagicMock()

        # Create events with different handling types
        event_specific = manage.EdriRegister(event="Event", param_set={"param1": "value1"})
        event_specific._api = ApiInfo("client1", ApiType.HTML)
        self.api_broker.events[event_specific.__class__] = EventInfo(resource="register", handling_type=EventHandlingType.SPECIFIC)
        self.api_broker.solve(event_specific)
        self.api_broker.send_specific.assert_called_once_with(event_specific)

        event_subscribed = Event()
        self.api_broker.events[event_subscribed.__class__] = EventInfo(resource="Event", handling_type=EventHandlingType.SUBSCRIBED)
        self.api_broker.send_specific.reset_mock()
        self.api_broker.solve(event_subscribed)
        self.api_broker.send_subscribed.assert_called_once_with(event_subscribed)

        event_all = Ping()
        self.api_broker.events[event_all.__class__] = EventInfo(resource="Ping", handling_type=EventHandlingType.ALL)
        self.api_broker.send_subscribed.reset_mock()
        self.api_broker.solve(event_all)
        self.api_broker.send_all.assert_called_once_with(event_all)

        # Test unknown event type
        unknown_event = MagicMock()
        unknown_event.__class__ = MagicMock()
        self.api_broker.logger.reset_mock()
        self.api_broker.solve(unknown_event)
        self.api_broker.logger.error.assert_called_once()

    def test_prepare(self):
        self.api_broker._prepare()
        self.assertIsInstance(self.api_broker.clients, Storage)

    def test_additional_pipes(self):
        self.assertEqual(self.api_broker.additional_pipes, {self.api_broker_queue._reader})

    # @patch('edri.api.broker.wait')
    # def test_run_resolver(self, mock_wait):
    #     ping = Ping()
    #     self.api_broker.router_pipe = MagicMock(spec=Connection)
    #     self.api_broker.router_pipe.recv = MagicMock(return_value=ping)
    #     self.api_broker.resolve = MagicMock(side_effect=KeyboardInterrupt)
    #
    #     # Simulate router_pipe being ready
    #     mock_wait.return_value = [self.api_broker.router_pipe]
    #     with self.assertRaises(KeyboardInterrupt):
    #         self.api_broker.run_resolver()
    #     self.api_broker.resolve.assert_called_once_with(ping)

    # def test_resolve_callback(self):
    #     event = Event()
    #     pipe = MagicMock(spec=Connection)
    #
    #     with patch.object(self.api_broker, "client_register") as mock_register, \
    #             patch.object(self.api_broker, "client_unregister") as mock_unregister, \
    #             patch.object(self.api_broker, "event_register") as mock_event_register, \
    #             patch.object(self.api_broker, "event_unregister") as mock_event_unregister, \
    #             patch.object(self.api_broker, "router_queue") as mock_router_queue:
    #         # Test client.Register
    #         event = client.Register()
    #         self.api_broker.resolve_callback(event, pipe)
    #         mock_register.assert_called_once_with(event)
    #
    #         # Test client.Unregister
    #         event = client.Unregister()
    #         self.api_broker.resolve_callback(event, pipe)
    #         mock_unregister.assert_called_once_with(event)
    #
    #         # Test manage.Register
    #         event = manage.Register()
    #         self.api_broker.resolve_callback(event, pipe)
    #         mock_event_register.assert_called_once_with(event)
    #
    #         # Test manage.Unregister
    #         event = manage.Unregister()
    #         self.api_broker.resolve_callback(event, pipe)
    #         mock_event_unregister.assert_called_once_with(event)
    #
    #         # Test other event
    #         event = Event()
    #         self.api_broker.resolve_callback(event, pipe)
    #         mock_router_queue.put.assert_called_once_with(event)

    @patch('edri.api.broker.api_events')
    def test_prepare_resolvers(self, mock_api_events):
        # Define some mock events
        mock_event_without_response = MagicMock()
        mock_event_with_response = MagicMock()
        mock_event_without_response.event.__annotations__ = {}
        mock_event_with_response.event.__annotations__ = {'response': 'ResponseStatus'}

        mock_api_events.__iter__.return_value = [
            mock_event_without_response,
            mock_event_with_response
        ]

        self.api_broker._prepare_resolvers()

        self.assertIn(mock_event_without_response.event, self.api_broker._requests)
        self.assertIn(mock_event_with_response.event, self.api_broker._responses)

        self.assertEqual(self.api_broker._requests[mock_event_without_response.event], self.api_broker.solve)
        self.assertEqual(self.api_broker._responses[mock_event_with_response.event], self.api_broker.solve)
