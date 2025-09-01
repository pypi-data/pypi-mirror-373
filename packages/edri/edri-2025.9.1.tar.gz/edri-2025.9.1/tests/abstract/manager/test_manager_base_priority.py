import unittest
from logging import getLogger
from multiprocessing.queues import Queue
from typing import Type
from unittest.mock import MagicMock, patch
from multiprocessing.connection import Connection
from threading import Thread
from queue import PriorityQueue

from edri.dataclass.event import Event
from edri.abstract import ManagerPriorityBase
from edri.abstract.manager.manager_priority_base import QueueItem
from edri.abstract.manager.worker import Worker
from edri.events.edri.manager import WorkerQuit
from edri.utility import Storage


class DummyManagerPriorityBase(ManagerPriorityBase):
    def get_priority(self, event_type: Type[Event]) -> int:
        return 1


class TestManagerPriorityBase(unittest.TestCase):
    def setUp(self):
        self.router_queue = MagicMock(spec=Queue)
        self.logger = MagicMock(spec=getLogger(__name__))
        self.manager = DummyManagerPriorityBase(self.router_queue, self.logger)
        self.manager.resolve = MagicMock()

        self.waking_up_reader = MagicMock()
        self.waking_up_writer = MagicMock()
        self.manager.waking_up = self.waking_up_reader, self.waking_up_writer
        self.manager.event_queue = MagicMock(scope=PriorityQueue)
        self.manager._workers = Storage()
        self.manager.router_pipe = MagicMock(spec=Connection)

        self.worker_pipe = MagicMock(spec=Connection)
        self.worker_name = "TestWorker"
        self.event = MagicMock(spec=Event)
        self.worker = Worker(pipe=self.worker_pipe, event=self.event, worker=MagicMock())
        self.worker.worker.name = self.worker_name
        self.worker_key = self.manager._workers.append(self.worker, self.worker_name)

    def test_prepare_initializes_components(self):
        self.manager._prepare()
        self.assertIsInstance(self.manager.event_queue, PriorityQueue)
        self.assertIsInstance(self.manager.event_worker, Thread)
        self.assertIsInstance(self.manager.waking_up, tuple)
        self.manager.event_worker_stop.set()

    def test_start_worker_wakes_up_manager(self):
        pipe = MagicMock(scope=Connection)
        event = MagicMock(scope=Event)
        resolver = MagicMock()
        worker = Worker(pipe, event, resolver)

        with patch("edri.abstract.ManagerBase.start_worker") as mock_start_worker:
            self.manager.start_worker(event, resolver)
            self.waking_up_writer.send.assert_called_once_with(None)
            mock_start_worker.assert_called_once()

    @patch("edri.abstract.manager.manager_priority_base.wait")
    def test_run_resolver_handles_events(self, mock_wait):
        mock_pipe = MagicMock(scope=Connection)
        event = MagicMock(scope=Event)
        mock_pipe.recv = MagicMock(return_value=event)
        self.manager.router_pipe = mock_pipe
        self.manager.get_pipes = MagicMock(return_value=[mock_pipe])

        mock_wait.return_value = [mock_pipe]

        with patch.object(self.manager.event_queue, "put", side_effect=StopIteration) as mock_put, self.assertRaises(StopIteration):
            self.manager.run_resolver()

        mock_put.assert_called_once_with(QueueItem(1, mock_pipe.recv()))

    def test_command_handler_processes_event(self):
        event = MagicMock(scope=Event)
        queue_item = QueueItem(priority=1, item=event)
        self.manager.event_queue.get.return_value = queue_item
        self.manager.event_worker_stop = MagicMock()
        self.manager.event_worker_stop.is_set.return_value = False

        with patch.object(self.manager, "resolve", side_effect=StopIteration) as mock_resolve, self.assertRaises(StopIteration) :
            self.manager.command_handler()
        mock_resolve.assert_called_once_with(event)

    def test_additional_pipes_includes_waking_up(self):
        additional_pipes = self.manager.additional_pipes
        self.assertIn(self.manager.waking_up[0], additional_pipes)

    def test_run_resolver(self):
        event = MagicMock(spec=Event)
        event_worker_quit = MagicMock(spec=WorkerQuit)

        self.manager.router_pipe.recv.return_value = event
        pipe_non_worker = MagicMock(spec=Connection)
        pipe_non_worker.recv.side_effect = [event, EOFError, OSError]
        self.worker_pipe.recv.side_effect = [event, event_worker_quit]

        with (patch("edri.abstract.manager.manager_priority_base.wait",
                    side_effect=[[self.manager.router_pipe, pipe_non_worker], [self.waking_up_reader], [pipe_non_worker], [pipe_non_worker], [self.worker_pipe],
                                 [self.worker_pipe]]),
              patch.object(self.manager, "resolve_callback_pipe") as mock_resolve_callback_pipe,
              patch.object(self.manager, "resolve_callback_worker") as mock_resolve_callback_worker,
              patch.object(self.manager, "_remove_worker", side_effect=[KeyboardInterrupt]) as mock_remove_worker,
              patch("edri.abstract.manager.manager_priority_base.sleep") as mock_sleep,
              patch.object(self.manager, "get_pipes") as mock_get_pipes):
            mock_get_pipes.side_effect = [[], [self.manager.router_pipe, pipe_non_worker], [self.manager.router_pipe, pipe_non_worker],
                                          [self.manager.router_pipe, pipe_non_worker], [self.manager.router_pipe, pipe_non_worker],
                                          [self.manager.router_pipe, pipe_non_worker], [self.manager.router_pipe, pipe_non_worker]]

            self.manager.run_resolver()

        self.waking_up_reader.recv.assert_called_once()
        mock_sleep.assert_called_once_with(1)
        self.manager.router_pipe.recv.assert_called_once()
        mock_resolve_callback_pipe.assert_called_once_with(event, pipe_non_worker)
        mock_resolve_callback_worker.assert_called_once_with(event, self.worker)
        mock_remove_worker.assert_called_once_with(self.worker_key)