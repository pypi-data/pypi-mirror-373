import unittest
from datetime import datetime, timedelta
from multiprocessing.connection import Connection
from multiprocessing.queues import Queue
from unittest.mock import MagicMock, patch

from edri.config.setting import HEALTH_CHECK_TIMEOUT
from edri.dataclass.health_checker import Status
from edri.events.edri.router import HealthCheck
from edri.events.edri.scheduler import Set as SchedulerSet
from edri.router.health_checker import HealthChecker
from tests.events.test import Ping


class TestHealthChecker(unittest.TestCase):

    def setUp(self):
        self.router_queue = MagicMock(spec=Queue)
        self.component_mock = MagicMock()
        self.component_mock.name = "test_component"
        self.components = {self.component_mock}
        self.health_checker = HealthChecker(self.router_queue, self.components)
        self.health_checker.logger = MagicMock()

    def test_set_task(self):
        self.router_queue.reset_mock()
        with patch("edri.router.health_checker.datetime") as mock_datetime:
            now = datetime.now()
            mock_datetime.now.return_value = now
            self.health_checker.set_task()
        self.router_queue.put.assert_called_once()
        args = self.router_queue.put.call_args[0][0]
        self.assertIsInstance(args, SchedulerSet)
        self.assertIsInstance(args.event, HealthCheck)
        self.assertEqual(args.when, now + timedelta(seconds=HEALTH_CHECK_TIMEOUT))
        self.assertEqual(args.repeat, timedelta(seconds=HEALTH_CHECK_TIMEOUT))
        self.assertEqual(args.identifier, "HealthCheckerTask")

    def test_component_add(self):
        pipe = MagicMock(spec=Connection)

        self.health_checker.component_add(self.component_mock.name, pipe)
        self.assertIn(self.component_mock.name, self.health_checker.statuses)
        self.assertEqual(self.health_checker.statuses[self.component_mock.name].name, self.component_mock.name)
        self.assertEqual(self.health_checker.statuses[self.component_mock.name].pipe, pipe)
        self.assertEqual(self.health_checker.statuses[self.component_mock.name].definition, self.component_mock)
        self.health_checker.logger.debug.assert_called_with("Manager was added %s %s", self.component_mock.name, pipe)

    def test_control_start(self):
        with patch.object(self.health_checker, "check_status") as mock_save_status:
            self.health_checker.last_check = datetime.now()
            self.health_checker.control_start()
            mock_save_status.assert_called_once()
            self.assertIsNotNone(self.health_checker.last_check)

    def test_control_result(self):
        pipe = MagicMock(spec=Connection)
        self.health_checker.component_add(self.component_mock.name, pipe)
        health_check = HealthCheck()
        health_check.response.name = self.component_mock.name
        health_check.response.status = Status.OK
        health_check.response.exceptions = []
        self.health_checker.control_result(health_check)
        self.assertEqual(self.health_checker.statuses[self.component_mock.name].status, Status.OK)
        self.assertIsNotNone(self.health_checker.statuses[self.component_mock.name].timestamp)
        self.health_checker.logger.debug.assert_called_with("Add status record to %s - %s, %s", f"{self.component_mock.name}", Status.OK, 0)

    def test_check_status(self):
        self.router_queue.reset_mock()
        name1 = "test_component_1"
        pipe1 = MagicMock(spec=Connection)
        name2 = "test_component_2"
        pipe2 = MagicMock(spec=Connection)
        name3 = "test_component_3"
        pipe3 = MagicMock(spec=Connection)
        ping = MagicMock(spec=Ping)

        self.health_checker.component_add(name1, pipe1)
        self.health_checker.component_add(name2, pipe2)
        self.health_checker.component_add(name3, pipe3)
        self.health_checker.statuses[name1].status = Status.OK
        self.health_checker.statuses[name1].timestamp = datetime.now()
        self.health_checker.statuses[name3].status = Status.OK
        self.health_checker.statuses[name3].timestamp = datetime.now() - timedelta(seconds=HEALTH_CHECK_TIMEOUT * 2)
        self.health_checker.logger.reset_mock()

        with patch("edri.router.health_checker.datetime") as mock_datetime:
            now = datetime.now()
            mock_datetime.now.return_value = now

            self.health_checker.check_status()
            self.health_checker.logger.warning.assert_called_with("%s did not send a status message - last status %s", name3, Status.OK)

    def test_restart_component(self):
        pipe = MagicMock(spec=Connection)
        now = datetime.now()
        self.health_checker.component_add(self.component_mock.name, pipe)
        self.component_mock.__class__ = MagicMock()
        self.health_checker.restart_component(pipe, now)
        self.health_checker.logger.warning.assert_called_with("Restarting component")
        self.component_mock.__class__.assert_called_once_with(router_queue=self.router_queue, from_time=now)
        self.health_checker.logger.info.assert_called_with("Component restarted")

        self.health_checker.component_add(f"{self.component_mock.name}1234", pipe)
        self.component_mock.definition = False
        self.health_checker.restart_component(pipe, now)
        self.health_checker.logger.warning.assert_called_with("Restarting component")
        self.health_checker.logger.error.assert_called_with("Component was found - definition was missing")

    def test_restart_component_not_found(self):
        pipe = MagicMock(spec=Connection)
        self.health_checker.restart_component(pipe, datetime.now())
        self.health_checker.logger.error.assert_called_with("Component was not found")
