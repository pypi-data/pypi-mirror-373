import unittest

from edri.config.setting import SWITCH_KEY_LENGTH
from edri.dataclass.response import Response
from edri.dataclass.response import ResponseStatus
from zlib import adler32

from edri.dataclass.event import SwitchInfo, Event


class TestBaseIdentification(unittest.TestCase):
    def test_default_key_generation(self):
        base_id = SwitchInfo()

        # Then
        self.assertEqual(len(base_id.key), SWITCH_KEY_LENGTH)
        self.assertIsNotNone(base_id.key)
        self.assertFalse(base_id.received)


class TestEvent(unittest.TestCase):

    def test_initial_state(self):
        event = Event()
        self.assertIsNone(event.get_response())
        self.assertFalse(event.has_response())

    def test_set_response(self):
        event = Event()
        response = Response()
        response.set_status(ResponseStatus.OK)
        event.set_response(response)
        self.assertEqual(event.get_response(), response)

    def test_remove_response(self):
        event = Event()
        response = Response()
        event.set_response(response)
        event.remove_response()
        self.assertIsNone(event.get_response())

    def test_hash_name(self):
        expected_hash = adler32(f"{Event.__module__}.{Event.__qualname__}".encode())
        self.assertEqual(Event.hash_name(), expected_hash)
