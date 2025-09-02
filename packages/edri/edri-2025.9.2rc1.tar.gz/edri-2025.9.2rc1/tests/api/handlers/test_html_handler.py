import unittest
from unittest.mock import AsyncMock, MagicMock, call
from http import HTTPStatus
from jinja2 import TemplateNotFound, TemplateSyntaxError

from edri.api import Headers
from edri.dataclass.directive.html import RedirectResponseDirective
from edri.dataclass.event import Event
from edri.utility import NormalizedDefaultDict
from edri.api.handlers.html_handler import HTMLHandler

class TestHTMLHandler(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mock dependencies
        HTMLHandler.url_root = None
        self.mock_send = AsyncMock()
        self.mock_receive = AsyncMock()
        self.mock_scope = {'query_string': b'', 'path': '/test', 'method': 'GET'}
        self.mock_headers = NormalizedDefaultDict[str, Headers](list)
        self.mock_headers["cookie"] = "test_cookie=test_value"

        # Instantiate HTMLHandler for testing
        self.handler = HTMLHandler(self.mock_scope, self.mock_receive, self.mock_send, self.mock_headers)
        self.handler.environment = MagicMock()  # Mocking the Jinja2 Environment
        self.handler.event_type_extensions = MagicMock()

    async def test_response_with_event(self):
        # Create a mock Event
        event = MagicMock(spec=Event)
        event.get_response.return_value.as_dict.return_value = {'some_key': 'some_value'}

        # Mock template rendering behavior
        mock_template = MagicMock()
        mock_template.render.return_value = 'Rendered Content'
        self.handler.environment.get_template.return_value = mock_template

        # Call response method with Event data
        await self.handler.response(HTTPStatus.OK, event, headers=self.mock_headers)

        self.handler.environment.get_template.assert_called_once()
        mock_template.render.assert_called_once()
        self.handler.send.assert_any_call({
            'type': 'http.response.start',
            'status': HTTPStatus.OK,
            'headers': self.handler.get_headers_binary(self.mock_headers),
        })

    async def test_response_template_not_found(self):
        # Simulate TemplateNotFound exception
        self.handler.environment = MagicMock()

        error_template = MagicMock()
        error_template.render.return_value = "<html>Error page</html>"  # Important fix

        self.handler.environment.get_template.side_effect = [
            TemplateNotFound("template.j2"),  # Initial template not found
            error_template  # Error template found
        ]

        headers = MagicMock()
        event = MagicMock(spec=Event)

        with self.assertLogs(self.handler.logger, level="ERROR") as log:
            await self.handler.response(HTTPStatus.OK, event, headers=headers)

        self.assertIn("Template was not found", "\n".join(log.output))

        # Assert get_template was called twice
        self.assertEqual(self.handler.environment.get_template.call_count, 2)

        # Construct expected headers
        body_bytes = error_template.render.return_value.encode()
        expected_headers = self.handler.get_headers_binary(headers)
        expected_headers.append((b'content-type', b'text/html'))
        expected_headers.append((b'content-length', str(len(body_bytes)).encode()))

        self.handler.send.assert_has_calls([
            call({
                'type': 'http.response.start',
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'headers': expected_headers,
            }),
            call({
                'type': 'http.response.body',
                'body': body_bytes,
                'more_body': False
            })
        ])

    async def test_response_template_syntax_error(self):
        # Simulate TemplateSyntaxError exception
        self.handler.environment = MagicMock()
        error_template = MagicMock()
        self.handler.environment.get_template.side_effect = [
            TemplateSyntaxError("Syntax Error", lineno=1, name="template.j2"),
            error_template  # Error template found
        ]
        headers = MagicMock()

        event = MagicMock(spec=Event)
        await self.handler.response(HTTPStatus.OK, event, headers=headers)

        # Assert get_template was called twice: first for the initial template, then for the error template
        self.assertEqual(self.handler.environment.get_template.call_count, 2)

        # Verify the correct calls to send were made
        headers = self.handler.get_headers_binary(headers)
        headers.append((b'content-type', b'text/html'))
        headers.append((b'content-length', b'0'))
        self.handler.send.assert_has_calls([
            call({
                'type': 'http.response.start',
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'headers': headers,
            }),
            call({
                'type': 'http.response.body',
                'body': error_template.render().encode(),
                'more_body': False
            })
        ])

    async def test_redirect_response(self):
        # Create a mock redirect directive
        directive = RedirectResponseDirective('https://example.com')

        # Call method to test redirect behavior
        status, headers = self.handler.handle_directives([directive])

        self.assertEqual(status, HTTPStatus.FOUND)
        self.assertIn('location', headers)
        self.assertEqual(headers['location'], ['https://example.com'])