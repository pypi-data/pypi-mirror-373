import unittest
from dataclasses import fields
from inspect import ismethod
from logging import getLogger
from multiprocessing import Process
from multiprocessing.connection import Connection
from multiprocessing.queues import Queue
from unittest.mock import MagicMock, patch, PropertyMock

from edri.abstract import ManagerBase, request, response
from edri.abstract.manager.manager_base import ManagerBaseMeta
from edri.abstract.manager.worker import Worker
from edri.dataclass.event import Event, Timing, event
from edri.events.edri.router import Subscribe, HealthCheck
from edri.events.edri.store import Get
from edri.utility import Storage
from tests.events.test import Ping, Ping2
from tests.events.test.event_request import EventRequest


# Sample events
@event
class TestRequest(Event):
    _handled: bool = False

@event
class TestResponse(Event):
    _processed: bool = False

def bad_method(event): pass
bad_method.__purpose__ = "invalid"


def dummy(event): pass
dummy.__purpose__ = "request"

class TestManagerBaseMeta(unittest.TestCase):

    def test_decorated_methods_renamed_and_registered(self):
        class MyManager(ManagerBase):
            @request
            def handle_request(self, event: TestRequest):
                event._handled = True

            @response
            def handle_response(self, event: TestResponse):
                event._processed = True

        self.assertTrue(hasattr(MyManager, 'solve_req_handle_request'))
        self.assertTrue(hasattr(MyManager, 'solve_res_handle_response'))
        self.assertFalse(hasattr(MyManager, 'handle_request'))
        self.assertFalse(hasattr(MyManager, 'handle_response'))

        mgr = MyManager()
        mgr._prepare_resolvers()

        self.assertIn(TestRequest, mgr._requests)
        self.assertIn(TestResponse, mgr._responses)

        # Ensure the methods actually work
        req_event = TestRequest()
        res_event = TestResponse()
        mgr._requests[TestRequest](req_event)
        mgr._responses[TestResponse](res_event)

        self.assertTrue(req_event._handled)
        self.assertTrue(res_event._processed)

    def test_conflicting_method_name_raises_key_error(self):
        with self.assertRaises(KeyError):
            class ConflictingManager(metaclass=ManagerBaseMeta):
                solve_req_dummy = lambda self, event: None
                dummy = dummy

    def test_invalid_purpose_raises_value_error(self):
        with self.assertRaises(ValueError):
            class InvalidPurposeManager(metaclass=ManagerBaseMeta):
                bad_method = bad_method

    def test_undecorated_methods_are_untouched(self):
        class PlainManager(metaclass=ManagerBaseMeta):
            def not_special(self, event: Event):
                pass

        self.assertTrue(hasattr(PlainManager, 'not_special'))

