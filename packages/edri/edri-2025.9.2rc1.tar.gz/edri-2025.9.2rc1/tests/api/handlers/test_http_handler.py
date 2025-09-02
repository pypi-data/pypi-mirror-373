import unittest
from http import HTTPStatus
from http.cookies import SimpleCookie
from io import BytesIO
from os import makedirs
from unittest.mock import AsyncMock, MagicMock, patch

from edri.api import Headers
from edri.api.dataclass import File
from edri.api.handlers import HTTPHandler
from edri.config.constant import ApiType
from edri.config.setting import UPLOAD_FILES_PATH
from edri.dataclass.directive.http import CookieResponseDirective
from edri.utility import NormalizedDefaultDict


# Concrete subclass of HTTPHandler for testing
class FakeHTMLHandler(HTTPHandler):
    @classmethod
    @property
    def api_type(cls) -> ApiType:
        return ApiType.HTML


class TestHTTPHandler(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        makedirs(UPLOAD_FILES_PATH, exist_ok=True)
        # Mock dependencies
        self.mock_send = AsyncMock()
        self.mock_receive = AsyncMock()
        self.mock_scope = {'query_string': b'', 'path': '/test', 'method': 'GET'}
        self.mock_headers = NormalizedDefaultDict[str, Headers](list)

        # Use the concrete subclass for testing
        self.handler = FakeHTMLHandler(self.mock_scope, self.mock_receive, self.mock_send, self.mock_headers)

    def test_create_cookie(self):
        directive = CookieResponseDirective(
            name='test_cookie',
            value='cookie_value',
            path='/',
            expires=None,
            comment='test',
            domain='example.com',
            max_age=3600,
            secure=True,
            version=1,
            httponly=True,
            samesite='Strict'
        )
        headers = {"cookie": {}}
        created_cookie = self.handler._create_cookie(directive, headers)
        self.assertIsInstance(created_cookie, SimpleCookie)
        self.assertEqual(created_cookie['test_cookie'].value, 'cookie_value')

    def test_parse_cookies(self):
        cookies = self.handler.parse_cookies("test_cookie=test_value; another_cookie=another_value")
        self.assertIsInstance(cookies, SimpleCookie)
        self.assertEqual(cookies['test_cookie'].value, 'test_value')
        self.assertEqual(cookies['another_cookie'].value, 'another_value')

    def test_parse_url_parameters(self):
        self.handler.scope['query_string'] = b'param1=value1&param2=value2'
        parameters = self.handler.parse_url_parameters()
        self.assertEqual(parameters['param1'], 'value1')
        self.assertEqual(parameters['param2'], 'value2')

    # def test_sort_events(self):
    #     sorted_events, event_extensions, event_names = self.handler.sort_events(self.handler.api_type)
    #     self.assertIsInstance(sorted_events, dict)
    #     self.assertIsInstance(event_extensions, dict)
    #     self.assertIsInstance(event_names, dict)

    @patch('edri.api.handlers.http_handler.MultipartParser')
    def test_handle_multipart(self, mock_multipart_parser):
        mock_part = MagicMock()
        mock_part.name = "path"
        mock_part.filename = 'file.txt'
        mock_part.content_type = 'text/plain'
        mock_part.file.read.return_value = b'some content'

        mock_multipart_parser.return_value = [mock_part]

        self.handler.headers['content-type'] = ["multipart/form-data", "boundary=something"]
        self.handler.body = BytesIO()

        self.handler.handle_multipart(self.handler.body)

        self.assertIn('path', self.handler.parameters)
        self.assertIsInstance(self.handler.parameters['path'], File)

    def test_handle_json(self):
        self.handler.body = BytesIO(b'{"param1": "value1", "param2": "value2"}')
        self.handler.handle_json()
        self.assertEqual(self.handler.parameters['param1'], 'value1')
        self.assertEqual(self.handler.parameters['param2'], 'value2')

    async def test_response(self):
        status = HTTPStatus.OK
        data = b"Test response data"
        headers = NormalizedDefaultDict[str, Headers](list, {"Content-Type": ["text/plain"]})

        await self.handler.response(status, data, headers=headers)

        self.handler.send.assert_any_call({
            'type': 'http.response.start',
            'status': status,
            'headers': self.handler.get_headers_binary(headers),
        })
        self.handler.send.assert_any_call({
            'type': 'http.response.body',
            'body': data,
            'more_body': False
        })

    async def test_response_error(self):
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        response = b"Error occurred"
        await self.handler.response_error(status, response)
        self.handler.send.assert_called()

    @patch('edri.api.handlers.http_handler.Path')
    async def test_response_file(self, mock_path):
        mock_file = MagicMock()
        mock_path.return_value = mock_file
        mock_file.is_file.return_value = True
        mock_file.open.return_value = BytesIO(b"file content")

        file_path = "test_file.txt"
        success = await self.handler.response_assets(file_path)

        self.assertTrue(success)
        self.handler.send.assert_called()

    def test_convert_type(self):
        morsel = SimpleCookie("cookie_name=cookie_value")["cookie_name"]
        result = self.handler.convert_type(morsel, str)
        self.assertEqual(result, "cookie_value")