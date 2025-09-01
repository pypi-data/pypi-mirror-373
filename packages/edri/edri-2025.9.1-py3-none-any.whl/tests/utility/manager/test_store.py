import unittest
from unittest.mock import MagicMock
from multiprocessing.queues import Queue

from edri.events.edri.store import Set, Get, Delete, GetCallback
from edri.utility.manager import Store, Callback


class TestStore(unittest.TestCase):

    def setUp(self):
        self.router_queue = MagicMock(spec=Queue)
        self.store = Store(self.router_queue)
        self.store.logger = MagicMock()

    def test_solve_req_set(self):
        event = Set(name="key1", value="value1")
        self.store.solve_req_set(event)
        self.assertEqual(self.store.store["key1"], "value1")
        self.store.logger.debug.assert_called_with("Value set for key '%s': %s", "key1", "value1")

    def test_solve_req_get(self):
        self.store.store["key1"] = "value1"
        event = Get(name="key1")
        self.store.solve_req_get(event)
        self.assertEqual(event.response.value, "value1")
        self.store.logger.debug.assert_called_with("Value retrieved for key '%s': %s", "key1", "value1")

        event = Get(name="key2")
        self.store.solve_req_get(event)
        self.assertIsNone(event.response.value)
        self.store.logger.debug.assert_called_with("No value found for key '%s'", "key2")

    def test_solve_req_delete(self):
        self.store.store["key1"] = "value1"
        event = Delete(name="key1")
        self.store.solve_req_delete(event)
        self.assertNotIn("key1", self.store.store)
        self.store.logger.debug.assert_called_with("Deleted item with key '%s'", "key1")

        event = Delete(name="key2")
        self.store.solve_req_delete(event)
        self.store.logger.debug.assert_called_with("Attempted to delete non-existent key '%s'", "key2")

    def test_solve_req_get_callback(self):
        condition = lambda x: x == "value1"
        event = GetCallback(name="key1", condition=condition)
        self.store.solve_req_get_callback(event)
        self.assertIn("key1", self.store.callbacks)
        self.assertEqual(len(self.store.callbacks["key1"]), 1)
        self.assertEqual(self.store.callbacks["key1"][0].condition, condition)
        self.store.logger.debug.assert_called_with("Callback added for key '%s'", "key1")

    def test_callbacks_triggered_on_set(self):
        condition = lambda x: x == "value1"
        self.store.callbacks["key1"] = [Callback(condition)]

        event = Set(name="key1", value="value1")
        self.store.solve_req_set(event)
        self.store.router_queue.put.assert_called_once()
        self.store.logger.debug.assert_called_with("Sending callback item for '%s'", "key1")

        event = Set(name="key1", value="value2")
        self.store.solve_req_set(event)
        self.store.router_queue.put.assert_called_once()
        self.store.logger.debug.assert_called_with("Value set for key '%s': %s", "key1", "value2")
