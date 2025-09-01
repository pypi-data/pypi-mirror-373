import unittest
from unittest.mock import AsyncMock
from dataclasses import dataclass
from typing import Any

from edri.api.handlers import BaseHandler
from edri.dataclass.directive import ResponseDirective
from edri.dataclass.event import Event, event

# Example Event and ResponseDirective classes for testing purposes
@event
class DummyEvent(Event):
    param1: str
    param2: int


@dataclass
class DummyResponseDirective(ResponseDirective):
    directive_type: str
    value: Any


# Concrete subclass of BaseHandler for testing
class ConcreteHandler(BaseHandler):
    async def response(self, status: ..., data: ..., *args, **kwargs) -> None:
        pass

    async def response_error(self, status: ..., response: ..., *args, **kwargs) -> None:
        pass

    def handle_directives(self, directives: list[ResponseDirective]) -> ...:
        return "handle_directives"


class TestBaseHandler(unittest.TestCase):

    def setUp(self):
        self.mock_send = AsyncMock()
        self.mock_receive = AsyncMock()
        self.mock_scope = {
            "query_string": b"",
        }
        # Use the concrete subclass for testing
        self.handler = ConcreteHandler(self.mock_scope, self.mock_receive, self.mock_send)
        self.handler.parameters = {'param1': 'test', 'param2': 42}

    def test_check_parameters_valid(self):
        # Test with valid parameters
        self.handler.check_parameters(DummyEvent)
        self.assertEqual(self.handler.parameters, {'param1': 'test', 'param2': 42})

    def test_check_parameters_invalid(self):
        # Test with invalid parameters
        self.handler.parameters['param2'] = 'invalid_type'
        with self.assertRaises(ValueError):
            self.handler.check_parameters(DummyEvent)

    def test_create_event_success(self):
        # Test event creation success
        event = self.handler.create_event(DummyEvent)
        self.assertIsInstance(event, DummyEvent)
        self.assertEqual(event.param1, 'test')
        self.assertEqual(event.param2, 42)

    def test_create_event_failure(self):
        # Test event creation failure due to invalid parameters
        self.handler.parameters['param2'] = 'invalid_type'
        with self.assertRaises(ValueError):
            self.handler.create_event(DummyEvent)

    def test_convert_type_basic(self):
        # Test type conversion for basic types
        self.assertEqual(self.handler.convert_type('42', int), 42)
        self.assertEqual(self.handler.convert_type('false', bool), False)
        self.assertEqual(self.handler.convert_type('3.14', float), 3.14)

    def test_convert_type_list(self):
        # Test type conversion for list
        self.assertEqual(self.handler.convert_type(['1', '2', '3'], list[int]), [1, 2, 3])

    def test_convert_type_invalid(self):
        # Test type conversion failure
        with self.assertRaises(TypeError):
            self.handler.convert_type('invalid', int)

    def test_handle_directives(self):
        # Prepare mock directives
        directives = [DummyResponseDirective(directive_type='test', value='data')]
        result = self.handler.handle_directives(directives)
        self.assertEqual(result, "handle_directives")

    def test_directive_handlers_property(self):
        # Test the directive handlers property
        handlers = self.handler.directive_handlers()
        self.assertIsInstance(handlers, dict)