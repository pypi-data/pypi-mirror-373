import unittest
from dataclasses import dataclass

from edri.dataclass.directive import ResponseDirective
from edri.dataclass.response import Response, ResponseStatus


@dataclass
class ResponseDirective(ResponseDirective):
    directive_name: str


class TestResponse(unittest.TestCase):

    def test_initial_state(self):
        response = Response()
        self.assertEqual(response.get_status(), ResponseStatus.NONE)
        self.assertFalse(response.has_changed())
        self.assertEqual(response._directives, [])

    def test_set_status(self):
        response = Response()
        response.set_status(ResponseStatus.OK)
        self.assertEqual(response.get_status(), ResponseStatus.OK)

    def test_setattr_triggers_change(self):
        response = Response()
        response.some_attribute = "test"  # Set a new attribute
        self.assertTrue(response.has_changed())
        self.assertEqual(response.get_status(), ResponseStatus.OK)

    def test_add_directive(self):
        response = Response()
        directive = ResponseDirective("TestDirective")
        response.add_directive(directive)
        self.assertIn(directive, response._directives)
        self.assertEqual(len(response._directives), 1)

    def test_dict_property(self):
        response = Response()
        response.set_status(ResponseStatus.FAILED)
        self.assertEqual(response.as_dict(transform=True, keep_concealed=False), {"status": ResponseStatus.FAILED.name})