class TestManagerBase(unittest.TestCase):

    def setUp(self):
        self.router_queue = MagicMock(spec=Queue)
        self.logger = MagicMock(spec=getLogger(__name__))
        self.manager = ManagerBase(router_queue=self.router_queue, logger=self.logger)
        self.manager._workers = Storage[Worker]()
        self.manager.router_pipe = MagicMock(spec=Connection)

        self.event = Event()
        self.worker_pipe = MagicMock(spec=Connection)
        self.worker_name = "TestWorker"
        self.worker = Worker(pipe=self.worker_pipe, worker=MagicMock(), event=self.event)
        self.worker.worker.name = self.worker_name
        self.worker_key = self.manager._workers.append(self.worker, self.worker_name)

    def test_subscribe(self):
        self.manager._subscribe()
        self.logger.info.assert_called_once_with("No events to subscribe!")

        event_type = MagicMock(spec=Event)
        pipe = MagicMock(spec=Connection)
        response = MagicMock(spec=[field.name for field in fields(Subscribe)])
        response_wrong = Ping()
        pipe.recv.side_effect = [response_wrong, response, response]
        self.manager._requests = {event_type: MagicMock()}
        self.manager._responses = {event_type: MagicMock()}
        self.manager._from_time = MagicMock()
        self.manager.router_pipe = MagicMock(spec=Connection)

        with (patch("edri.abstract.manager.manager_base.Pipe", return_value=(pipe, pipe)),
              patch("edri.abstract.manager.manager_base.Subscribe", new=MagicMock) as mock_subscribe):
            self.manager._subscribe()

        self.logger.debug.assert_any_call("Count of events to register: %s", len(self.manager._requests) + len(self.manager._responses))
        self.logger.debug.assert_any_call("Event was registered: %s", response.event_type)
        self.router_queue.put.assert_called()
        self.assertEqual(len(self.manager._unresolved), 1)
        self.logger.debug.assert_any_call("Received %s undelivered events!", 1)
        pipe.close.assert_called_once()

    def test_resolve_undelivered_events(self):
        event = MagicMock(spec=Event)
        event._timing = MagicMock(spec=Timing)
        self.manager._unresolved = [event]

        with patch.object(self.manager, "resolve") as mock_resolve:
            self.manager._resolve_undelivered_events()
            mock_resolve.assert_called_once_with(event)

        self.assertFalse(hasattr(self.manager, "_unresolved"), msg=f"obj lacking an attribute. {self.manager=}, _unresolved")

        self.manager._unresolved = []
        self.manager._resolve_undelivered_events()
        self.logger.debug.assert_called_with("No unresolved events!")

    # @patch("edri.abstract.manager.manager_base.dir")
    def test_prepare_resolvers(self):
        class TestClass:
            def func(self, event: Ping):
                pass

            def func2(self, event: Ping2):
                pass

            def bad_func(self, message: Ping):
                pass

            def bad_func2(self, event):
                pass

        test_class = TestClass()

        self.manager.solve_req_func = test_class.func
        self.manager.solve_res_func = test_class.func2
        self.manager._prepare_resolvers()
        self.assertIn(Ping, self.manager._requests)
        self.assertIn(Ping2, self.manager._responses)
        self.assertTrue(ismethod(self.manager._requests[Ping]))
        self.assertTrue(ismethod(self.manager._responses[Ping2]))

        self.manager.solve_req_bad_func = test_class.bad_func
        with self.assertRaises(AttributeError):
            self.manager._prepare_resolvers()

        del self.manager.solve_req_bad_func

        self.manager.solve_req_bad_func = test_class.bad_func2
        with self.assertRaises(AttributeError):
            self.manager._prepare_resolvers()

        del self.manager.solve_req_bad_func

        with self.assertRaises(TypeError):
            self.manager._prepare_resolvers()
        self.manager._requests = {}

        with self.assertRaises(TypeError):
            self.manager._prepare_resolvers()
        self.manager._requests = {}
        self.manager._responses = {}

        self.manager.solve_req_bad_func = "never"
        self.manager._prepare_resolvers()
        self.logger.warning.assert_called_once_with("%s suppose to be a method", "solve_req_bad_func")

    def test_subscribe_static_resolvers(self):
        with patch.object(self.manager, "_responses") as mock_responses:
            original_get = MagicMock()
            mock_responses.get.return_value = original_get
            self.manager._subscribe_static_resolvers()

            mock_responses.__setitem__.assert_called_once_with(Get, self.manager.store_get)

        self.assertIn(HealthCheck, self.manager._requests)
        self.assertEqual(self.manager._requests[HealthCheck], self.manager.health_check)

        self.assertEqual(self.manager._store_get, original_get)

    def test_resolve_callback_worker(self):
        event = MagicMock(spec=Event)
        event._timing = MagicMock(spec=Timing)
        self.manager.resolve_callback_worker(event, self.worker)
        self.router_queue.put.assert_called_once_with(event)
        self.assertEqual(event._worker, self.worker.worker.name)

    def test_remove_worker(self):
        with patch.object(self.manager, "_workers") as mock_workers:
            mock_workers.__getitem__.return_value = self.worker
            self.manager._remove_worker(self.worker_key)
            self.worker_pipe.close.assert_called_once()
            mock_workers.pop.assert_called_once_with(self.worker_key)

    def test_resolve(self):
        def add_response(event: EventRequest):
            event.response._changed = True
            event.has_response.return_value = True

        event = MagicMock(spec=Event)
        event._stream = None
        event.has_response.return_value = False

        event_response = MagicMock(spec=Event)
        event_response._stream = None
        resolver = MagicMock(side_effect=add_response)

        self.manager._requests[event.__class__] = resolver
        event.has_response.return_value = False

        self.manager.resolve(event)

        resolver.assert_called_once_with(event)
        self.router_queue.put.assert_called_once_with(event)

        event.has_response.return_value = True
        with patch.object(self.manager, "resolve_unknown") as mock_resolve_unknown:
            self.manager.resolve(event)
            mock_resolve_unknown.assert_called_once_with(event)

    @patch('edri.abstract.manager.manager_base.ManagerBase.additional_pipes', new_callable=PropertyMock)
    def test_get_pipes(self, mock_additional_pipes):
        event = MagicMock(spec=Event)
        mock_worker_pipe_1 = MagicMock(spec=Connection)
        mock_worker_pipe_2 = MagicMock(spec=Connection)
        mock_worker = {
            'worker1': Worker(event=event, pipe=mock_worker_pipe_1, worker=MagicMock()),
            'worker2': Worker(event=event, pipe=mock_worker_pipe_2, worker=MagicMock())
        }
        self.manager._workers = MagicMock()
        self.manager._workers.values.return_value = mock_worker.values()

        mock_additional_pipes.return_value = {MagicMock(spec=Connection)}

        pipes = self.manager.get_pipes()

        expected_pipes = {self.manager.router_pipe, mock_worker_pipe_1, mock_worker_pipe_2, *mock_additional_pipes.return_value}
        self.assertEqual(pipes, expected_pipes)

    # def test_start_worker(self):
    #     # Mock the event, process, resolver, pipe, and environment
    #     event = MagicMock(spec=Event)
    #     process = MagicMock(spec=Process)
    #     pipe = MagicMock(spec=Connection)
    #     environment = Path('/mock/environment')
    #
    #     # Mock the resolver as a class, not an instance
    #     resolver_class = MagicMock(spec=WorkerProcess)
    #     resolver_class.__name__ = 'TestWorkerProcess'  # Add a name to make it look like a real class
    #
    #     # Ensure that resolver_class behaves like a class and can be instantiated
    #     resolver_instance = MagicMock(spec=WorkerProcess)  # This is an instance of the mocked class
    #     resolver_class.return_value = resolver_instance  # When instantiated, return this instance
    #
    #     # Mock the Pipe and randint function
    #     with patch("edri.abstract.manager.manager_base.Pipe", return_value=(pipe, pipe)), \
    #             patch("edri.abstract.manager.manager_base.randint", return_value=12345), \
    #             patch("edri.abstract.manager.manager_base.get_context") as mock_get_context, \
    #             patch("builtins.issubclass") as mock_issubclass:
    #         # Mock issubclass to return True for the resolver class
    #         mock_issubclass.side_effect = lambda cls, base: cls is WorkerProcess  # Returns True if cls is WorkerProcess
    #
    #         # Mock the context and process creation for WorkerProcess subclass
    #         mock_ctx = MagicMock()
    #         mock_get_context.return_value = mock_ctx
    #         mock_ctx.Process = MagicMock(spec=Process)
    #
    #         # Mock the Storage class and appending workers
    #         self.manager._workers = Storage()
    #
    #         # Create a mock worker and mock the worker attribute with a name
    #         mock_worker = MagicMock()
    #         mock_worker.worker = MagicMock()  # Mock the 'worker' attribute
    #         mock_worker.worker.name = f"{self.manager.name}-Worker_54321"  # Assign the name to the 'worker' mock
    #
    #         # Mock the 'values' method to return a list of workers, with one having the same name
    #
    #         # Call the start_worker method
    #         worker = self.manager.start_worker(event, resolver_class, environment=environment)
    #
    #         # Check if the resolver class was initialized with the right parameters
    #         resolver_class.assert_called_once_with(pipe, event, f"{self.manager.name}-Worker_12345")
    #
    #         # Check if the worker process started
    #         resolver_instance.start.assert_called_once()
    #
    #         # Check if the worker was added to _workers
    #         self.manager._workers.append.assert_called_once()
    #
    #         # Verify that pipe.close() was called
    #         pipe.close.assert_called_once()
    #
    #         # Verify the worker's name is set correctly
    #         self.assertEqual(worker.worker.name, f"{self.manager.name}-Worker_12345")
    #
    #         # Verify the worker was started
    #         worker.worker.start.assert_called_once()
    #
    #         # If the resolver is a WorkerProcess subclass, make sure we check pipe_remote.close()
    #         if mock_issubclass(resolver_class, WorkerProcess):
    #             pipe.close.assert_called_once()
    #
    #         # Ensure that the worker was logged correctly
    #         self.logger.debug.assert_any_call("Worker %s has been started", worker.worker.name)

    def test_health_check(self):
        event = MagicMock(spec=HealthCheck)
        self.manager.health_check(event)
        self.assertEqual(event.response.name, self.manager.name)

    def test_store_get_with_worker(self):
        self.event = MagicMock(spec=Get)
        self.event._worker = self.worker_name
        self.manager.store_get(self.event)

        self.worker_pipe.send.assert_called_once_with(self.event)

    def test_store_get_with_no_worker_and_store_get_defined(self):
        self.event = MagicMock(spec=Get)
        self.event._worker = None
        self.manager._store_get = MagicMock()

        self.manager.store_get(self.event)

        self.manager._store_get.assert_called_once_with(self.event)

    def test_store_get_with_no_worker_and_store_get_not_defined(self):
        self.event = MagicMock(spec=Get)
        self.event._worker = None

        with patch.object(self.manager, "_store_get", None):
            self.manager.store_get(self.event)

        self.assertFalse(self.worker_pipe.send.called)

    @patch('edri.abstract.manager.manager_base.ManagerBase.run_resolver')
    @patch('edri.abstract.manager.manager_base.ManagerBase._resolve_undelivered_events')
    @patch('edri.abstract.manager.manager_base.ManagerBase.after_start')
    @patch('edri.abstract.manager.manager_base.ManagerBase._prepare')
    @patch('edri.abstract.manager.manager_base.ManagerBase._subscribe')
    @patch('edri.abstract.manager.manager_base.ManagerBase._subscribe_static_resolvers')
    @patch('edri.abstract.manager.manager_base.ManagerBase._prepare_resolvers')
    def test_run(self, mock_prepare_resolvers, mock_subscribe_static_resolvers,
                 mock_subscribe, mock_prepare, mock_after_start,
                 mock_resolve_undelivered_events, mock_run_resolver):
        self.manager.run()
        self.logger.debug.assert_called_once_with(f"{self.manager.name} is running!")
        mock_prepare_resolvers.assert_called_once()
        mock_subscribe_static_resolvers.assert_called_once()
        mock_subscribe.assert_called_once()
        mock_prepare.assert_called_once()
        mock_after_start.assert_called_once()
        mock_resolve_undelivered_events.assert_called_once()
        mock_run_resolver.assert_called_once()

    @patch.object(Process, "start")
    def test_start(self, mock_start):
        self.manager.start(self.router_queue)

        self.assertEqual(self.manager.router_queue, self.router_queue)
        mock_start.assert_called_once()

        self.manager.router_queue = None
        with self.assertRaises(RuntimeError):
            self.manager.start()
