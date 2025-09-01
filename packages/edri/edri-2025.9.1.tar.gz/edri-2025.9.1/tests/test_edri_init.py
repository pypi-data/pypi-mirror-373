import unittest
from unittest.mock import MagicMock, patch
from multiprocessing.queues import Queue
from edri.utility.manager import Job
from edri.abstract import ManagerBase
from edri.api.broker import Broker
from edri.utility.json_encoder import CustomJSONEncoder

from edri import EDRI


class TestEDRI(unittest.TestCase):
    def setUp(self) -> None:
        self.edri = EDRI()

    def test_initialization(self) -> None:
        self.assertIsInstance(self.edri.router_queue, Queue)
        self.assertEqual(len(self.edri.components), 0)

    def test_add_component(self) -> None:
        mock_component = MagicMock(spec=ManagerBase)
        self.edri.add_component(mock_component)
        self.assertIn(mock_component, self.edri.components)

    @patch('edri.Store')
    def test_start_store(self, mock_store) -> None:
        mock_store_instance = mock_store.return_value
        self.edri.start_store()
        mock_store.assert_called_once_with(self.edri.router_queue)
        mock_store_instance.start.assert_called_once()
        self.assertEqual(self.edri.store, mock_store_instance)

    @patch('edri.Scheduler')
    def test_start_scheduler_with_jobs(self, mock_scheduler) -> None:
        mock_scheduler_instance = mock_scheduler.return_value
        mock_job = MagicMock(spec=Job)
        jobs = [mock_job]

        self.edri.start_scheduler(jobs)
        mock_scheduler.assert_called_once_with(self.edri.router_queue, jobs)
        mock_scheduler_instance.start.assert_called_once()
        self.assertEqual(self.edri.scheduler, mock_scheduler_instance)

    @patch('edri.Scheduler')
    def test_start_scheduler_without_jobs(self, mock_scheduler) -> None:
        mock_scheduler_instance = mock_scheduler.return_value

        self.edri.start_scheduler()
        mock_scheduler.assert_called_once_with(self.edri.router_queue, [])
        mock_scheduler_instance.start.assert_called_once()
        self.assertEqual(self.edri.scheduler, mock_scheduler_instance)

    @patch('edri.Broker')
    def test_broker_start(self, mock_broker) -> None:
        mock_broker_instance = mock_broker.return_value
        with patch("edri.Queue") as mock_queue:
            self.edri.start_broker([])
            mock_broker.assert_called_once_with(self.edri.router_queue, mock_queue.return_value, [])
        mock_broker_instance.start.assert_called_once()
        self.assertEqual(self.edri.broker, mock_broker_instance)

    @patch('edri.Listener')
    def test_start_api(self, mock_listener) -> None:
        self.edri.broker = MagicMock(spec=Broker)
        self.edri.broker.api_broker_queue = MagicMock(spec=Queue)
        mock_listener_instance = mock_listener.return_value
        self.edri.start_broker = MagicMock()
        with patch("edri.hasattr") as mock_hasattr:
            mock_hasattr.return_value = False
            self.edri.start_api()
        mock_listener.assert_called_once_with(self.edri.broker.api_broker_queue, [], CustomJSONEncoder)

        mock_listener_instance.start.assert_called_once()
        self.assertEqual(self.edri.api, mock_listener_instance)

    @patch('edri.Connector')
    def test_start_connector(self, mock_connector) -> None:
        mock_connector_instance = mock_connector.return_value
        self.edri.start_connector()
        mock_connector.assert_called_once_with(self.edri.router_queue, None)
        mock_connector_instance.start.assert_called_once()
        self.assertEqual(self.edri.connector, mock_connector_instance)

    @patch('edri.Router')
    def test_run(self, mock_router) -> None:
        mock_router_instance = mock_router.return_value
        mock_component = MagicMock(spec=ManagerBase)
        self.edri.add_component(mock_component)
        self.edri.start_watcher()

        with patch.object(mock_router_instance, 'run') as mock_run, patch.object(mock_router_instance, 'quit') as mock_quit:
            mock_run.side_effect = KeyboardInterrupt
            self.edri.run()
            mock_router.assert_called_once_with(self.edri.router_queue, self.edri.components)
            mock_component.start.assert_called_once_with(self.edri.router_queue)
            mock_run.assert_called_once()
            mock_quit.assert_called_once()