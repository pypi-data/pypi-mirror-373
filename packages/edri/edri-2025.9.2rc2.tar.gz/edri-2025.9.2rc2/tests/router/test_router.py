import unittest
from unittest.mock import MagicMock, patch, call
from multiprocessing.connection import Connection
from multiprocessing.queues import Queue
from typing import Type

from edri.abstract import ManagerBase
from edri.dataclass.event import Event, Timing
from edri.dataclass.response import ResponseStatus
from edri.events.edri import router
from edri.events.edri.router import SendFrom
from tests.events.test import Ping, EventRequest
from edri.router import Router, Cache


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.queue = MagicMock(spec=Queue)
        self.components = {MagicMock(spec=ManagerBase)}
        self.router = Router(self.queue, self.components)
        self.router.cache = MagicMock(spec=Cache)
        self.router.logger = MagicMock()
        self.router.connector_pipe = MagicMock()

    def test_subscribe_successful(self):

        pipe = MagicMock(spec=Connection)
        event = MagicMock(spec=router.Subscribe)
        event.name = "TestComponent"
        event.pipe = pipe
        event.request = True
        event.event_type = MagicMock(spec=Type[Event])
        self.router.subscribed_requests = {event.event_type: {None}}

        pipe = self.router.subscribe(event)

        self.assertIn("TestComponent", self.router.connections)
        self.assertIn(event.event_type, self.router.subscribed_requests)
        self.assertIn(pipe, self.router.subscribed_requests[event.event_type])
        self.router.connector_pipe.send.assert_called_once()
        event.response.set_status.assert_called_once_with(ResponseStatus.OK)
        pipe.send.assert_called_once_with(event)

        self.router.connector_pipe.reset_mock()

        pipe2 = MagicMock(spec=Connection)
        event2 = MagicMock(spec=router.Subscribe)
        event2.name = "TestComponent"
        event2.pipe = pipe2
        event2.request = False
        event2.event_type = MagicMock(spec=Type[Event])

        self.router.subscribe(event2)

        self.assertIn("TestComponent", self.router.connections)
        self.assertIn(event2.event_type, self.router.subscribed_responses)
        self.assertIn(pipe, self.router.subscribed_responses[event2.event_type])
        self.router.connector_pipe.send.assert_called_once()
        event2.response.set_status.assert_called_once_with(ResponseStatus.OK)
        pipe2.send.assert_not_called()

    def test_subscribe_missing_pipe(self):
        event = MagicMock(spec=router.Subscribe)
        event.name = "TestComponent"
        event.pipe = None
        event.request = True
        event.event_type = MagicMock(spec=Type[Event])

        # Test subscription with missing pipe
        result = self.router.subscribe(event)

        self.assertIsNone(result)
        self.router.logger.error.assert_called_with("Missing pipe in subscribe event!")

    def test_unsubscribe(self):
        event = MagicMock(spec=router.Unsubscribe)
        event.name = "TestComponent"
        event.request = True
        event.event_type = MagicMock(spec=Type[Event])
        event.pipe = MagicMock(spec=Connection)

        # Add a subscription first
        self.router.subscribed_requests[event.event_type] = {event.pipe}
        self.router.connections[event.name] = event.pipe

        # Test unsubscribing
        self.router.unsubscribe(event)

        self.assertNotIn(event.pipe, self.router.subscribed_requests[event.event_type])

    def test_unsubscribe_pipe(self):
        pipe = MagicMock(spec=Connection)
        self.router.connections["TestComponent"] = pipe
        self.router.subscribed_requests[MagicMock(spec=Type[Event])] = {pipe}
        self.router.subscribed_responses[MagicMock(spec=Type[Event])] = {pipe}

        # Test unsubscribing a pipe
        self.router.unsubscribe_pipe(pipe)

        self.assertNotIn("TestComponent", self.router.connections)
        for subscribers in self.router.subscribed_requests.values():
            self.assertNotIn(pipe, subscribers)
        for subscribers in self.router.subscribed_responses.values():
            self.assertNotIn(pipe, subscribers)
        self.router.logger.warning.assert_called_with("Removing subscription for this connection: %s", pipe)

    # def test_send_from_with_id(self):
    #     # Prepare the cached events
    #     event1 = Event()
    #     event2 = EventRequest()
    #     event2.response.set_status(ResponseStatus.OK)
    #     self.router.cache.events_from.return_value = [event1, event2]
    #     self.router.subscribed_requests[Event] = {self.router.connector_pipe}
    #     self.router.subscribed_responses[EventRequest] = {self.router.connector_pipe}
    #
    #     # Prepare the SendFrom event
    #     send_from_event = MagicMock(spec=SendFrom)
    #     send_from_event.key = "some-key"
    #
    #     # Call the method
    #     self.router.send_from(send_from_event)
    #
    #     # Verify that events_from was called with the correct key
    #     self.router.cache.events_from.assert_called_once_with(send_from_event.key)
    #
    #     # Verify that the connector pipe tried to send the events
    #     # TODO: this call need much better checking
    #     self.router.connector_pipe.send.assert_has_calls([call(send_from_event), call(send_from_event)])
    #
    # def test_send_from_without_id(self):
    #     # Prepare the cached events
    #     event1 = Event()
    #     event2 = EventRequest()
    #     event2.response.set_status(ResponseStatus.OK)
    #     self.router.cache.items = [MagicMock(event=event1), MagicMock(event=event2)]
    #     self.router.subscribed_requests[Event] = {self.router.connector_pipe}
    #     self.router.subscribed_responses[EventRequest] = {self.router.connector_pipe}
    #
    #     # Prepare the SendFrom event
    #     send_from_event = MagicMock(spec=SendFrom)
    #     send_from_event.key = None
    #
    #     # Call the method
    #     self.router.send_from(send_from_event)
    #
    #     # Verify that events_from was called with the correct ID
    #     self.router.cache.events_from.assert_not_called()
    #
    #     # Verify that the connector pipe tried to send the events
    #     self.router.connector_pipe.send.assert_has_calls([call(send_from_event), call(send_from_event)])

    def test_send(self):
        event = MagicMock(spec=Event)
        event._switch = None
        connection1 = MagicMock(spec=Connection)
        connection2 = MagicMock(spec=Connection)
        self.router.connector_pipe = connection1

        self.router.send(event, {connection1, connection2})

        connection1.send.assert_called_once_with(event)
        connection2.send.assert_called_once_with(event)
        self.router.cache.append.assert_called_once_with(event)

        self.router.send(event, set())
        self.router.logger.info.assert_called_once_with("Event without subscriber: %s", event)

        connection1.send.side_effect = [BrokenPipeError]
        with patch.object(self.router, "unsubscribe_pipe") as mock_unsubscribe_pipe:
            self.router.send(event, {connection1})
            mock_unsubscribe_pipe.assert_called_once_with(connection1)


    @patch.object(Router, "send")
    def test_run_with_subscribe_event(self, mock_send):
        subscribe_event = MagicMock(spec=router.Subscribe)
        subscribe_event.name = "TestComponent"
        subscribe_event.event_type = MagicMock(spec=Type[Ping])
        subscribe_event.request = True
        subscribe_event.from_time = None
        subscribe_event.has_response.return_value = False
        subscribe_event._timing = MagicMock(spec=Timing)

        self.queue.get.side_effect = [subscribe_event, StopIteration]

        with patch.object(self.router, "subscribe", return_value=MagicMock(spec=Connection)) as mock_subscribe, self.assertRaises(StopIteration):
            self.router.run()
        mock_subscribe.assert_called_once_with(subscribe_event)

        self.router.logger.debug.assert_called_with("<- %s", subscribe_event)
        mock_send.assert_not_called()

    def test_quit(self):
        self.router.quit()
        self.router.cache.quit.assert_called_once()
