import unittest
from unittest.mock import MagicMock, patch, call
from multiprocessing.connection import Connection
from edri.dataclass.event import Event
from edri.config.constant import STREAM_CLOSE_MARK
from edri.events.edri.manager import StreamCreate, StreamMessage, StreamClose
from edri.events.edri.manager.worker_quit import WorkerQuit
from edri.abstract.worker import Worker
from tests.dataclass.event.test_response import ResponseStatus


class DummyEvent(Event):
    pass

class DummyWorker(Worker[DummyEvent]):
    def do(self):
        pass


class TestWorker(unittest.TestCase):
    def setUp(self):
        self.manager_pipe = MagicMock(spec=Connection)
        self.event = DummyEvent()
        self.stream_key = "random_stream"
        self.event._stream = self.stream_key
        self.worker = DummyWorker(self.manager_pipe, self.event, "TestWorker")
        self.worker.logger = MagicMock()

    def test_init(self):
        self.assertEqual(self.worker._name, "TestWorker")
        self.assertEqual(self.worker._manager_pipe, self.manager_pipe)
        self.assertEqual(self.worker.event, self.event)
        self.assertEqual(self.worker._stream_key, self.stream_key)

    def test_event_send(self):
        event = DummyEvent()
        with patch.object(self.worker.logger, 'debug') as mock_logger:
            self.worker.event_send(event)
            self.manager_pipe.send.assert_called_once_with(event)
            mock_logger.assert_called_once_with("Event was sent: %s", event)

    def test_event_receive(self):
        event = DummyEvent()
        event_buffer = MagicMock(spec=Event)
        event_stream_close_wrong = StreamClose()
        event_stream_close = StreamClose()
        event_stream_close._stream = self.stream_key
        self.manager_pipe.recv.side_effect = [event_stream_close_wrong, event_stream_close, event]
        self.worker._buffer.append(event_buffer)


        received_event = self.worker.event_receive()
        self.assertEqual(received_event, event_buffer)

        received_event = self.worker.event_receive()
        self.assertEqual(received_event, event)

    # def test_stream_create(self):
    #     event = DummyEvent()
    #     stream_create_event = StreamCreate(event=event)
    #
    #     self.manager_pipe.recv.side_effect = [stream_create_response]
    #     self.worker.event_receive = MagicMock(return_value=stream_create_response)
    #
    #     self.worker.event_send = MagicMock()
    #     created = self.worker.stream_create(event)
    #
    #     self.worker.event_send.assert_called_once_with(stream_create_event)
    #     self.worker.event_receive.assert_called_once()
    #     self.assertTrue(created)
    #     self.assertEqual(self.worker._stream_key, "stream_key")
    #
    # def test_stream_exists(self):
    #     self.assertTrue(self.worker.stream_exists)
    #     self.worker._stream_key = None
    #     self.assertFalse(self.worker.stream_exists)
    #
    # def test_stream_poll(self):
    #     event = MagicMock(spec=Event)
    #     self.manager_pipe.poll.return_value = True
    #     self.manager_pipe.recv.return_value = event
    #
    #     polled = self.worker.stream_poll()
    #     self.assertTrue(polled)
    #     self.assertEqual(self.worker._stream_buffer, event)
    #
    # def test_stream_wait(self):
    #     event = MagicMock(spec=Event)
    #     self.worker._stream_key = "stream_key"
    #     event._stream = MagicMock(spec=str)
    #     event._stream.endswith.side_effect = [False]
    #     self.manager_pipe.poll.return_value = True
    #     self.manager_pipe.recv.return_value = event
    #
    #     waited = self.worker.stream_wait(timeout=1)
    #     self.assertTrue(waited)
    #     self.assertEqual(self.worker._stream_buffer, event)
    #
    # def test_stream_receive(self):
    #     event = DummyEvent()
    #     self.worker._stream_buffer = event
    #
    #     received_event = self.worker.stream_receive()
    #     self.assertEqual(received_event, event)
    #     self.assertIsNone(self.worker._stream_buffer)
    #
    #     with self.assertRaises(BlockingIOError):
    #         self.worker.stream_receive()
    #
    # def test_stream_send(self):
    #     event = DummyEvent()
    #     stream_event = StreamMessage(event=event)
    #     self.worker.stream_send(event)
    #     self.manager_pipe.send.assert_called_once_with(stream_event)
    #
    # def test_stream_close(self):
    #     self.worker._stream_key = "stream_key"
    #     with patch.object(self.worker, 'event_send') as mock_send:
    #         closed = self.worker.stream_close()
    #         self.assertTrue(closed)
    #         mock_send.assert_called_once()

    def test_run(self):
        with patch.object(self.worker, 'do') as mock_do:
            self.worker.run()
            mock_do.assert_called_once()

    def test_run_with_exception(self):
        error = Exception("Error")
        with patch.object(self.worker, 'do', side_effect=error) as mock_do:
            self.worker.run()
            mock_do.assert_called_once()
            self.worker.logger.error.assert_called_once_with("Worker %s was closed unexpectedly", self.worker._name, exc_info=error)
            event_wq = WorkerQuit()
            self.manager_pipe.send.assert_called_once_with(event_wq)