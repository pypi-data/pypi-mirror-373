import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from edri.config.constant import SCHEDULER_TIMEOUT_MAX
from edri.dataclass.event import Event
from edri.dataclass.response import ResponseStatus
from edri.events.edri.scheduler import Set, Update, Cancel
from edri.utility import Storage
from edri.utility.manager import Scheduler, Job


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.router_queue = MagicMock()
        self.delay = 10
        self.jobs = [
            Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay)),
            Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay * 2)),
        ]
        self.scheduler = Scheduler(self.router_queue, self.jobs)
        self.scheduler.router_pipe = MagicMock()
        self.scheduler.jobs = MagicMock(spec=Storage)
        self.scheduler.initial_jobs = self.jobs
        self.scheduler.logger = MagicMock()

    def test_after_start(self):
        with patch.object(self.scheduler, "jobs", new_callable=Storage):
            self.scheduler.after_start()
            for job in self.jobs:
                self.assertIn(job, self.scheduler.jobs.values())

    def test_solve_req_set(self):
        event = MagicMock(spec=Set)
        event.identifier = "job1"
        event.when = datetime.now() + timedelta(seconds=30)
        event.repeat = None
        event.response = MagicMock()
        event.event = MagicMock(spec=Event)

        self.scheduler.solve_req_set(event)
        self.scheduler.jobs.append.assert_called_once()
        self.scheduler.logger.debug.assert_called_with("New scheduled task: %s", self.scheduler.jobs.append.return_value)

        mock_key_error = KeyError()
        self.scheduler.jobs.append.side_effect = [mock_key_error]
        self.scheduler.solve_req_set(event)
        self.scheduler.logger.warning.assert_called_with("Scheduled task already exists: %s", event.identifier, exc_info=mock_key_error)

    def test_solve_req_update(self):
        event = MagicMock(spec=Update)
        event.identifier = "job1"
        event.event = MagicMock(spec=Event)
        event.when = datetime.now() + timedelta(seconds=40)
        event.repeat = timedelta(minutes=5)
        event.response = MagicMock()

        job = Job(event=MagicMock(spec=Event), when=datetime.now(), repeat=None)
        self.scheduler.jobs.get.return_value = job

        self.scheduler.solve_req_update(event)

        self.assertEqual(job.event, event.event)
        self.assertEqual(job.when, event.when)
        self.assertEqual(job.repeat, event.repeat)
        self.scheduler.logger.debug.assert_called_with("Scheduled task %s was updated", event.identifier)

    def test_solve_req_update_not_found(self):
        event = MagicMock(spec=Update)
        event.identifier = "job1"
        event.response = MagicMock()

        self.scheduler.jobs.get.return_value = None

        self.scheduler.solve_req_update(event)

        event.response.set_status.assert_called_once_with(ResponseStatus.FAILED)
        self.scheduler.logger.debug.assert_called_with("Scheduled task %s was not found", event.identifier)

    def test_solve_req_cancel(self):
        event = MagicMock(spec=Cancel)
        event.identifier = "job1"
        event.response = MagicMock()

        self.scheduler.solve_req_cancel(event)

        del self.scheduler.jobs[event.identifier]
        self.scheduler.logger.debug.assert_called_with("Scheduled task %s was cancelled", event.identifier)

    def test_solve_req_cancel_not_found(self):
        event = MagicMock(spec=Cancel)
        event.identifier = "job1"
        event.response = MagicMock()

        self.scheduler.jobs = MagicMock(spec=Storage)
        del self.scheduler.jobs[event.identifier]
        self.scheduler.jobs.__delitem__.side_effect = KeyError

        self.scheduler.solve_req_cancel(event)

        self.scheduler.logger.debug.assert_called_with("Scheduled task %s was not found", event.identifier)

    def test_get_next_job(self):
        self.scheduler.jobs = {
            "job1": Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay)),
            "job2": Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay * 2)),
        }

        key, job = self.scheduler.get_next_job()
        self.assertEqual(key, "job1")

        self.scheduler.jobs = {
            "job1": Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay)),
        }

        key, job = self.scheduler.get_next_job()
        self.assertEqual(key, "job1")

        self.scheduler.jobs = {
            "job1": Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay * 2)),
            "job2": Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay)),
        }

        key, job = self.scheduler.get_next_job()
        self.assertEqual(key, "job2")

        self.scheduler.jobs = {}

        key, job = self.scheduler.get_next_job()
        self.assertEqual(key, "")
        self.assertEqual(job, None)

    def test_run_pending(self):
        job1 = Job(event=MagicMock(spec=Event), when=datetime.now() - timedelta(seconds=self.delay))
        job2 = Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay * 2))
        self.scheduler.jobs = {
            "job1": job1,
            "job2": job2,
        }

        self.scheduler.run_pending()

        self.router_queue.put.assert_called_once_with(job1.event)
        self.scheduler.logger.debug.assert_called_with("Scheduled task %s was completed", "job1")
        self.assertFalse("job1" in self.scheduler.jobs)

    def test_run_pending_repeat(self):
        repeat = timedelta(seconds=self.delay/2)
        when = datetime.now() - timedelta(seconds=self.delay)
        job1 = Job(event=MagicMock(spec=Event), when=when, repeat=repeat)
        job2 = Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay * 2))
        self.scheduler.jobs = {
            "job1": job1,
            "job2": job2,
        }

        self.scheduler.run_pending()

        self.router_queue.put.assert_called_once_with(job1.event)
        self.assertTrue("job1" in self.scheduler.jobs)
        job = self.scheduler.jobs["job1"]
        self.assertEqual(job.repeat, repeat)
        self.assertAlmostEqual(job.when, when + repeat)

    def test_run_resolver(self):
        with patch("edri.utility.manager.scheduler.datetime") as mock_datetime:
            now = datetime.now()
            mock_datetime.now.return_value = now
            self.scheduler.jobs = {
                "job1": Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay)),
                "job2": Job(event=MagicMock(spec=Event), when=datetime.now() + timedelta(seconds=self.delay * 2)),
            }

            self.scheduler.router_pipe.poll.return_value = True
            self.scheduler.router_pipe.recv.return_value = MagicMock(spec=Event())
            self.scheduler.resolve = MagicMock(side_effect=StopIteration)

            with self.assertRaises(StopIteration):
                self.scheduler.run_resolver()

            actual_timeout = self.scheduler.router_pipe.poll.call_args[1]["timeout"]
            self.assertAlmostEqual(actual_timeout, self.delay, delta=1)
            ###

            mock_datetime.now.return_value = now + timedelta(seconds=self.delay)

            with self.assertRaises(StopIteration):
                self.scheduler.run_resolver()

            self.scheduler.router_pipe.recv.assert_called()
            self.scheduler.router_pipe.recv.reset_mock()

            actual_timeout = self.scheduler.router_pipe.poll.call_args_list[0][1]["timeout"]
            self.assertAlmostEqual(actual_timeout, self.delay, delta=1)
            ###

            mock_datetime.now.return_value = now - timedelta(seconds=SCHEDULER_TIMEOUT_MAX)
            with self.assertRaises(StopIteration):
                self.scheduler.run_resolver()

            self.scheduler.router_pipe.recv.assert_called()
            self.scheduler.router_pipe.recv.reset_mock()

            actual_timeout = self.scheduler.router_pipe.poll.call_args[1]["timeout"]
            self.assertAlmostEqual(actual_timeout, SCHEDULER_TIMEOUT_MAX, delta=1)

            self.scheduler.jobs = {}
            mock_datetime.now.return_value = now - timedelta(seconds=SCHEDULER_TIMEOUT_MAX)
            with self.assertRaises(StopIteration):
                self.scheduler.run_resolver()

            self.scheduler.router_pipe.recv.assert_called()
            self.scheduler.router_pipe.recv.reset_mock()

            actual_timeout = self.scheduler.router_pipe.poll.call_args[1]["timeout"]
            self.assertAlmostEqual(actual_timeout, SCHEDULER_TIMEOUT_MAX, delta=1)
            ###

            with patch.object(self.scheduler, "run_pending", side_effect=KeyboardInterrupt):
                self.scheduler.run_resolver()

            self.scheduler.router_pipe.recv.assert_not_called()
