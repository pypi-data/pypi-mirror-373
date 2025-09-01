import unittest
from http import HTTPMethod
from typing import Union

from edri.api.dataclass.api_event import api, api_events
from edri.dataclass.event import Event


class TestApiDecorator(unittest.TestCase):
    def test_api_decorator(self):
        @api(url="/test", template="my_template.j2")
        class TestEvent(Event):
            strings: Union[str, int]
            method: HTTPMethod = HTTPMethod.POST

        self.assertGreaterEqual(len(api_events), 1)
        api_event = api_events[-1]
        self.assertEqual(api_event.url, "/test")
        self.assertEqual(api_event.resource, "test-event")
        self.assertEqual(api_event.event.__name__, "TestEvent")
