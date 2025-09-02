import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from edri.config.constant import ApiType
from edri.config.setting import CACHE_TIMEOUT, CACHE_INFO_MESSAGE
from edri.dataclass.event import Event, ApiInfo
from edri.dataclass.response import ResponseStatus
from edri.router.cache import Cache


class TestCache(unittest.TestCase):

    def setUp(self):
        self.cache = Cache()
        self.cache.logger = MagicMock()  # Mock logger to prevent actual logging

    def tearDown(self):
        self.cache.quit()  # Ensure the cleaner thread is stopped after each test

    def test_append(self):
        event = MagicMock(spec=Event)
        timestamp = self.cache.append(event)
        self.assertEqual(len(self.cache.items), 1)
        self.assertEqual(self.cache.items[0].event, event)
        self.assertEqual(self.cache.items[0].time, timestamp)

    def test_find(self):
        event1 = MagicMock(spec=Event)
        event1.response = None
        event2 = MagicMock(spec=Event)
        event2.response = MagicMock()
        event2.response.get_status.return_value = ResponseStatus.NONE
        self.cache.append(event1)
        timestamp = self.cache.append(event2)

        found_events = self.cache.find(MagicMock, True, None)
        self.assertEqual(len(found_events), 2)

        found_events = self.cache.find(MagicMock, False, None)
        self.assertEqual(len(found_events), 0)

        found_events = self.cache.find(MagicMock, True, timestamp)
        self.assertEqual(len(found_events), 1)


    def test_clean(self):
        event = MagicMock(spec=Event)
        self.cache.append(event)

        with patch("edri.router.cache.datetime") as mock_datetime, patch("edri.router.cache.sleep", side_effect=StopIteration) as mock_sleep:
            now = datetime.now()
            mock_datetime.now.side_effect = [now, now + timedelta(seconds=CACHE_TIMEOUT + 1)]
            with self.assertRaises(StopIteration):
                self.cache.clean()
            self.assertEqual(len(self.cache.items), 0)

            mock_datetime.now.side_effect = [now, now + timedelta(seconds=CACHE_INFO_MESSAGE + 1)]
            with self.assertRaises(StopIteration):
                self.cache.clean()
            self.cache.logger.info.assert_called_with("Count of cached events: %s", 0)

    def test_last_events(self):
        event1 = MagicMock(spec=Event)
        event1._switch.router_id = uuid4()
        event1._api = ApiInfo("key1", ApiType.HTML)
        self.cache.append(event1)

        event2 = MagicMock(spec=Event)
        event2._switch.router_id = uuid4()
        event2._api = ApiInfo("key2", ApiType.HTML)
        self.cache.append(event2)

        last_events = self.cache.last_events()
        self.assertEqual(len(last_events), 2)
        self.assertEqual(last_events[event1._switch.router_id], "key1")
        self.assertEqual(last_events[event2._switch.router_id], "key2")

    def test_events_from(self):
        event1 = MagicMock(spec=Event)
        event1._api = ApiInfo("key1", ApiType.HTML)
        self.cache.append(event1)

        event2 = MagicMock(spec=Event)
        event2._api = ApiInfo("key2", ApiType.HTML)
        self.cache.append(event2)

        event3 = MagicMock(spec=Event)
        event3._api = ApiInfo("key3", ApiType.HTML)
        self.cache.append(event3)

        events = self.cache.events_from("key1")
        self.assertEqual(list(events), [event2, event3])

    def test_quit(self):
        self.cache.quit()
        self.assertTrue(self.cache.cleaner_stop.is_set())
        self.cache.cleaner.join()
